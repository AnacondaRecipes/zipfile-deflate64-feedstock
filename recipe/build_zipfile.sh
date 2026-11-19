#!/bin/bash
set -euxo pipefail

# The sdist's vendored zlib/ must not be compiled: the extension links
# libinfback9-resumable (built by build.sh) through its headers here.
rm -rf zlib
export INFBACK9_INCLUDE="${PREFIX}/include/infback9-resumable"
"${PYTHON}" -m pip install . -vv --no-deps --no-build-isolation
