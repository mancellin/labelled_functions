#!/usr/bin/env python
# coding: utf-8

import pytest
from copy import copy

from labelled_functions.abstract import Unknown
from labelled_functions.labels import LabelledFunction, label
from labelled_functions.decorators import keeping_inputs

from example_functions import *


def test_labelling():
    lpi = LabelledFunction(compute_pi)
    assert lpi() == compute_pi()
    assert lpi.__wrapped__.__code__ == compute_pi.__code__
    assert lpi.name == compute_pi.__name__
    assert list(lpi.input_names) == []
    assert list(lpi.output_names) == ['pi']
    assert str(lpi) == "compute_pi() -> (pi)"

    lc = LabelledFunction(cube)
    assert lc(0) == cube(0)
    assert list(lc.input_names) == ['x']
    assert list(lc.output_names) == ['length', 'area', 'volume']
    assert str(lc) == "cube(x) -> (length, area, volume)"

    assert lc.rename("square parallelepiped").name == "square parallelepiped"
    assert lc.name == "cube"


def test_idempotence():
    lc = label(cube)
    llc = label(lc)
    assert llc is lc


def test_method():
    class A:
        def __init__(self):
            self.a = 10.0

        def f(self, x):
            y = 2*x + self.a
            return y

    lab_Af = LabelledFunction(A().f)
    assert list(lab_Af.input_names) == ['x']
    assert list(lab_Af.output_names) == ['y']
    assert lab_Af(2) == 14
    assert lab_Af(x=2) == 14

    lab_f = LabelledFunction(A.f)
    assert list(lab_f.input_names) == ['self', 'x']
    assert list(lab_f.output_names) == ['y']
    assert lab_f(A(), 2) == 14
    assert lab_f(A(), x=2) == 14


def test_lambda():
    ld = label(lambda foo: 2*foo)
    assert ld.input_names == ["foo"]
    assert ld.output_names is Unknown

def test_output_checking():
    la = LabelledFunction(add, output_names=['shrubbery'])
    assert la._has_never_been_run
    assert la(1, 2) == 3

    # Wrong number of outputs
    la = LabelledFunction(add, output_names=['moose', 'llama'])
    assert la._has_never_been_run
    with pytest.raises(TypeError):
        la(1, 2)


def test_namespace():
    namespace = {'x': 0, 'y': 3, 'z': 2}
    new_namespace = LabelledFunction(add).apply_in_namespace(namespace)
    assert new_namespace == {'x+y': 3, 'x': 0, 'y': 3, 'z': 2}

    import xarray as xr
    in_ds = xr.Dataset(coords={'radius': np.linspace(0, 1, 10),
                               'length': np.linspace(0, 1, 10)})
    out_ds = LabelledFunction(cylinder_volume).apply_in_namespace(in_ds)
    assert 'volume' in out_ds.data_vars


def test_set_default():
    lc = LabelledFunction(cylinder_volume)
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
    assert keeping_inputs(label(optional_add).hide('x'))(y=a)      == {'y': a, 'x+y': a}
    assert keeping_inputs(label(optional_add).hide('y'))()         == {'x': 0, 'x+y': 0}
    assert keeping_inputs(label(optional_add).hide_all_but('y'))() == {'y': 0, 'x+y': 0}

    with pytest.raises(TypeError):
        keeping_inputs(label(optional_add).hide('y'))(y=a)


def test_fix():
    lc = LabelledFunction(cylinder_volume)
    llc = lc.fix(radius=1.0)
    assert llc(length=1.0) == np.pi
    assert keeping_inputs(llc)(length=1.0) == {'length': 1.0, 'volume': np.pi}

