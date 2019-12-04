#!/usr/bin/env python
# coding: utf-8
"""Some higher-order functions that make useful tools."""

from labelled_functions.labels import label


# API

def time(func):
    func = label(func)

    def timed_func(*args, **kwargs):
        from time import perf_counter
        start = perf_counter()
        result = func._output_as_dict(func(*args, **kwargs))
        end = perf_counter()
        result[f"{func.name}_execution_time"] = end - start
        return result

    timed_f = label(
        timed_func,
        name=f"time({func.name})",
        _input_names=func._input_names,
        output_names=func.output_names + [f"{func.name}_execution_time"],
        default_values=func.default_values,
        hidden_inputs=func.hidden_inputs,
    )

    return timed_f
