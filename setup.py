from setuptools import Extension, setup
from Cython.Build import cythonize

ext_modules = [
    # Other extension modules (if any)
    Extension(
        name="mask_utils",
        sources=["mask_utils.pyx"],
    ),
    Extension(
        name="binary_ops_utils",
        sources=["binary_ops_utils.pyx"],
    ),
]

setup(
    ext_modules=cythonize(ext_modules),
)
