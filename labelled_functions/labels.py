#!/usr/bin/env python
# coding: utf-8

from typing import Dict
from inspect import Parameter, Signature
from functools import wraps

Unknown = None

class LabelledFunction:
    """A class wrapping a function and storing names for its inputs and outputs.

    Parameters
    ----------
    f: Function
        A Python function.

    Attributes
    ----------
    name: str
        The name of the function.
    input_names: List[str]
        The names of the inputs.
    output_names: List[str]
        The names of the outputs.
    default_values: Dict[str, Any]
        The default values of the optional inputs.

    Function are assumed to always return the same type of output, in
    particular, the same number of output variables.

    Positional-only arguments are not supported (since their name is irrelevant,
    they are not suited for labelled functions).
    
    The constructor `LabelledFunction` is idempotent:
    >>> lf = LabelledFunction(f)
    >>> llf = LabelledFunction(lf)
    >>> lf is llf
    True

    """

    def __new__(cls, f):
        if isinstance(f, LabelledFunction):
            return f  # No need to create a new object, the function has already been labelled.
        else:
            return super().__new__(cls)

    def __init__(self, f):
        if isinstance(f, LabelledFunction):
            pass  # Do not rerun __init__ when idempotent call.
        else:
            self.function = f
            self.name = f.__name__
            self.signature = Signature.from_callable(f)

            # INPUT
            self.input_names = [name for name in self.signature.parameters]
            self.default_values = {name: self.signature.parameters[name].default for name in self.signature.parameters if self.signature.parameters[name].default is not Parameter.empty}

            # OUTPUT
            self.output_names = Unknown  # For now...
            if self.signature.return_annotation is not Signature.empty:
                if _is_tuple_or_list(self.signature.return_annotation):
                    self.output_names = list(self.signature.return_annotation)
                else:
                    self.output_names = [self.signature.return_annotation]

    def __str__(self):
        input_str = ", ".join(self.input_names) if len(self.input_names) > 0 else ""
        output_str = ", ".join(self.output_names) if len(self.output_names) > 0 else ""
        return f"{self.name}({input_str}) -> ({output_str})"

    def __getattr__(self, name):
        try:
            return getattr(self.function, name)
        except AttributeError:
            raise AttributeError(f"{self.__class__} does not have a attribute named {name}.")

    def __call__(self, *args, **kwargs):
        result = self.function(*args, **kwargs)

        if self.output_names is Unknown:
            if _is_tuple_or_list(result) and len(result) > 1:
                self.output_names = [f"{self.name}[{i}]" for i in range(len(result))]
            elif isinstance(result, dict):
                self.output_names = list(result.keys())
            # TODO: Handle named tuples
            else:
                self.output_names = [self.name]
        return result

    def _output_as_dict(self, result):
        if isinstance(result, dict):
            return result
        elif len(self.output_names) == 1:
            return {self.output_names[0]: result}
        else:
            return {name: val for name, val in zip(self.output_names, result)}

    def recorded_call(self, *args, **kwargs):
        """Call the function and return a dict with its inputs and outputs.

        Examples
        --------
        >>> LabelledFunction(round).recorded_call(1.6)
        {'number': 1.6, 'round': 2}

        >>> LabelledFunction(pow).recorded_call(2, 3)
        {'x': 2, 'y': 3, 'pow': 8}

        >>> def cube(x):
                return (12*x, 6*x**2, x**3)
        >>> LabelledFunction(cube).recorded_call(5)
        {'x': 5, 'cube[0]': 60, 'cube[1]': 150, 'cube[2]': 125}

        >>> def cube(x) -> ('length', 'area', 'volume'):
                return (12*x, 6*x**2, x**3)
        >>> LabelledFunction(cube).recorded_call(5)
        {'x': 5, 'length': 60, 'area': 150, 'volume': 125}
        """
        inputs = {**self.default_values, **{name: val for name, val in zip(self.input_names, args)}, **kwargs}
        outputs = self._output_as_dict(self.__call__(*args, **kwargs))
        return {**inputs, **outputs}

    def apply_in_namespace(self, namespace: Dict) -> Dict:
        """Call the functions using the relevant variables in the namespace as
        inputs and adding the outputs to the namespace (in-place).

        Examples
        --------
        >>> LabelledFunction(round).apply_in_namespace({'number': 4.2, 'other': 'a'})
        {'number': 4.2, 'other': 'a', 'round': 4}
        """
        inputs = {name: val for name, val in namespace.items() if name in self.input_names}
        outputs = self._output_as_dict(self.__call__(**inputs))
        namespace.update(outputs)
        return namespace


def recorded_call(f, *args, **kwargs):
    return LabelledFunction(f).recorded_call(*args, **kwargs)


def _is_tuple_or_list(a):
    return isinstance(a, tuple) or isinstance(a, list)

