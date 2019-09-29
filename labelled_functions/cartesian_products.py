#!/usr/bin/env python
# coding: utf-8

from itertools import product

from .labels import LabelledFunction
from .maps import parse_map_input, pandas_map

def full_parametric_study(f, *args, **kwargs):
    f = LabelledFunction(f)
    return pandas_map(f, *zip(*product(*parse_map_input(f.input_names, *args, **kwargs))))

