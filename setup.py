from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

setup(
	name="world",
	ext_modules=cythonize(
		Extension("world", ["world.pyx"], include_dirs=[numpy.get_include()])
	),
)
