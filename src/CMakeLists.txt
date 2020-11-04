cmake_minimum_required(VERSION 3.17)

set(CMAKE_CXX_STANDARD 20)
set(UNIT_TESTS test/BTWModelTest.cpp)
set(BINARY ${CMAKE_PROJECT_NAME})

include_directories(${Boost_INCLUDE_DIRS})

set(BINARY ${CMAKE_PROJECT_NAME})
set(SOURCES Simulator.cpp BTWModel.h BTWModel.cpp)

add_executable(btwsim ${SOURCES})

add_library(${BINARY}_lib STATIC ${SOURCES})
target_link_libraries (${BINARY} ${Boost_LIBRARIES})
