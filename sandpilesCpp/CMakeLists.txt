cmake_minimum_required(VERSION 3.17)
project(sandpilesCpp)

set(CMAKE_CXX_STANDARD 20)

add_executable(sandpilesCpp Simulator.cpp BTWModel.h BTWModel.cpp)