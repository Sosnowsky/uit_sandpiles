cmake_minimum_required(VERSION 3.17)
project(btwsim)

set(CMAKE_CXX_STANDARD 20)
FIND_PACKAGE(Boost COMPONENTS program_options REQUIRED)
INCLUDE_DIRECTORIES(${Boost_INCLUDE_DIRS})

add_executable(btwsim Simulator.cpp BTWModel.h BTWModel.cpp)
TARGET_LINK_LIBRARIES(btwsim ${Boost_LIBRARIES})
