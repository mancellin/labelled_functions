#!/usr/bin/env python
# coding: utf-8

from itertools import product

from .maps import pandas_map

def full_parametric_study(f, *args_range):
    return pandas_map(f, *zip(*product(*args_range)))

