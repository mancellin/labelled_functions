from setuptools import setup

setup(
    name='labelled_functions',
    version='0.1',
    description='Python functions with metadata on their inputs and outputs',
    author='Matthieu Ancellin',
    author_email='matthie.ancellin@cmla.ens-cachan.fr',
    license='MIT',
    install_requires=[
        'pandas',
        'xarray',
        'toolz',
        'parso',
    ],
    packages=['labelled_functions'],
)
