
from .__about__ import (
    __title__, __description__, __version__, __author__, __uri__, __license__
)

from .labels import label
from .pipeline import pipeline, compose, let, show, relabel
from .maps import pandas_map
from .cartesian_products import full_parametric_study
