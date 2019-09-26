
def pi():
    return 3.14159

def deep_thought() -> "The Answer":
    return 42

def double(x):
    return 2*x

def optional_double(x=0):
    return 2*x

def sum(x, y):
    return x+y

def optional_sum(x=0, y=0):
    return x+y

def cube(x):
    return (x, x, x)

def annotated_cube(x) -> ('width', 'height', 'depth'):
    return (x, x, x)
