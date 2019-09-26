#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd

from .labels import LabelledFunction

def recorded_map(f, *args):
    return map(LabelledFunction(f).recorded_call, *args)

def pandas_map(f, *args):
    f = LabelledFunction(f)
    return pd.DataFrame(list(recorded_map(f, *args))).set_index(f.input_names)

