"""
Setup for the "Cython-isation".

Run the following command in the terminal:

    cd projects/testing_cython
    python src/testing_cython/setup.py build_ext --inplace
"""

import pathlib

import setuptools
from Cython.Build import cythonize

HERE = pathlib.Path(__file__).parent


setuptools.setup(
    ext_modules=cythonize(str(HERE / "cythonisation.pyx"), annotate=True)
)
