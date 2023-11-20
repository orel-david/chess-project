from setuptools import Extension, setup
from Cython.Build import cythonize
import os

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
    Extension(
        name="transposition_table",
        sources=["transposition_table.pyx"],
    ),
    Extension(
        name="repetition_table",
        sources=["repetition_table.pyx"],
    ),
]

setup(
    ext_modules=cythonize(ext_modules),
)

current_directory = os.path.abspath(os.path.dirname(__file__))

# Delete all .c files which are biproduct 
c_files_to_delete = [f for f in os.listdir(current_directory) if f.endswith(".c")]
for c_file in c_files_to_delete:
    os.remove(os.path.join(current_directory, c_file))