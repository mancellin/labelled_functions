
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


@given(number, number)
@settings(max_examples=1)
def test_recorder(a, b):
    assert recorded_call(pi) == {'pi': 3.14159}
    assert recorded_call(deep_thought) == {'The Answer': 42}

    assert recorded_call(double, a) == {'x': a, 'double': 2*a}

    assert recorded_call(optional_double, a) == {'x': a, 'optional_double': 2*a}
    assert recorded_call(optional_double, x=a) == {'x': a, 'optional_double': 2*a}
    assert recorded_call(optional_double, ) == {'optional_double': 0}

    assert recorded_call(sum, a, b) == {'x': a, 'y': b, 'sum': a+b}

    assert recorded_call(optional_sum, a, b) == {'x': a, 'y': b, 'optional_sum': a+b}
    assert recorded_call(optional_sum, a) == {'x': a, 'optional_sum': a}
    assert recorded_call(optional_sum, ) == {'optional_sum': 0}
    assert recorded_call(optional_sum, x=a, y=b) == {'x': a, 'y': b, 'optional_sum': a+b}
    assert recorded_call(optional_sum, y=a, x=b) == {'y': a, 'x': b, 'optional_sum': a+b}
    assert recorded_call(optional_sum, y=a) == {'y': a, 'optional_sum': a}

    assert recorded_call(cube, a) == {'x': a, 'cube[0]': 12*a, 'cube[1]': 6*a**2, 'cube[2]': a**3}
    assert recorded_call(annotated_cube, a) == {'x': a, 'length': 12*a, 'area': 6*a**2, 'volume': a**3}

