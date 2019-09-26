#!/usr/bin/env python
# coding: utf-8

from inspect import getfullargspec
from functools import wraps

Unknown = None

def is_tuple_or_list(a):
    return isinstance(a, tuple) or isinstance(a, list)


def extend_dict(d, keys, values):
    for key, value in zip(keys, values):
        d[key] = value
    return d


class LabelledFunction:
    """Function are assumed to return always the same type of output...
    
    TODO: Support keyword-only arguments."""

    def __new__(cls, f):
        if isinstance(f, LabelledFunction):
            return f  # No need to label it more...
        else:
            return super().__new__(cls)

    def __init__(self, f):
        self.function = f

        self._spec = getfullargspec(f)

        self.name = f.__name__
        self.input_names = self._spec.args
        self.output_names = Unknown  # For now...

        self._parse_annotations()

    def _parse_annotations(self):
        if 'return' in self._spec.annotations:
            if is_tuple_or_list(self._spec.annotations['return']):
                self.output_names = list(self._spec.annotations['return'])
            else:
                self.output_names = [self._spec.annotations['return']]
        # TODO: Read input annotations?

    def __getattr__(self, name):
        try:
            return getattr(self.function, name)
        except AttributeError:
            raise AttributeError(f"{self.__class__} does not have a attribute named {name}.")

    def __call__(self, *args, **kwargs):
        result = self.function(*args, **kwargs)
        if self.output_names is Unknown:
            if is_tuple_or_list(result) and len(result) > 1:
                self.output_names = [f"{self.name}[{i}]" for i in range(len(result))]
            # TODO: Handle dictionnaries and named tuples
            else:
                self.output_names = [self.name]
        return result

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
        record = {}
        extend_dict(record, self.input_names, args)
        extend_dict(record, kwargs.keys(), kwargs.values())

        result = self.__call__(*args, **kwargs)

        if len(self.output_names) == 1:
            extend_dict(record, self.output_names, [result])
        else:
            extend_dict(record, self.output_names, result)

        return record

def recorded_call(f, *args, **kwargs):
    return LabelledFunction(f).recorded_call(*args, **kwargs)
