#!/usr/bin/env python
# coding: utf-8

from itertools import product

import numpy as np
import pandas as pd
import xarray as xr

from .labels import label
from .decorators import keeping_inputs


# API

def pandas_map(f, *args, **kwargs):
    f = label(f)
    dict_of_lists = _preprocess_map_inputs(f.input_names, args, kwargs)
    data = pd.DataFrame(list(lmap(keeping_inputs(f), **dict_of_lists)))
    return _set_index(f, data)


def pandas_cartesian_product(f, *args, **kwargs):
    f = label(f)
    dict_of_lists = _preprocess_map_inputs(f.input_names, args, kwargs)
    data = pd.DataFrame(list(lcartesianmap(keeping_inputs(f), **dict_of_lists)))
    return _set_index(f, data)


full_parametric_study = pandas_cartesian_product


# TOOLS

def lstarmap(f, list_of_kwargs):
    """Similar to itertools.starmap but for keyword arguments."""
    for it_kw in list_of_kwargs:
        yield f(**it_kw)


def lzip(**dict_of_lists):
    """
    >>> lzip({'a': [1, 2, 3], 'b':[3, 4, 5]})
    [{'a': 1, 'b': 3}, {'a': 2, 'b': 4}, {'a': 3, 'b': 5}]
    """
    for vals in zip(*dict_of_lists.values()):
        yield {key: val for key, val in zip(dict_of_lists.keys(), vals)}


def lmap(f, **dict_of_lists):
    """Similar to built-in map but for keyword arguments."""
    list_of_dicts = lzip(**dict_of_lists)
    yield from lstarmap(f, list_of_dicts)


def lproduct(**dict_of_lists):
    """Similar to itertools.product but for keyword arguments."""
    for vals in product(*dict_of_lists.values()):
        yield {key: val for key, val in zip(dict_of_lists.keys(), vals)}


def lcartesianmap(f, **dict_of_lists):
    list_of_dicts = lproduct(**dict_of_lists)
    yield from lstarmap(f, list_of_dicts)


def _preprocess_map_inputs(input_names, args, kwargs) -> dict:
    """When a dataframe or a dataset is passed, transfrom it into a dict of vectors"""
    if len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], pd.DataFrame):
        df = args[0]
        return {name: df[name] for name in input_names if name in df.columns}
    elif len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], xr.Dataset):
        ds = args[0]
        return {name: ds[name].data for name in input_names if name in ds.variables}
    else:
        return {**{name: val for name, val in zip(input_names, args)}, **kwargs}


def _set_index(f, data):
    indices = [name for name in f.input_names if name not in f.hidden_inputs]
    if len(indices) > 0:
        return data.set_index(indices)
    else:
        return data
