import os
from setuptools import setup

base_dir = os.path.dirname(__file__)
src_dir = os.path.join(base_dir, "labelled_functions")

about = {}
with open(os.path.join(src_dir, "__about__.py")) as f:
    exec(f.read(), about)

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    author=about["__author__"],
    license=about["__license__"],
    url=about["__uri__"],
    packages=['labelled_functions'],
    install_requires=[
        'pandas',
        'xarray',
        'toolz',
        'parso',
        'joblib',
        'tqdm',
    ],
)
