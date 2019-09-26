#!/usr/bin/env python
# coding: utf-8

from itertools import product

import numpy as np
import pandas as pd

from .labels import recording_calls

def recorded_map(f, *args):
    return map(LabelledFunction(f).recorded_call, *args)

def pandas_map(f, *args):
    input_names = getfullargspec(f).args
    return pd.DataFrame(list(recording_map(f, *args))).set_index(input_names)

def full_parametric_study(f, *args_range):
    return pandas_map(f, *zip(*product(*args_range)))

