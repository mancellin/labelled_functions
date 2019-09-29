#!/usr/bin/env python
# coding: utf-8

from itertools import product

import pandas as pd

from .labels import LabelledFunction
from .maps import identify_passed_ranges

def recorded_cartesian_product(f, *args, **kwargs):
    f = LabelledFunction(f)
    dict_of_lists = identify_passed_ranges(f.input_names, args, kwargs)
    for it_kw in lproduct_with_default_values(dict_of_lists, defaults=f.default_values):
        yield f.recorded_call(**it_kw)

def pandas_cartesian_product(f, *args, **kwargs):
    f = LabelledFunction(f)
    return pd.DataFrame(list(recorded_cartesian_product(f, *args, **kwargs))).set_index(f.input_names)

full_parametric_study = pandas_cartesian_product

# Tools

def lproduct(d):
    for vals in product(*d.values()):
        yield {key: val for key, val in zip(d.keys(), vals)}

def lproduct_with_default_values(d, defaults):
    for z in lproduct(d):
        z = {**defaults, **z}
        yield z
