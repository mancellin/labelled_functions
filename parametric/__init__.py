#!/usr/bin/env python
# coding: utf-8

from inspect import getfullargspec
from functools import wraps
from itertools import product

import numpy as np
import pandas as pd

from tqdm import tqdm


def pandify(f):
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

    f_spec = getfullargspec(f)
    # f_spec is of the form:
    # FullArgSpec(args=['a'], varargs='args', varkw='kwargs', defaults=None,
    #             kwonlyargs=['b'], kwonlydefaults={'b': 1}, annotations={})

    input_names = f_spec.args

    if 'return' in f_spec.annotations:
        output_names = list(f_spec.annotations['return'])
        nb_outputs = len(output_names)
    else:
        output_names = []
        nb_outputs = 1

    @wraps(f)
    def pandified_f(list_of_params):
        nonlocal output_names, nb_outputs

        data = []
        for params in list_of_params:
            result = f(*params)

            if isinstance(result, tuple):
                nb_outputs = max(nb_outputs, len(result))
                data.append(tuple(params) + result)

            else:
                data.append(params + (result,))

        if len(output_names) == 0:
            if nb_outputs == 1:
                output_names = [f.__name__]
            else:
                output_names = [f.__name__ + "[{}]".format(i) for i in range(nb_outputs)]

        df = pd.DataFrame(data, columns=input_names + output_names)
        if len(input_names) > 0:
            df = df.set_index(input_names)

        return df

    return pandified_f


def parametric_study(f, progressbar=True):
    """
    """
    pandified_f = pandify(f)

    @wraps(f)
    def vectorized_f(*args_range):
        nonlocal progressbar
        if not progressbar:
            return pandified_f(product(*args_range))
        else:
            return pandified_f(tqdm(list(product(*args_range))))

    return vectorized_f

