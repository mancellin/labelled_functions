#!/usr/bin/env python
# coding: utf-8

from itertools import product
from copy import copy
from typing import Union, Sequence, Dict

import pandas as pd

def from_sequence(**kwargs):
    for name, values in kwargs.items():
        yield from ({name: val} for val in values)

def merge_dicts(ds: Sequence[Dict]) -> Dict:
    merged = {}
    for d in ds:
        merged.update(d)
    return merged

def combine_plans_and_sequences(plans, sequences):
    plans = list(plans)
    for name, values in sequences.items():
        plan = from_sequence(**{name: values})
        plans.append(plan)
    return plans

def zip_plans(*plans, **sequences):
    return map(merge_dicts, zip(*combine_plans_and_sequences(plans, sequences)))

def product_of_plans(*plans, **sequences):
    return map(merge_dicts, product(*combine_plans_and_sequences(plans, sequences)))

def cross_plans(*plans, pivot, **sequences):
    yield pivot
    for plan in combine_plans_and_sequences(plans, sequences):
        for experiment in plan:
            current = copy(pivot)
            current.update(experiment)
            if current != pivot:
                yield current

if __name__ == "__main__":
    a = range(5)
    b = ['foo', 'bar', 'baz', 'moose', 'llama']
    c = range(100, 110)

    assert list(from_sequence(a=range(3))) == [{'a': 0}, {'a': 1}, {'a': 2}]
    assert list(from_sequence(a=range(3), b=['foo'])) == [{'a': 0}, {'a': 1}, {'a': 2}, {'b': 'foo'}]
    assert list(from_sequence(a=range(3))) == list(zip_plans(a=range(3)))
    assert list(from_sequence(a=range(3))) == list(product_of_plans(a=range(3)))

    assert list(zip_plans(a=range(2), b=['foo', 'bar'])) == [{'a': 0, 'b': 'foo'}, {'a': 1, 'b': 'bar'}]

    plan_1 = zip_plans(a=range(2), b=['foo', 'bar'])
    plan_2 = zip_plans(c=range(10))
    print(pd.DataFrame(cross_plans(plan_1, plan_2, pivot={'a': 1, 'b': 'bar', 'c': 0})))

