#!/usr/bin/env python
# coding: utf-8
"""Some higher-order functions that make useful tools."""

from labelled_functions.abstract import Unknown
from labelled_functions.labels import label, LabelledFunction
from copy import copy


# API

def keeping_inputs(func):
    func = label(func)

    def func_returning_inputs(*args, **kwargs):
        inputs = {**func.default_values, **{name: val for name, val in zip(func.input_names, args)}, **kwargs}
        outputs = func._output_as_dict(func.__call__(*args, **kwargs))
        return {**inputs, **outputs}

    func_returning_inputs = LabelledFunction(
        func_returning_inputs,
        name=f"{func.name}",
        input_names=func.input_names,
        output_names=func.input_names + func.output_names if func.output_names is not Unknown else Unknown,
        default_values=func.default_values,
    )

    return func_returning_inputs


def time(func):
    func = label(func)

    def timed_func(*args, **kwargs):
        from time import perf_counter
        start = perf_counter()
        result = func._output_as_dict(func(*args, **kwargs))
        end = perf_counter()
        result[f"{func.name}_execution_time"] = end - start
        return result

    timed_func = LabelledFunction(
        timed_func,
        name=f"time({func.name})",
        input_names=func.input_names,
        output_names=func.output_names + [f"{func.name}_execution_time"],
        default_values=func.default_values,
    )

    return timed_func


def decorate(func, decorator):
    new_func = copy(func)
    new_func.function = decorator(func.function)
    return new_func


def cache(func, memory=None):
    if memory is None:
        from joblib import Memory
        memory = Memory("/tmp", verbose=0)
    return decorate(func, memory.cache)

