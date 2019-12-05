#!/usr/bin/env python
# coding: utf-8

import pytest
import xarray as xr
from copy import copy

from hypothesis import given, settings
from hypothesis.strategies import floats

from labelled_functions.labels import *

from example_functions import *

number = floats(allow_nan=False, allow_infinity=False)


def test_labelled_class():
    ldt = LabelledFunction(compute_pi)
    assert ldt() == compute_pi(), "The LabelledFunction is not callable"
    assert ldt.__wrapped__.__code__ == compute_pi.__code__, "Attributes are not passed to encapsulated function"
    assert ldt.name == compute_pi.__name__, "Name is wrong"
    assert str(ldt) == "compute_pi() -> (pi)", "String representation is wrong"

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
    with pytest.raises(TypeError):
        la(1, 2)


def test_method():
    class A:
        def __init__(self):
            self.a = 10.0

        def f(self, x):
            y = 2*x + self.a
            return y

    lab_Af = label(A().f)
    assert list(lab_Af.input_names) == ['x']
    assert list(lab_Af.output_names) == ['y']
    assert lab_Af(2) == 14
    assert lab_Af(x=2) == 14

    lab_f = label(A.f)
    assert list(lab_f.input_names) == ['self', 'x']
    assert list(lab_f.output_names) == ['y']
    assert lab_f(A(), 2) == 14
    assert lab_f(A(), x=2) == 14


def test_recorder():
    a, b = 1, 2

    assert label(compute_pi).recorded_call() == {'pi': 3.14159}

    assert label(double).recorded_call(a) == {'x': a, '2*x': 2*a}

    assert label(optional_double).recorded_call(a)   == {'x': a, '2*x': 2*a}
    assert label(optional_double).recorded_call(x=a) == {'x': a, '2*x': 2*a}
    assert label(optional_double).recorded_call()    == {'x': 0, '2*x': 0}

    assert label(add).recorded_call(a, b) == {'x': a, 'y': b, 'x+y': a+b}

    assert label(optional_add).recorded_call(a, b)     == {'x': a, 'y': b, 'x+y': a+b}
    assert label(optional_add).recorded_call(a)        == {'x': a, 'y': 0, 'x+y': a}
    assert label(optional_add).recorded_call()         == {'x': 0, 'y': 0, 'x+y': 0}
    assert label(optional_add).recorded_call(x=a, y=b) == {'x': a, 'y': b, 'x+y': a+b}
    assert label(optional_add).recorded_call(y=a, x=b) == {'x': b, 'y': a, 'x+y': a+b}
    assert label(optional_add).recorded_call(y=a)      == {'x': 0, 'y': a, 'x+y': a}

    assert label(cube).recorded_call(a) == {'x': a, 'length': 12*a, 'area': 6*a**2, 'volume': a**3}

    with pytest.raises(TypeError):
        label(all_kinds_of_args).recorded_call(0, 1, 2, 3)

    assert label(all_kinds_of_args).recorded_call(0, 1, z=2, t=3)     == {'x': 0, 'y': 1, 'z': 2, 't': 3}
    assert label(all_kinds_of_args).recorded_call(x=0, y=1, z=2, t=3) == {'x': 0, 'y': 1, 'z': 2, 't': 3}
    assert label(all_kinds_of_args).recorded_call(x=0, z=2, t=3)      == {'x': 0, 'y': 1, 'z': 2, 't': 3}
    assert label(all_kinds_of_args).recorded_call(x=0, z=2)           == {'x': 0, 'y': 1, 'z': 2, 't': 3}
    assert label(all_kinds_of_args).recorded_call(z=2, t=3, x=0)      == {'x': 0, 'y': 1, 'z': 2, 't': 3}


def test_namespace():
    namespace = {'x': 0, 'y': 3, 'z': 2}
    new_namespace = LabelledFunction(add).apply_in_namespace(namespace)
    assert new_namespace == {'x+y': 3, 'x': 0, 'y': 3, 'z': 2}

    in_ds = xr.Dataset(coords={'radius': np.linspace(0, 1, 10),
                               'length': np.linspace(0, 1, 10)})
    out_ds = LabelledFunction(cylinder_volume).apply_in_namespace(in_ds)
    assert 'volume' in out_ds.data_vars

def test_set_default():
    lc = label(cylinder_volume)
    llc = lc.set_default(radius=1.0)
    assert llc(length=1.0) == np.pi
    assert copy(llc)(length=1.0) == np.pi

    lllc = lc.set_default(radius=1.0, length=1.0)
    assert lllc() == np.pi

    rllc = lllc.reset_default('radius', 'length')
    assert rllc.default_values == {}
    with pytest.raises(TypeError):
        rllc()

def test_hide():
    a = np.random.rand(1)[0]
    assert label(optional_add).hide('x').recorded_call(y=a) == {'y': a, 'x+y': a}
    assert label(optional_add).hide('y').recorded_call(y=a) == {'x': 0, 'x+y': a}
    assert label(optional_add).hide('y').recorded_call() == {'x': 0, 'x+y': 0}
    assert label(optional_add).hide_all_but('y').recorded_call() == {'y': 0, 'x+y': 0}

def test_fix():
    lc = label(cylinder_volume)
    llc = lc.fix(radius=1.0)
    assert llc.default_values == {'radius': 1.0}
    assert llc.hidden_inputs == {'radius'}
    assert llc(length=1.0) == np.pi
    assert llc.recorded_call(length=1.0) == {'length': 1.0, 'volume': np.pi}

