# Tool for parametric study


```python
In [1]: def double(x):
   ...:     return 2*x
   ...:

In [2]: pandas_map(double, [3, 4, 5])
Out[2]:
   double
x
3       6
4       8
5      10

In [3]: def add(x, y):
   ...:     return x+y
   ...:

In [4]: pandas_map(add, [2, 3], [5, 6])
Out[4]:
     add
x y
2 5    7
3 6    9

In [5]: def add(x, y) -> 'sum':
   ...:     return x+y
   ...:

In [6]: pandas_map(add, [2, 3], [5, 6])
Out[6]:
     sum
x y
2 5    7
3 6    9

In [7]: full_parametric_study(add, [2, 3], [5, 6]).to_xarray()
Out[7]:
<xarray.Dataset>
Dimensions:  (x: 2, y: 2)
Coordinates:
  * x        (x) int64 2 3
  * y        (y) int64 5 6
Data variables:
    sum      (x, y) int64 7 8 8 9

In [8]: def cube(x) -> ('width', 'height', 'depth'):
   ...:     return (x, x, x)
   ...:

In [9]: pandas_map(cube, [5, 6, 7])
Out[9]:
   width  height  depth
x
5      5       5      5
6      6       6      6
7      7       7      7

In [10]: _.to_xarray()
Out[10]:
<xarray.Dataset>
Dimensions:  (x: 3)
Coordinates:
  * x        (x) int64 5 6 7
Data variables:
    width    (x) int64 5 6 7
    height   (x) int64 5 6 7
    depth    (x) int64 5 6 7
```
