#!/usr/bin/env python
# coding: utf-8
"""Some higher-order functions that make useful tools."""

from labelled_functions.labels import label


# API

def pass_inputs(func):
    func = label(func)

    def func_passing_inputs(*args, **kwargs):
        inputs = {**func.default_values, **{name: val for name, val in zip(func.input_names, args)}, **kwargs}
        inputs = {name: inputs[name] for name in inputs if name not in func.hidden_inputs}  # Drop hidden inputs
        outputs = func._output_as_dict(func.__call__(*args, **kwargs))
        return {**inputs, **outputs}

    func_passing_inputs = label(
        func_passing_inputs,
        name=f"{func.name}",
        _input_names=func._input_names,
        output_names=func._input_names + func.output_names,
        default_values=func.default_values,
        hidden_inputs=func.hidden_inputs,
    )

    return func_passing_inputs

def time(func):
    func = label(func)

    def timed_func(*args, **kwargs):
        from time import perf_counter
        start = perf_counter()
        result = func._output_as_dict(func(*args, **kwargs))
        end = perf_counter()
        result[f"{func.name}_execution_time"] = end - start
        return result

    timed_func = label(
        timed_func,
        name=f"time({func.name})",
        _input_names=func._input_names,
        output_names=func.output_names + [f"{func.name}_execution_time"],
        default_values=func.default_values,
        hidden_inputs=func.hidden_inputs,
    )

    return timed_func
