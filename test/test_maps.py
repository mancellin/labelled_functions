#!/usr/bin/env python
# coding: utf-8

from hypothesis import given, settings
from hypothesis.strategies import floats

import numpy as np
import pandas as pd

from labelled_functions.maps import *

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
                              'length': [12*a, 12*b],
                              'area': [6*a**2, 6*b**2],
                              'volume': [a**3, b**3],
                              }
                        ).set_index('x')
    )

