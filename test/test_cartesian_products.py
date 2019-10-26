#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import xarray as xr

from labelled_functions.maps import *
from labelled_functions.cartesian_products import *

from example_functions import *


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

