#!/usr/bin/env python
# coding: utf-8

import pytest
import xarray as xr

from hypothesis import given, settings
from hypothesis.strategies import floats

from labelled_functions.labels import *

from example_functions import *

number = floats(allow_nan=False, allow_infinity=False)


def test_labelled_class():
    ldt = LabelledFunction(deep_thought)
    assert ldt() == deep_thought(), "The LabelledFunction is not callable"
    assert ldt.__code__ == deep_thought.__code__, "Attributes are not passed to encapsulated function"
    assert ldt.name == deep_thought.__name__, "Name is wrong"
    assert str(ldt) == "deep_thought() -> (The Answer)", "String representation is wrong"

    lc = LabelledFunction(cube)
    assert lc(0) == cube(0)
    assert lc.input_names == ['x']
    assert lc.output_names == ['length', 'area', 'volume']
    assert str(lc) == "cube(x) -> (length, area, volume)"


def test_idempotence():
    lc = LabelledFunction(cube)
    llc = LabelledFunction(lc)
    assert llc is lc


def test_output_checking():
    la = LabelledFunction(add)
    assert la._has_never_been_run

    la.output_names = ['moose', 'llama']
    with pytest.raises(AssertionError):
        la(1, 2)


def test_recorder():
    a, b = 1, 2

    assert recorded_call(compute_pi) == {'pi': 3.14159}
    assert recorded_call(deep_thought) == {'The Answer': 42}

    assert recorded_call(double, a) == {'x': a, '2*x': 2*a}

    assert recorded_call(optional_double, a)   == {'x': a, '2*x': 2*a}
    assert recorded_call(optional_double, x=a) == {'x': a, '2*x': 2*a}
    assert recorded_call(optional_double, )    == {'x': 0, '2*x': 0}

    assert recorded_call(add, a, b) == {'x': a, 'y': b, 'x+y': a+b}

    assert recorded_call(optional_add, a, b)     == {'x': a, 'y': b, 'x+y': a+b}
    assert recorded_call(optional_add, a)        == {'x': a, 'y': 0, 'x+y': a}
    assert recorded_call(optional_add, )         == {'x': 0, 'y': 0, 'x+y': 0}
    assert recorded_call(optional_add, x=a, y=b) == {'x': a, 'y': b, 'x+y': a+b}
    assert recorded_call(optional_add, y=a, x=b) == {'x': b, 'y': a, 'x+y': a+b}
    assert recorded_call(optional_add, y=a)      == {'x': 0, 'y': a, 'x+y': a}

    assert recorded_call(cube, a) == {'x': a, 'length': 12*a, 'area': 6*a**2, 'volume': a**3}
    assert recorded_call(annotated_cube, a) == {'x': a, 'length': 12*a, 'area': 6*a**2, 'volume': a**3}

    with pytest.raises(TypeError):
        recorded_call(all_kinds_of_args, 0, 1, 2, 3)

    assert recorded_call(all_kinds_of_args, 0, 1, z=2, t=3)     == {'x': 0, 'y': 1, 'z': 2, 't': 3}
    assert recorded_call(all_kinds_of_args, x=0, y=1, z=2, t=3) == {'x': 0, 'y': 1, 'z': 2, 't': 3}
    assert recorded_call(all_kinds_of_args, x=0, z=2, t=3)      == {'x': 0, 'y': 1, 'z': 2, 't': 3}
    assert recorded_call(all_kinds_of_args, x=0, z=2)           == {'x': 0, 'y': 1, 'z': 2, 't': 3}
    assert recorded_call(all_kinds_of_args, z=2, t=3, x=0)      == {'x': 0, 'y': 1, 'z': 2, 't': 3}


def test_namespace():
    namespace = {'x': 0, 'y': 3, 'z': 2}
    new_namespace = LabelledFunction(add).apply_in_namespace(namespace)
    assert new_namespace == {'x+y': 3, 'x': 0, 'y': 3, 'z': 2}

    in_ds = xr.Dataset(coords={'radius': np.linspace(0, 1, 10),
                               'length': np.linspace(0, 1, 10)})
    out_ds = LabelledFunction(cylinder_volume).apply_in_namespace(in_ds)
    assert 'volume' in out_ds.data_vars

