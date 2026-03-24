"""
Build configuration for pyfzz.

This setup.py works together with pyproject.toml.  pybind11 is declared
as a build dependency in pyproject.toml so it is always available when
this file is executed.
"""

import os
from setuptools import setup, Extension, find_packages
import pybind11

# ---------------------------------------------------------------------------
# Paths  (must be relative for setuptools)
# ---------------------------------------------------------------------------
_PYFZZ_DIR = "pyfzz"
_PHAT_INCLUDE = os.path.join(_PYFZZ_DIR, "phat-include")

# ---------------------------------------------------------------------------
# C++ extension — compiled into the pyfzz package as _fzz_core
# ---------------------------------------------------------------------------
ext = Extension(
    name="pyfzz._fzz_core",
    sources=[
        os.path.join(_PYFZZ_DIR, "pyfzz.cpp"),
        "fzz.cpp",
    ],
    include_dirs=[
        pybind11.get_include(),
        _PHAT_INCLUDE,
        ".",                # so that #include "fzz.h" resolves
    ],
    language="c++",
    extra_compile_args=["-std=c++14", "-O3", "-DNDEBUG"],
)

# ---------------------------------------------------------------------------
setup(
    packages=find_packages(),
    ext_modules=[ext],
)
