#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd

from .labels import LabelledFunction

def recorded_map(f, *args):
    return map(LabelledFunction(f).recorded_call, *args)

def pandas_map(f, *args):
    f = LabelledFunction(f)
    if len(args) == 1 and isinstance(args[0], pd.DataFrame):
        return pandas_map(f, *[args[0][name] for name in f.input_names])
    else:
        return pd.DataFrame(list(recorded_map(f, *args))).set_index(f.input_names)

