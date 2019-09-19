from parametric import pandify, parametric_study

import numpy as np
import pandas as pd

def test_parametric_study():
    # Zero arguments, one result
    def f():
        return 42
    f_data = parametric_study(f)()
    assert isinstance(f_data, pd.DataFrame)
    assert set(f_data.columns) == {'f'}
    assert list(f_data['f']) == [42]

    # One positional argument, one result
    def g(x):
        return 2*x
    g_data = parametric_study(g)([1, 2]).reset_index()
    assert set(g_data.columns) == {'x', 'g'}
    assert list(g_data['x']) == [1, 2]
    assert list(g_data['g']) == [2, 4]

    # Two positional arguments, one result
    def h(x, y):
        return 2*x
    h_data = parametric_study(h)([1, 2], [10, 11]).reset_index()
    assert set(h_data.columns) == {'x', 'y', 'h'}

    # One positional argument, two results
    def ff(a):
        return a, 2*a
    ff_data = parametric_study(ff)([1, 2]).reset_index()
    assert set(ff_data.columns) == {'a', 'ff[0]', 'ff[1]'}

    # One positional argument, various number of results
    def fg(a):
        if a % 2 == 0:
            return a/2
        else:
            return a, a
    fg_data = parametric_study(fg)([1, 2]).reset_index()
    assert set(fg_data.columns) == {'a', 'fg[0]', 'fg[1]'}
    assert np.isnan(fg_data['fg[1]'][1])

    # One positional argument, two named results
    def ff(a) -> ('x', 'y'):
        return 3*a, 4*a
    ff_data = parametric_study(ff)([1, 2]).reset_index()
    assert set(ff_data.columns) == {'a', 'x', 'y'}

