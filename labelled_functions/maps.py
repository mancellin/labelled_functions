#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import xarray as xr

from .labels import LabelledFunction

# API

def lmap(f, *args, **kwargs):
    f = LabelledFunction(f)
    dict_of_lists = identify_passed_ranges(f.input_names, args, kwargs)
    for it_kw in lzip_with_default_values(dict_of_lists, defaults=f.default_values):
        yield f(**it_kw)

def recorded_map(f, *args, **kwargs):
    f = LabelledFunction(f)
    dict_of_lists = identify_passed_ranges(f.input_names, args, kwargs)
    for it_kw in lzip_with_default_values(dict_of_lists, defaults=f.default_values):
        yield f.recorded_call(**it_kw)

def pandas_map(f, *args, **kwargs):
    f = LabelledFunction(f)
    data = pd.DataFrame(list(recorded_map(f, *args, **kwargs)))
    indices = [name for name in f.input_names if name not in f.hidden_inputs]
    if len(indices) > 0:
        return data.set_index(indices)
    else:
        return data

# Tools

def identify_passed_ranges(input_names, args, kwargs) -> dict:
    """When a dataframe or a dataset is passed, transfrom it into a dict of vectors"""
    if len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], pd.DataFrame):
        df = args[0]
        return {name: df[name] for name in input_names if name in df.columns}
    elif len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], xr.Dataset):
        ds = args[0]
        return {name: ds[name].data for name in input_names if name in ds.variables}
    else:
        return {**{name: val for name, val in zip(input_names, args)}, **kwargs}

def lzip(d):
    """
    >>> lzip({'a': [1, 2, 3], 'b':[3, 4, 5]})
    [{'a': 1, 'b': 3}, {'a': 2, 'b': 4}, {'a': 3, 'b': 5}]
    """
    for vals in zip(*d.values()):
        yield {key: val for key, val in zip(d.keys(), vals)}

def lzip_with_default_values(d, defaults):
    """
    >>> lzip({'a': [1, 2, 3], 'b':[3, 4, 5]}, defaults={'c': 1})
    [{'a': 1, 'b': 3, 'c': 1}, {'a': 2, 'b': 4, 'c': 1}, {'a': 3, 'b': 5, 'c': 1}]
    """
    for z in lzip(d):
        z = {**defaults, **z}
        yield z


