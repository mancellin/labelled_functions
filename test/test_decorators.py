#!/usr/bin/env python
# coding: utf-8

import pytest

from labelled_functions.decorators import pass_inputs
from example_functions import *


def test_pass_inputs():
    a, b = 12, 34

    assert pass_inputs(compute_pi)() == {'pi': 3.14159}

    assert pass_inputs(double)(a)            == {'x': a, '2*x': 2*a}
    assert pass_inputs(optional_double)(a)   == {'x': a, '2*x': 2*a}
    assert pass_inputs(optional_double)(x=a) == {'x': a, '2*x': 2*a}
    assert pass_inputs(optional_double)()    == {'x': 0, '2*x': 0}

    assert pass_inputs(all_kinds_of_args)(0, 1, z=2, t=3)     == {'x': 0, 'y': 1, 'z': 2, 't': 3}
    assert pass_inputs(all_kinds_of_args)(x=0, y=1, z=2, t=3) == {'x': 0, 'y': 1, 'z': 2, 't': 3}
    assert pass_inputs(all_kinds_of_args)(x=0, z=2, t=3)      == {'x': 0, 'y': 1, 'z': 2, 't': 3}
    assert pass_inputs(all_kinds_of_args)(x=0, z=2)           == {'x': 0, 'y': 1, 'z': 2, 't': 3}
    assert pass_inputs(all_kinds_of_args)(z=2, t=3, x=0)      == {'x': 0, 'y': 1, 'z': 2, 't': 3}

    with pytest.raises(TypeError):
        pass_inputs(all_kinds_of_args)(0, 1, 2, 3)

