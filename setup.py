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
    Extension(
        name="piece",
        sources=["piece.pyx"],
    ),
    Extension(
        name="board",
        sources=["board.pyx"],
    ),
    Extension(
        name="core_utils",
        sources=["core_utils.pyx"],
    ),
]

setup(
    ext_modules=cythonize(ext_modules),
)
