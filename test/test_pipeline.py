#!/usr/bin/env python
# coding: utf-8

import pytest

from labelled_functions.pipeline import compose, pipeline, let, relabel

from example_functions import *


def test_pipeline():
    pipe = pipeline([random_radius, cylinder_volume])
    assert pipe.input_names == ['length']
    assert pipe.output_names == ['volume']
    assert 0.0 < pipe(length=1.0)['volume'] < 2*compute_pi()

    with pytest.raises(TypeError):
        pipe(length=1.0, potato=1.0)


def test_return_intermediate_outputs():
    # Only outputs
    pipe = pipeline([random_radius, cylinder_volume], return_intermediate_outputs=False)
    result = pipe(length=1.0)
    assert 'length' not in result.keys()
    assert 'radius' not in result.keys()

    # Outputs and intermediate variable
    pipe = pipeline([random_radius, cylinder_volume], return_intermediate_outputs=True)
    result = pipe(length=1.0)
    assert 'length' not in result.keys()
    assert 'radius' in result.keys()

    # Inputs and outputs but no intermediate variable
    pipe = pipeline([random_radius, cylinder_volume], return_intermediate_outputs=False)
    result = pipe.recorded_call(length=1.0)
    assert 'length' in result.keys()
    assert 'radius' not in result.keys()

    # Inputs and outputs and intermediate variable
    pipe = pipeline([random_radius, cylinder_volume], return_intermediate_outputs=True)
    result = pipe.recorded_call(length=1.0)
    assert 'length' in result.keys()
    assert 'radius' in result.keys()


def test_default_variables():
    def f(a) -> 'b':
        return 2*a
    def g(b, c=3) -> 'output':
        return c - b

    pipe = pipeline([f, g])
    assert pipe(a=1) == {'output': 1}
    assert pipe(a=1, c=0) == {'output': -2}

    pipe = pipeline([cube], default_values={'x': 1.0})
    assert pipe()['volume'] == 1.0
    assert pipe(x=10.0)['volume'] == 1000.0

    pipe = pipeline([cube]).set_default(x=1.0)
    assert pipe()['volume'] == 1.0
    assert pipe(x=10.0)['volume'] == 1000.0


def test_let():
    l = let(x=1.0)
    assert l.input_names == []
    assert l.output_names == ['x']
    assert l.default_values == {}
    assert l() == (1.0,)
    assert l.recorded_call() == {'x': 1.0}

    pipe = pipeline([let(x=1.0), cube])
    assert pipe()['volume'] == 1.0

    pipe = pipeline([let(radius=1.0), cylinder_volume])
    assert pipe(length=1.0)['volume'] == np.pi

    pipe = pipeline([let(radius=1.0, length=1.0), cylinder_volume])
    assert pipe()['volume'] == np.pi


def test_relabel():
    l = relabel("foo", "bar")
    assert l.input_names == ["foo"]
    assert l.output_names == ["bar"]
    assert l.default_values == {}
    assert l(foo=1000) == {'bar': 1000}
    assert l.recorded_call(foo=1000) == {'foo': 1000, 'bar': 1000}

    pipe = pipeline([relabel('foo', 'x'), cube, relabel("volume", "moose")])
    assert pipe(foo=1.0)['moose'] == 1.0


def test_compose():
    composed = compose([cylinder_volume, random_radius])
    assert composed.input_names == ['length']
    assert composed.output_names == ['volume']


