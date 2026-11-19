@echo on
REM libinfback9-resumable: zlib contrib/infback9 (+ zutil.c) as one shared
REM library. test_infback9 is built beside it and run on the upstream fixtures.
cmake -S "%RECIPE_DIR%\infback9" -B build-infback9 -G Ninja %CMAKE_ARGS% -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="%LIBRARY_PREFIX%" -DZLIB_SRC="%SRC_DIR%\zlib-1.4" -DINFBACK9R_TESTS=ON
if errorlevel 1 exit 1
cmake --build build-infback9
if errorlevel 1 exit 1
"%PYTHON%" "%RECIPE_DIR%\infback9\tests\run_decode_matrix.py" build-infback9\test_infback9.exe "%SRC_DIR%\fixture-downloads"
if errorlevel 1 exit 1
cmake --install build-infback9
if errorlevel 1 exit 1
