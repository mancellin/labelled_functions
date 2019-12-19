from time import sleep
from labelled_functions.maps import pandas_map

def f(i):
    sleep(2.0)
    print(i)
    return 2*i

pandas_map(f, n_jobs=2, i=range(12))


