"""Build the C code with CFFI."""

import os
import sys
import sysconfig
from cffi import FFI

# Get the compiler. We support gcc and clang.
_compiler = os.environ.get("CC", sysconfig.get_config_var("CC"))

if "gcc" in _compiler:
    compiler = "gcc"
elif "clang" in _compiler:
    compiler = "clang"
else:
    raise ValueError(f"Compiler {_compiler} not supported for 21cmFAST")

ffi = FFI()

LOCATION = os.path.dirname(os.path.abspath(__file__))
CLOC = os.path.join(LOCATION, "src", "py21cmfast", "src")
include_dirs = [CLOC]

# ==================================================
# Set compilation arguments dependent on environment
# ==================================================
extra_compile_args = ["-w", "--verbose"]

if "DEBUG" in os.environ:
    extra_compile_args += ["-g", "-O0"]
else:
    extra_compile_args += ["-Ofast"]

if sys.platform == "darwin":
    extra_compile_args += ["-Xpreprocessor"]

extra_compile_args += ["-fopenmp"]

# Set the C-code logging level.
# If DEBUG is set, we default to the highest level, but if not,
# we set it to the level just above no logging at all.
log_level = os.environ.get("LOG_LEVEL", 4 if "DEBUG" in os.environ else 1)
available_levels = [
    "NONE",
    "ERROR",
    "WARNING",
    "INFO",
    "DEBUG",
    "SUPER_DEBUG",
    "ULTRA_DEBUG",
]


if isinstance(log_level, str) and log_level.upper() in available_levels:
    log_level = available_levels.index(log_level.upper())

try:
    log_level = int(log_level)
except ValueError:
    # note: for py35 support, can't use f strings.
    raise ValueError(
        "LOG_LEVEL must be specified as a positive integer, or one "
        "of {}".format(available_levels)
    )

library_dirs = []
for k, v in os.environ.items():
    if "inc" in k.lower():
        include_dirs += [v]
    elif "lib" in k.lower():
        library_dirs += [v]

libraries = ["m", "gsl", "gslcblas", "fftw3f_omp", "fftw3f"]

if compiler == "clang":
    libraries += ["omp"]

# =================================================================

# This is the overall C code.
ffi.set_source(
    "py21cmfast.c_21cmfast",  # Name/Location of shared library module
    """
    #define LOG_LEVEL {log_level}

    #include "GenerateICs.c"
    """.format(
        log_level=log_level
    ),
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=libraries,
    extra_compile_args=extra_compile_args,
)

# This is the Header file
with open(os.path.join(CLOC, "21cmFAST.h")) as f:
    ffi.cdef(f.read())

with open(os.path.join(CLOC, "Globals.h")) as f:
    ffi.cdef(f.read())

if __name__ == "__main__":
    ffi.compile()
