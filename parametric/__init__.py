#!/usr/bin/env python
# coding: utf-8
"""Given a function f: ℝ^n -> ℝ^m,
returns a function Iterable[ℝ^n] -> pd.DataFrame,
where each row of the DataFrame stores the inputs and outputs of one call of f.

Use introspection to read the name of the arguments of f.
TODO: Support keyword arguments.

If the function returns a tuple, the output is saved in the DataFrame as n columns 'f[0]', ... 'f[n]'.
Otherwise, a single column named 'f' is used to store the output.
Alternatively, users can define the output names using function annotations:

    def f(x, y, z) -> ("a", "b", "c"):
        ...
"""

# FullArgSpec(args=['a'], varargs='args', varkw='kwargs', defaults=None,
#             kwonlyargs=['b'], kwonlydefaults={'b': 1}, annotations={})

from inspect import getfullargspec
from functools import wraps
from itertools import product

import numpy as np
import pandas as pd

from tqdm import tqdm


def recording_calls(f):
    f_spec = getfullargspec(f)
    input_names = f_spec.args
    # TODO: keyword-only arguments

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

# TODO: PyDOE wrappers

def full_parametric_study(f, *args_range):
    return pandas_map(f, *zip(*product(*args_range)))


