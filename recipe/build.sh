#!/bin/bash
set -euxo pipefail

# libinfback9-resumable: zlib's contrib/infback9 (+ zutil.c) as one shared
# library. test_infback9 is built beside it and run on the upstream fixtures.
cmake -S "${RECIPE_DIR}/infback9" -B build-infback9 -G Ninja ${CMAKE_ARGS} \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="${PREFIX}" \
    -DZLIB_SRC="${SRC_DIR}/zlib-src" \
    -DINFBACK9R_TESTS=ON
cmake --build build-infback9
"${PYTHON}" "${RECIPE_DIR}/infback9/tests/run_decode_matrix.py" \
    build-infback9/test_infback9 "${SRC_DIR}/fixture-downloads"
cmake --install build-infback9
