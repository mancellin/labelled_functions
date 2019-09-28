#!/usr/bin/env python
# coding: utf-8

from hypothesis import given, settings
from hypothesis.strategies import floats
from hypothesis.extra.numpy import arrays

import numpy as np
import pandas as pd
import xarray as xr

from labelled_functions.cartesian_products import *

from example_functions import *


def test_full_parametric_study():
    a = np.linspace(1, 10, 10)
    b = np.linspace(1, 10, 5)

    assert np.all(
        full_parametric_study(double, a)
        == pandas_map(double, a)
    )

    assert full_parametric_study(sum, a, b).to_xarray() == xr.Dataset(
        {'sum': (('x', 'y'), a[:, None] + b)},
        coords={'x': a,
                'y': b}
    )

