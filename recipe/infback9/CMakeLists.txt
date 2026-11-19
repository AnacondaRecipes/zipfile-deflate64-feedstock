# Packaging build for libinfback9-resumable: zlib's contrib/infback9 decoder
# (plus zutil.c, which it needs privately) as one shared library that exports
# only three renamed entry points. ZLIB_SRC points at the patched zlib source.
cmake_minimum_required(VERSION 3.15)
project(infback9_resumable C)

if(NOT ZLIB_SRC)
  message(FATAL_ERROR "set -DZLIB_SRC=<path to the zlib source tree>")
endif()
file(TO_CMAKE_PATH "${ZLIB_SRC}" ZLIB_SRC)
option(INFBACK9R_TESTS "build test_infback9 (not installed)" OFF)

add_library(infback9r SHARED
  ${ZLIB_SRC}/zutil.c
  ${ZLIB_SRC}/contrib/infback9/infback9.c
  ${ZLIB_SRC}/contrib/infback9/inftree9.c)
target_include_directories(infback9r PRIVATE ${ZLIB_SRC} ${ZLIB_SRC}/contrib/infback9)
target_compile_definitions(infback9r PRIVATE
  inflateBack9Init_=infback9r_init_
  inflateBack9=infback9r_decode
  inflateBack9End=infback9r_end)
set_target_properties(infback9r PROPERTIES OUTPUT_NAME infback9-resumable SOVERSION 1)

# Export exactly the three renamed functions; everything else stays local.
if(WIN32)
  target_sources(infback9r PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/infback9-resumable.def)
  set_target_properties(infback9r PROPERTIES
    RUNTIME_OUTPUT_NAME infback9-resumable-1
    ARCHIVE_OUTPUT_NAME infback9-resumable)
elseif(APPLE)
  target_link_options(infback9r PRIVATE
    "LINKER:-exported_symbols_list,${CMAKE_CURRENT_SOURCE_DIR}/infback9r.exp")
  set_target_properties(infback9r PROPERTIES INSTALL_NAME_DIR "@rpath")
else()
  target_link_options(infback9r PRIVATE
    "LINKER:--version-script=${CMAKE_CURRENT_SOURCE_DIR}/infback9r.map")
endif()

if(INFBACK9R_TESTS)
  add_executable(test_infback9 tests/test_infback9.c)
  target_include_directories(test_infback9 PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR} ${ZLIB_SRC} ${ZLIB_SRC}/contrib/infback9)
  target_link_libraries(test_infback9 PRIVATE infback9r)
endif()

install(TARGETS infback9r
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib)
install(FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/infback9r.h
  ${ZLIB_SRC}/contrib/infback9/infback9.h
  ${ZLIB_SRC}/zlib.h
  ${ZLIB_SRC}/zconf.h
  DESTINATION include/infback9-resumable)
