#!/usr/bin/env python
# coding: utf-8

import numpy as np
from random import random

def compute_pi():
    pi = 3.14159
    return pi

def double(x):
    return 2*x

def optional_double(x=0):
    return 2*x

def add(x, y):
    return x+y

def optional_add(x=0, y=0):
    return x+y

def random_radius():
    radius = random()
    return radius

def cylinder_volume(radius, length):
    volume = np.pi * radius**2 * length
    return volume

def cube(x):
    length = 12*x
    area = 6*x**2
    volume = x**3
    return length, area, volume

def all_kinds_of_args(x, y=1, *, z, t=3):
    pass

#
# def deep_thought() -> "The Answer":
#     return 42
#
# def annotated_cube(x) -> ('length', 'area', 'volume'):
#     return (12*x, 6*x**2, x**3)
