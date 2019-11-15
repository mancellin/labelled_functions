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

TODO

# Lightweight pipeline builder

## Example

TODO	

## Acknowledgments

Some inspiration comes from the [xarray-simlab](https://github.com/benbovy/xarray-simlab) package by Benoit Bovy.

## Author and license

Matthieu Ancellin, MIT License.
