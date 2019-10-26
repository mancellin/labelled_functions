#!/usr/bin/env python
# coding: utf-8

from typing import Dict, List
from inspect import Parameter, Signature, getsource
from functools import wraps

import parso

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

            else:
                try:
                    source = getsource(self.function)
                    self.output_names = _get_output_names_from_source(source)
                except ValueError:
                    pass


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
        if result is None:
            return {}
        elif isinstance(result, dict):
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


# HELPER FUNCTIONS

def _is_tuple_or_list(a):
    return isinstance(a, tuple) or isinstance(a, list)

def _get_output_names_from_source(source: str) -> List[str]:
    content = parso.parse(source)
    return_stmt = _find_return_in_tree(content)
    if return_stmt is None:
        return []  # The function has no return statement.
    names = _parse_returned_expression(return_stmt.children[-1])
    if names is not None:
        # Strip space and newlines (when using \ at the end of the line)
        return [n.strip(' \\\n') for n in names]
    else:
        raise ValueError("A return statement has been found, "
                         "but it is not a simple expression or a typle")

def _find_return_in_tree(tree):
    # Recursively go through the syntax tree to find a return statement.
    if tree.type == "return_stmt":
        # Found!
        return tree
    elif hasattr(tree, 'children'):
        # Go through the children, starting with the end.
        for s in reversed(tree.children):
            found = _find_return_in_tree(s)
            if found is not None:
                return found

def _parse_returned_expression(tree):
    # Look for a single expression, or a tuple of expressions.
    if tree.type in {"name", "term", "arith_expr", "atom_expr"}:
        return [tree.get_code()]
    elif tree.type == "testlist":
        return [o.get_code() for o in tree.children if not o.type == "operator"]
    elif tree.type == "atom" and "(" in tree.children[0].get_code():
        return _parse_returned_expression(tree.children[1])

