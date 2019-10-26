#!/usr/bin/env python
# coding: utf-8

import pytest

from hypothesis import given, settings
from hypothesis.strategies import floats
from hypothesis.extra.numpy import arrays

import numpy as np
import pandas as pd
import xarray as xr

from labelled_functions.maps import *

from example_functions import *

number = floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
array = arrays(dtype=np.float64, shape=(10,), elements=number)

@given(array, array)
@settings(max_examples=5)
def test_map_with_several_kind_of_inputs(length, radius):
    df = pd.DataFrame(data={'radius': radius, 'length': length})
    ds = xr.Dataset(coords={'radius': radius, 'length': length})
    assert (
        list(map(cylinder_volume, radius, length))
        == list(lmap(cylinder_volume, radius, length))
        == list(lmap(cylinder_volume, length=length, radius=radius))
        == list(lmap(cylinder_volume, df))
        == list(lmap(cylinder_volume, ds))
    )


def test_recorded_map():
    assert list(recorded_map(double, [1])) == [{'x': 1, '2*x': 2}]
    assert list(recorded_map(optional_add, y=[1])) == [{'x': 0, 'y': 1, 'x+y': 1}]

    # TODO?
    # with pytest.raises(TypeError):
    #     recorded_map(all_kinds_of_args, [0], [1], [2], [3])

    assert list(recorded_map(all_kinds_of_args, [0], [1], z=[2], t=[3]))     == [{'x': 0, 'y': 1, 'z': 2, 't': 3}]
    assert list(recorded_map(all_kinds_of_args, x=[0], y=[1], z=[2], t=[3])) == [{'x': 0, 'y': 1, 'z': 2, 't': 3}]
    assert list(recorded_map(all_kinds_of_args, x=[0], z=[2], t=[3]))        == [{'x': 0, 'y': 1, 'z': 2, 't': 3}]
    assert list(recorded_map(all_kinds_of_args, x=[0], z=[2]))               == [{'x': 0, 'y': 1, 'z': 2, 't': 3}]
    assert list(recorded_map(all_kinds_of_args, z=[2], t=[3], x=[0]))        == [{'x': 0, 'y': 1, 'z': 2, 't': 3}]


@given(array, array)
@settings(max_examples=5)
def test_pandas_map(a, b):
    assert np.all(
        pandas_map(double, a)
        == pd.DataFrame(data={'x': a, '2*x': 2*a}).set_index('x')
    )
    assert np.all(
        pandas_map(add, a, b)
        == pd.DataFrame(data={'x': a,
                              'y': b,
                              'x+y': a+b,
                              }
                        ).set_index(['x', 'y'])
    )
    assert np.all(
        pandas_map(annotated_cube, a)
        == pd.DataFrame(data={'x': a,
                              'length': 12*a,
                              'area': 6*a**2,
                              'volume': a**3,
                              }
                        ).set_index('x')
    )


@given(array, array)
@settings(max_examples=5)
def test_pandas_map_on_df(x, y):
    df = pd.DataFrame(data={'x': x, 'y': y})
    assert np.all(
        pandas_map(add, df).reset_index()
        == pd.DataFrame(data={'x': x, 'y': y, 'x+y': x+y})
    )

