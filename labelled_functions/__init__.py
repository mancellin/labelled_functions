#!/usr/bin/env python
# coding: utf-8

from inspect import getfullargspec
from functools import wraps
from itertools import product

import numpy as np
import pandas as pd


def recording_calls(f):
    """Decorate a function to make it return a dict of its inputs and outputs.

    >>> recording_calls(round)(1.6)
    {'number': 1.6, 'round': 2}

    >>> recording_calls(pow)(2, 3)
    {'x': 2, 'y': 3, 'pow': 8}

    The keys of the dict are optained by introspection: they are here the name of the input variable in the code and the name of the function itself.

    Positional and keyword arguments are supported, but nor *args, **kwargs, nor keyword-only arguments (TODO).

    If the function return a tuple or a list, it is expanded in the dict:

    >>> def cube(x):
            return (12*x, 6*x**2, x**3)
    >>> recording_calls(cube)(5)
    {'x': 5, 'cube[0]': 60, 'cube[1]': 150, 'cube[2]': 125}

    There are several ways to change the keys of the output, such as annotations:

    >>> def cube(x) -> ('length', 'area', 'volume'):
            return (12*x, 6*x**2, x**3)
    >>> recording_calls(cube)(5)
    {'x': 5, 'length': 60, 'area': 150, 'volume': 125}
    """
    f_spec = getfullargspec(f)
    input_names = f_spec.args

    if 'return' in f_spec.annotations:
        if isinstance(f_spec.annotations['return'], tuple) or isinstance(f_spec.annotations['return'], list):
            output_names = list(f_spec.annotations['return'])
        else:
            output_names = [f_spec.annotations['return']]
    else:
        output_names = []

    @wraps(f)
    def recorded_f(*args, **kwargs):
        nonlocal input_names, output_names

        record = {name: value for name, value in zip(input_names, args)}
        record = {**record, **kwargs}

        result = f(*args, **kwargs)

        if (isinstance(result, tuple) or isinstance(result, list)) and len(result) > 1:
            for i, res in enumerate(result):
                if len(output_names) <= i:
                    output_names.append(f.__name__ + "[{}]".format(i))
                record[output_names[i]] = res
        # TODO: Support namedtuple and dicts
        else:
            if len(output_names) == 0:
                output_names.append(f.__name__)
            record[output_names[0]] = result

        return record

    return recorded_f


def recording_map(f, *args):
    return map(recording_calls(f), *args)


def pandas_map(f, *args):
    input_names = getfullargspec(f).args
    return pd.DataFrame(list(recording_map(f, *args))).set_index(input_names)

def full_parametric_study(f, *args_range):
    return pandas_map(f, *zip(*product(*args_range)))


