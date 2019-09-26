#!/usr/bin/env python
# coding: utf-8

from hypothesis import given, settings
from hypothesis.strategies import floats

import numpy as np
import pandas as pd

from labelled_functions.parametric import *

from example_functions import *

number = floats(allow_nan=False, allow_infinity=False)

def test_recorded_map():
    assert list(recorded_map(double, [1])) == [{'x': 1, 'double': 2}]

@given(number, number, number, number)
@settings(max_examples=10)
def test_pandas_map(a, b, c, d):
    assert np.all(
        pandas_map(double, [a, b])
        == pd.DataFrame(data={'x': [a, b], 'double': [2*a, 2*b]}).set_index('x')
    )
    assert np.all(
        pandas_map(sum, [a, b], [c, d])
        == pd.DataFrame(data={'x': [a, b],
                              'y': [c, d],
                              'sum': [a+c, b+d],
                              }
                        ).set_index(['x', 'y'])
    )
    assert np.all(
        pandas_map(annotated_cube, [a, b])
        == pd.DataFrame(data={'x': [a, b],
                              'width': [a, b],
                              'height': [a, b],
                              'depth': [a, b],
                              }
                        ).set_index('x')
    )

@given(number, number, number, number)
@settings(max_examples=10)
def test_full_parametric_study(a, b, c, d):
    assert np.all(
        full_parametric_study(double, [a, b])
        == pandas_map(double, [a, b])
    )
    assert np.all(
        full_parametric_study(sum, [a, b], [c, d])
        == pd.DataFrame(data={'x': [a, a, b, b],
                              'y': [c, d, c, d],
                              'sum': [a+c, a+d, b+c, b+d],
                              }
                        ).set_index(['x', 'y'])
    )

