#!/usr/bin/env python
# coding: utf-8

from hypothesis import given, settings
from hypothesis.strategies import floats

import numpy as np
import pandas as pd

from labelled_functions.cartesian_products import *

from example_functions import *

number = floats(allow_nan=False, allow_infinity=False)

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

