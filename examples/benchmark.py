#!/usr/bin/env python
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
from timeit import repeat
from labelled_functions.maps import pandas_map

def benchmark(n):
    """A very normal Python function that make some numerical experiment."""
    results = repeat(
        setup=f"""import numpy as np; A = np.random.rand({n}, {n}); b = np.random.rand({n})""",
        stmt="np.linalg.solve(A, b)",
        number=3,
        repeat=100,
    )
    return {'min': min(results), 'mean': np.mean(results), 'max': max(results)}

# Apply the function to a range of inputs to get a fully labelled dataframe.
df = pandas_map(benchmark, n=range(1, 500, 50))

# Plot this dataframe
df.plot(y=['min', 'mean', 'max'])
plt.show()
