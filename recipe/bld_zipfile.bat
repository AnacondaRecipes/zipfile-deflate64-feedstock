@echo on
REM The sdist vendored zlib\ must not be compiled: the extension links
REM libinfback9-resumable (built by bld.bat) through its headers here.
if exist zlib rmdir /s /q zlib
if errorlevel 1 exit 1
set "INFBACK9_INCLUDE=%LIBRARY_INC%\infback9-resumable"
set "LIB=%LIBRARY_LIB%;%LIB%"
"%PYTHON%" -m pip install . -vv --no-deps --no-build-isolation
if errorlevel 1 exit 1
