#!/usr/bin/env python
# coding: utf-8

import pytest

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

    lc = LabelledFunction(cube)
    assert lc(0) == cube(0)
    assert lc.input_names == ['x']
    assert lc.output_names == ['cube[0]', 'cube[1]', 'cube[2]']

    llc = LabelledFunction(lc)
    assert llc is lc


@given(number, number)
@settings(max_examples=1)
def test_recorder(a, b):
    assert recorded_call(pi) == {'pi': 3.14159}
    assert recorded_call(deep_thought) == {'The Answer': 42}

    assert recorded_call(double, a) == {'x': a, 'double': 2*a}

    assert recorded_call(optional_double, a)   == {'x': a, 'optional_double': 2*a}
    assert recorded_call(optional_double, x=a) == {'x': a, 'optional_double': 2*a}
    assert recorded_call(optional_double, )    == {'x': 0, 'optional_double': 0}

    assert recorded_call(add, a, b) == {'x': a, 'y': b, 'add': a+b}

    assert recorded_call(optional_add, a, b)     == {'x': a, 'y': b, 'optional_add': a+b}
    assert recorded_call(optional_add, a)        == {'x': a, 'y': 0, 'optional_add': a}
    assert recorded_call(optional_add, )         == {'x': 0, 'y': 0, 'optional_add': 0}
    assert recorded_call(optional_add, x=a, y=b) == {'x': a, 'y': b, 'optional_add': a+b}
    assert recorded_call(optional_add, y=a, x=b) == {'x': b, 'y': a, 'optional_add': a+b}
    assert recorded_call(optional_add, y=a)      == {'x': 0, 'y': a, 'optional_add': a}

    assert recorded_call(cube, a) == {'x': a, 'cube[0]': 12*a, 'cube[1]': 6*a**2, 'cube[2]': a**3}
    assert recorded_call(annotated_cube, a) == {'x': a, 'length': 12*a, 'area': 6*a**2, 'volume': a**3}

    with pytest.raises(TypeError):
        recorded_call(all_kinds_of_args, 0, 1, 2, 3)
    assert recorded_call(all_kinds_of_args, 0, 1, z=2, t=3)         == {'x': 0, 'y': 1, 'z': 2, 't': 3, 'all_kinds_of_args': None}
    assert recorded_call(all_kinds_of_args, x=0, y=1, z=2, t=3) == {'x': 0, 'y': 1, 'z': 2, 't': 3, 'all_kinds_of_args': None}
    assert recorded_call(all_kinds_of_args, x=0, z=2, t=3)      == {'x': 0, 'y': 1, 'z': 2, 't': 3, 'all_kinds_of_args': None}
    assert recorded_call(all_kinds_of_args, x=0, z=2)           == {'x': 0, 'y': 1, 'z': 2, 't': 3, 'all_kinds_of_args': None}
    assert recorded_call(all_kinds_of_args, z=2, t=3, x=0)      == {'x': 0, 'y': 1, 'z': 2, 't': 3, 'all_kinds_of_args': None}


def test_namespace():
    namespace = {'x': 0, 'y': 3, 'z': 2}
    new_namespace = LabelledFunction(add).apply_in_namespace(namespace)
    assert new_namespace == {'add': 3, 'z': 2}
