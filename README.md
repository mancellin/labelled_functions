# Labelled functions

Labelled functions are Python functions with names inputs and outputs.
In the same way that [xarray](https://xarray.pydata.org) adds names to the axes of Numpy's arrays,
the present package adds names to the "axes" of Python's functions.

At the moment, there are two main applications of labelled functions implemented
in this package:
* Interaction with labelled data from [pandas](https://pandas.pydata.org/) or [xarray](https://xarray.pydata.org)
* Clever function composition to build pipeline for complex workflows.
See examples below.

# Interaction with labelled data

## Example: building a dataset from a labelled function

```python
import calendar
import labelled_functions as lf

def weekday_of_new_year(year):
    """A normal Python function that makes a dummy computation."""
    weekday_index = calendar.weekday(year, 1, 1)
    weekday_name = calendar.day_name[weekday_index]
    return weekday_index, weekday_name

# Apply the function to a range of inputs.
df = lf.pandas_map(weekday_of_new_year, year=range(2000, 2100))
```
`pandas_map` returns a Pandas dataframe labelled with the inputs and ouputs of
the function:
```python
>>> print(df.head())
      weekday_index weekday_name
year
2000              5     Saturday
2001              0       Monday
2002              1      Tuesday
2003              2    Wednesday
2004              3     Thursday
```

## Example: interact with Pandas dataframe

```python
import numpy as np
from numpy import pi
import pandas as pd
import labelled_functions as lf

my_cylinders = pd.DataFrame(
    [[1.4, 2.0, 'red'],
     [5.2, 3.2, 'blue'],
     [9.1, 3.0, 'red'],
     [1.2, 1.9, 'green']],
    columns=['radius', 'length', 'color']
)

def cylinder_sizes(radius, length):
    volume = length * 2*pi*radius**2
    area = 4*pi*radius**2 + length*2*pi*radius
    return volume, area
```

```python
>>> print(lf.pandas_map(cylinder_sizes, my_cylinders))
                    volume         area
radius length
1.4    2.0       24.630086    42.223005
5.2    3.2      543.671458   444.346865
9.1    3.0     1560.931726  1212.152109
1.2    1.9       17.190795    32.421236
```

# Lightweight pipeline builder

## Functional-ish programming

TODO	

## Acknowledgments

Some inspiration comes from the [xarray-simlab](https://github.com/benbovy/xarray-simlab) package by Benoit Bovy.

## Author and license

Matthieu Ancellin, MIT License.
