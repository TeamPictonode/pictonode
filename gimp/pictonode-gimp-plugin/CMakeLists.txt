# No Implied Warranty

cmake_minimum_required(VERSION 3.0)
project(PictonodeGimpPlugin)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PkgConfig REQUIRED)
pkg_check_modules(GIMP REQUIRED gimp-2.0>=2.8)

include_directories(${GIMP_INCLUDE_DIRS})
link_directories(${GIMP_LIBRARY_DIRS})

# The "src" directory relative to CmakeLists
set(SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src)

add_custom_target(
    format ALL
    COMMAND clang-format -i -style=file ${SRC_DIR}/*.cpp
)

# Compile and link src/plugin.cpp
add_library(pictonode-gimp-plugin src/plugin.cpp)
target_link_libraries(pictonode-gimp-plugin ${GIMP_LIBRARIES})
