
from .__about__ import (
    __title__, __description__, __version__, __author__, __uri__, __license__
)

from .labels import label
from .pipeline import pipeline, compose, let, show, relabel
from .maps import pandas_map, pandas_cartesian_product, full_parametric_study
from .decorators import time
