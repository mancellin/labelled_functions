#!/usr/bin/env python
# coding: utf-8

import numpy as np

def pi():
    return 3.14159

def deep_thought() -> "The Answer":
    return 42

def double(x):
    return 2*x

def optional_double(x=0):
    return 2*x

def add(x, y):
    return x+y

def optional_add(x=0, y=0):
    return x+y

def cylinder_volume(radius, length):
    return np.pi * radius**2 * length

def cube(x):
    return (12*x, 6*x**2, x**3)

def annotated_cube(x) -> ('length', 'area', 'volume'):
    return (12*x, 6*x**2, x**3)
