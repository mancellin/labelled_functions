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

## As method chaining (WIP)

The labelled pipeline can also be seen as an alternative to method chaining:
```python
(
	my_object
	.do_this(1.0)
	.do_that(title="foo")
	.do_this_other_thing(True)
)
```

In the context of `labelled_function`, the equivalent code would be:
```python
(
	do_this
	| do_that
	| do_this_other_thing
)(
	self=my_object,
	x=1.0,
	title="foo",
	all=True,
)
```
or
```python
(
	do_this.fix(x=1.0)
	| do_that.fix(title="foo")
	| do_this_other_thing.fix(all=True)
)(
	self=my_object
)
```
or alternatively
```python
(
    let(self=my_object)
	| do_this.fix(x=1.0)
	| do_that.fix(title="foo")
	| do_this_other_thing.fix(all=True)
)()
```

Pro of `labelled_functions`:
* More general: can pass more that one object between functions

Cons of `labelled_functions`:
* All argument have to be keyword arguments.
* Too much `fix`. Some syntactic sugar should be added in the future.

# Other tools

```python
from time import sleep
from labelled_functions import time                                                                         

def f(x): 
    sleep(x)
    y = x/2
    return y 

print(time(f)(1))
# {'y': 0.5, 'f_execution_time': 1.0011490990873426}
```

## Acknowledgments

Some inspiration comes from the [xarray-simlab](https://github.com/benbovy/xarray-simlab) package by Benoit Bovy.

## Author and license

Matthieu Ancellin, MIT License.
