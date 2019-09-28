#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
from labelled_functions.maps import pandas_map

df = pd.DataFrame({
    'foo': np.linspace(0.0, 10.0, 11),
    'bar': np.zeros(11),
    'baz': np.random.rand(11),
})

df['foobaz'] = pandas_map(lambda foo, baz: foo+baz, df).values
print(df)
