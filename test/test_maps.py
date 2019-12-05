#!/usr/bin/env python
# coding: utf-8

import pytest

from hypothesis import given, settings
from hypothesis.strategies import floats
from hypothesis.extra.numpy import arrays

import numpy as np
import pandas as pd
import xarray as xr

from labelled_functions import label
from labelled_functions.maps import *

from example_functions import *

def test_map_with_several_kind_of_inputs():
    length = np.random.rand(5)
    radius = np.random.rand(5)

    df = pd.DataFrame(data={'radius': radius, 'length': length})
    ds = xr.Dataset(coords={'radius': radius, 'length': length})
    assert (
           list(pandas_map(cylinder_volume, radius, length))
        == list(pandas_map(cylinder_volume, length=length, radius=radius))
        == list(pandas_map(cylinder_volume, df))
        == list(pandas_map(cylinder_volume, ds))
    )


def test_recorded_map():
    assert list(lmap(pass_inputs(double), x=[1])) == [{'x': 1, '2*x': 2}]
    assert list(lmap(pass_inputs(optional_add), y=[1])) == [{'x': 0, 'y': 1, 'x+y': 1}]

    # TODO?
    # with pytest.raises(TypeError):
    #     recorded_map(all_kinds_of_args, [0], [1], [2], [3])

    assert list(lmap(pass_inputs(all_kinds_of_args), x=[0], y=[1], z=[2], t=[3])) == [{'x': 0, 'y': 1, 'z': 2, 't': 3}]
    assert list(lmap(pass_inputs(all_kinds_of_args), x=[0], z=[2], t=[3]))        == [{'x': 0, 'y': 1, 'z': 2, 't': 3}]
    assert list(lmap(pass_inputs(all_kinds_of_args), x=[0], z=[2]))               == [{'x': 0, 'y': 1, 'z': 2, 't': 3}]
    assert list(lmap(pass_inputs(all_kinds_of_args), z=[2], t=[3], x=[0]))        == [{'x': 0, 'y': 1, 'z': 2, 't': 3}]


def test_pandas_map():
    a, b = np.random.rand(5), np.random.rand(5)

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
        pandas_map(cube, a)
        == pd.DataFrame(data={'x': a,
                              'length': 12*a,
                              'area': 6*a**2,
                              'volume': a**3,
                              }
                        ).set_index('x')
    )
    assert np.all(
        pandas_map(label(cube).hide('x'), a)
        == pd.DataFrame(data={'length': 12*a,
                              'area': 6*a**2,
                              'volume': a**3,
                              }
                        )
    )


def test_pandas_map_on_df():
    x, y = np.random.rand(5), np.random.rand(5)

    df = pd.DataFrame(data={'x': x, 'y': y})
    assert np.all(
        pandas_map(add, df).reset_index()
        == pd.DataFrame(data={'x': x, 'y': y, 'x+y': x+y})
    )


def test_full_parametric_study():
    a = np.linspace(1, 10, 10)
    b = np.linspace(1, 10, 5)

    assert np.all(
        full_parametric_study(double, a)
        == pandas_map(double, a)
    )

    A = full_parametric_study(add, a, b).to_xarray()
    assert A == xr.Dataset(
        {'x+y': (('x', 'y'), a[:, None] + b)},
        coords={'x': a,
                'y': b}
    )
    assert A == full_parametric_study(add, A).to_xarray()

