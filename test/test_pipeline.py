#!/usr/bin/env python
# coding: utf-8

import pytest

from labelled_functions.labels import LabelledFunction, label
from labelled_functions.pipeline import LabelledPipeline, pipeline, compose
from labelled_functions.special_functions import let, relabel, show
from labelled_functions.decorators import keeping_inputs

from example_functions import *


def test_pipeline():
    pipe = pipeline([random_radius, cylinder_volume], name="pipe")
    assert pipe.input_names == ['length']
    assert pipe.output_names == ['volume']
    assert 0.0 < pipe(length=1.0)['volume'] < 2*compute_pi()
    assert pipe.rename("bar").name == "bar"
    assert repr(pipe) == (
        "pipe:\n"
        "	random_radius() -> (radius)\n"
        "	cylinder_volume(radius, length) -> (volume)"
    )


    with pytest.raises(TypeError):
        pipe(length=1.0, potato=1.0)

    # Creation with "|" symbol
    pipe = LabelledFunction(random_radius) | LabelledFunction(cylinder_volume)
    assert isinstance(pipe, LabelledPipeline)
    assert pipe.input_names == ['length']
    assert pipe.output_names == ['volume']
    assert 0.0 < pipe(length=1.0)['volume'] < 2*compute_pi()


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
    pipe = keeping_inputs(pipeline([random_radius, cylinder_volume], return_intermediate_outputs=False))
    result = pipe(length=1.0)
    assert 'length' in result.keys()
    assert 'radius' not in result.keys()

    # Inputs and outputs and intermediate variable
    pipe = keeping_inputs(pipeline([random_radius, cylinder_volume], return_intermediate_outputs=True))
    result = pipe(length=1.0)
    assert 'length' in result.keys()
    assert 'radius' in result.keys()


def test_default_variables():
    def f(a):
        b = 2*a
        return b
    def g(b, c=3):
        output = c - b
        return output

    pipe = pipeline([f, g])
    assert pipe(a=1) == {'output': 1}
    assert pipe(a=1, c=0) == {'output': -2}

    ###
    pipe = pipeline([cube], default_values={'x': 1.0})
    assert pipe()['volume'] == 1.0
    assert pipe(x=10.0)['volume'] == 1000.0

    pipe = pipeline([cube]).set_default(x=1.0)
    assert pipe()['volume'] == 1.0
    assert pipe(x=10.0)['volume'] == 1000.0


def test_fix():
    a, b = 1, 2
    f = label(lambda x, y: x + y, name="foo", output_names=['z'])
    g = label(lambda x, z: x * z, name="bar", output_names=['u'])
    h = label(lambda u: u**2, name="baz", output_names=['w'])

    pipe = pipeline([f, g, h]).fix(y=b)
    assert pipe(x=a) == {'w': (a*(a+b))**2}

    pipe = pipeline([f, g, h]).fix(x=a)
    assert pipe(y=b) == {'w': (a*(a+b))**2}


def test_let():
    l = let(x=1.0)
    assert l.input_names == []
    assert l.output_names == ['x']
    assert l.default_values == {}
    assert l() == (1.0,)
    assert keeping_inputs(l)() == {'x': 1.0}

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
    assert keeping_inputs(l)(foo=1000) == {'foo': 1000, 'bar': 1000}

    pipe = pipeline([relabel('foo', 'x'), cube, relabel("volume", "moose")])
    assert pipe(foo=1.0)['moose'] == 1.0


def test_show():
    pipe = pipeline([show('x'), cube, show('x', 'volume', 'area')])
    pipe(x=1.0)


def test_compose():
    composed = compose([cylinder_volume, random_radius])
    assert composed.input_names == ['length']
    assert composed.output_names == ['volume']


def test_vertical_line():
    p = pipeline([cube])
    pp = let(x=1.0) | p | show('area')
    assert pp()['volume'] == 1.0


def test_merge():
    pipe = pipeline([random_radius, cylinder_volume])
    lf = pipe.merge_graph()
    # lf.graph(backend='pygraphviz', rankdir='TB').draw('/home/matthieu/tempo/test.pdf', prog='dot')
