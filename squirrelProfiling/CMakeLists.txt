cmake_minimum_required(VERSION 2.8.9)
project(sqProfiling)

set(SQUIRREL_PATH "/home/edward/Documents/avDeps/squirrel" CACHE FILEPATH "")

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=gnu++11")

include_directories("${SQUIRREL_PATH}/include")
include_directories("src")

file(GLOB_RECURSE INCLUDE_FILES src/*.h)
file(GLOB_RECURSE SRC_FILES src/*.cpp)

add_executable(sqProfiling ${SRC_FILES} ${INCLUDE_FILES})

target_link_libraries(sqProfiling "${SQUIRREL_PATH}/build/squirrel/libsquirrel_static.a" "${SQUIRREL_PATH}/build/sqstdlib/libsqstdlib_static.a")
