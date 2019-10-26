
from labelled_functions.compose import compose, pipeline

from example_functions import *


def test_compose():
    composed = compose([cylinder_volume, random_radius])
    assert composed.input_names == ['length']
    assert composed.output_names == ['volume']


def test_pipeline():
    pipe = pipeline([random_radius, cylinder_volume])
    assert pipe.input_names == ['length']
    assert pipe.output_names == ['volume']
    assert 0.0 < pipe(length=1.0)['volume'] < 2*compute_pi()
