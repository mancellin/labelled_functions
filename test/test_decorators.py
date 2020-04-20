#!/usr/bin/env python
# coding: utf-8

import pytest

from time import sleep

from labelled_functions import label, pipeline
from labelled_functions.maps import pandas_map
from labelled_functions.decorators import keeping_inputs, with_progress_bar, decorate, cache
from example_functions import *


def test_keeping_inputs():
    a, b = 12, 34

    assert keeping_inputs(compute_pi)() == {'pi': 3.14159}

    assert keeping_inputs(double)(a)            == {'x': a, '2*x': 2*a}
    assert keeping_inputs(optional_double)(a)   == {'x': a, '2*x': 2*a}
    assert keeping_inputs(optional_double)(x=a) == {'x': a, '2*x': 2*a}
    assert keeping_inputs(optional_double)()    == {'x': 0, '2*x': 0}

    assert keeping_inputs(all_kinds_of_args)(0, 1, z=2, t=3)     == {'x': 0, 'y': 1, 'z': 2, 't': 3}
    assert keeping_inputs(all_kinds_of_args)(x=0, y=1, z=2, t=3) == {'x': 0, 'y': 1, 'z': 2, 't': 3}
    assert keeping_inputs(all_kinds_of_args)(x=0, z=2, t=3)      == {'x': 0, 'y': 1, 'z': 2, 't': 3}
    assert keeping_inputs(all_kinds_of_args)(x=0, z=2)           == {'x': 0, 'y': 1, 'z': 2, 't': 3}
    assert keeping_inputs(all_kinds_of_args)(z=2, t=3, x=0)      == {'x': 0, 'y': 1, 'z': 2, 't': 3}

    with pytest.raises(TypeError):
        keeping_inputs(all_kinds_of_args)(0, 1, 2, 3)


def test_cache():
    # Cache one function
    pipe = cache(label(random_radius)) | label(cylinder_volume)
    a = pipe(length=1.0)
    b = pipe(length=1.0)
    assert a == b

    # Cache whole function
    pipe = cache(pipeline([random_radius, cylinder_volume]))
    a = pipe(length=1.0)
    b = pipe(length=1.0)
    assert a == b


def test_progress_bar(capfd):
    def wait(dt):
        sleep(dt)
        output = 1
        return output

    pandas_map(wait, dt=[0.01]*10, progress_bar=True)

    out, err = capfd.readouterr()
    assert "10/10" in err

