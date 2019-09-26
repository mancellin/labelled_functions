
from collections import namedtuple

import pytest
# TODO: use Hypothesis
import numpy as np
import pandas as pd

from labelled_functions import *

from example_functions import *

def cube(x):
    return (x, x, x)

def annotated_cube(x) -> ('width', 'height', 'depth'):
    return (x, x, x)

def test_recorder():
    assert recording_calls(pi)() == {'pi': 3.14159}

    assert recording_calls(deep_thought)() == {'The Answer': 42}

    assert recording_calls(double)(4) == {'x': 4, 'double': 8}

    assert recording_calls(optional_double)(4) == {'x': 4, 'optional_double': 8}
    assert recording_calls(optional_double)(x=6) == {'x': 6, 'optional_double': 12}
    assert recording_calls(optional_double)() == {'optional_double': 0}

    assert recording_calls(sum)(4, 5) == {'x': 4, 'y': 5, 'sum': 9}

    assert recording_calls(optional_sum)(4, 5) == {'x': 4, 'y': 5, 'optional_sum': 9}
    assert recording_calls(optional_sum)(4) == {'x': 4, 'optional_sum': 4}
    assert recording_calls(optional_sum)() == {'optional_sum': 0}
    assert recording_calls(optional_sum)(x=4, y=5) == {'x': 4, 'y': 5, 'optional_sum': 9}
    assert recording_calls(optional_sum)(y=4, x=5) == {'y': 4, 'x': 5, 'optional_sum': 9}
    assert recording_calls(optional_sum)(y=4) == {'y': 4, 'optional_sum': 4}

    assert recording_calls(cube)(4) == {'x': 4, 'cube[0]': 4, 'cube[1]': 4, 'cube[2]': 4}

    assert recording_calls(annotated_cube)(8) == {'x': 8, 'width': 8, 'height': 8, 'depth': 8}

def test_pandas_map():
    assert np.all(
        pandas_map(double, [3, 5])
        == pd.DataFrame(data={'x': [3, 5], 'double': [6, 10]}).set_index('x')
    )
    assert np.all(
        pandas_map(sum, [3, 5], [1, 0])
        == pd.DataFrame(data={'x': [3, 5],
                              'y': [1, 0],
                              'sum': [4, 5],
                              }
                        ).set_index(['x', 'y'])
    )
    assert np.all(
        pandas_map(annotated_cube, [3, 5])
        == pd.DataFrame(data={'x': [3, 5],
                              'width': [3, 5],
                              'height': [3, 5],
                              'depth': [3, 5],
                              }
                        ).set_index('x')
    )

def test_full_parametric_study():
    assert np.all(
        full_parametric_study(double, [3, 5])
        == pandas_map(double, [3, 5])
    )
    assert np.all(
        full_parametric_study(sum, [3, 5], [1, 0])
        == pd.DataFrame(data={'x': [3, 3, 5, 5],
                              'y': [1, 0, 1, 0],
                              'sum': [4, 3, 6, 5],
                              }
                        ).set_index(['x', 'y'])
    )

