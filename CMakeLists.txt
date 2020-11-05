cmake_minimum_required(VERSION 3.16)

project(btwsim)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_BINARY_DIR  build)

FIND_PACKAGE(Boost COMPONENTS program_options REQUIRED)

message(status "** Boost Include: ${Boost_INCLUDE_DIR}")
message(status "** Boost Libraries: ${Boost_LIBRARY_DIRS}")
message(status "** Boost Libraries: ${Boost_LIBRARIES}")

include_directories(${Boost_INCLUDE_DIR})
include_directories(src)

add_subdirectory(src)
add_subdirectory(test)
