from time import sleep
from joblib import Parallel, delayed

from labelled_functions import label
from labelled_functions.maps import *

def f(i):
    print(i)
    sleep(0.5)
    return i

# WORKS
# print(Parallel(n_jobs=4)(delayed(f)(i) for i in range(8)))
# print(Parallel(n_jobs=4)(label(delayed(f))(i) for i in range(8)))
# print(Parallel(n_jobs=4)((f, tuple(), {'i': i}) for i in range(8)))
print(parallel_recorded_map(f, i=range(8)))

# BROKEN
print(Parallel(n_jobs=4)(delayed(label(f).recorded_call)(i) for i in range(8)))

