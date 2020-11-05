set(CMAKE_CXX_STANDARD 20)
set(UNIT_TESTS test/BTWModelTest.cpp)
set(BINARY ${CMAKE_PROJECT_NAME})

include_directories(${Boost_INCLUDE_DIRS})

set(BINARY ${CMAKE_PROJECT_NAME})
set(SOURCES Simulator.cpp BTWModel.h BTWModel.cpp ForestFireModel.cpp ForestFireModel.h ModelUtils.cpp ModelUtils.h)

add_executable(btwsim ${SOURCES})

add_library(${BINARY}_lib STATIC ${SOURCES})
target_link_libraries(${BINARY} ${Boost_LIBRARIES} ${Boost_LOG_LIBRARY})
