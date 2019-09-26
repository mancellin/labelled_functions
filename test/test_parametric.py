#!/usr/bin/env python
# coding: utf-8

from hypothesis import given, settings
from hypothesis.strategies import floats

import numpy as np
import pandas as pd

from labelled_functions.labels import recording_calls
from labelled_functions.parametric import pandas_map, full_parametric_study

from example_functions import *

number = floats(allow_nan=False, allow_infinity=False)

@given(number, number)
@settings(max_examples=10)
def test_recorder(a, b):
    assert recording_calls(pi)() == {'pi': 3.14159}
    assert recording_calls(deep_thought)() == {'The Answer': 42}

    assert recording_calls(double)(a) == {'x': a, 'double': 2*a}

    assert recording_calls(optional_double)(a) == {'x': a, 'optional_double': 2*a}
    assert recording_calls(optional_double)(x=a) == {'x': a, 'optional_double': 2*a}
    assert recording_calls(optional_double)() == {'optional_double': 0}

    assert recording_calls(sum)(a, b) == {'x': a, 'y': b, 'sum': a+b}

    assert recording_calls(optional_sum)(a, b) == {'x': a, 'y': b, 'optional_sum': a+b}
    assert recording_calls(optional_sum)(a) == {'x': a, 'optional_sum': a}
    assert recording_calls(optional_sum)() == {'optional_sum': 0}
    assert recording_calls(optional_sum)(x=a, y=b) == {'x': a, 'y': b, 'optional_sum': a+b}
    assert recording_calls(optional_sum)(y=a, x=b) == {'y': a, 'x': b, 'optional_sum': a+b}
    assert recording_calls(optional_sum)(y=a) == {'y': a, 'optional_sum': a}

    assert recording_calls(cube)(a) == {'x': a, 'cube[0]': a, 'cube[1]': a, 'cube[2]': a}

    assert recording_calls(annotated_cube)(a) == {'x': a, 'width': a, 'height': a, 'depth': a}

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

