#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd

from .labels import LabelledFunction

def parse_input(input_names, *args, **kwargs):
    if len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], pd.DataFrame):
        return [args[0][name] for name in input_names]
    else:
        return args + tuple(kwargs[name] for name in input_names[len(args):])

def lmap(f, *args, **kwargs):
    f = LabelledFunction(f)
    return map(f, *parse_input(f.input_names, *args, **kwargs))

def recorded_map(f, *args, **kwargs):
    f = LabelledFunction(f)
    return map(f.recorded_call, *parse_input(f.input_names, *args, **kwargs))

def pandas_map(f, *args, **kwargs):
    f = LabelledFunction(f)
    return pd.DataFrame(list(recorded_map(f, *args, **kwargs))).set_index(f.input_names)

