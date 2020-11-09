set(CMAKE_CXX_STANDARD 20)
set(BINARY ${CMAKE_PROJECT_NAME})

include_directories(${Boost_INCLUDE_DIRS})

set(BINARY ${CMAKE_PROJECT_NAME})
set(SOURCES Simulator.cpp BTWModel.h BTWModel.cpp ForestFireModel.cpp ForestFireModel.h ModelUtils.cpp ModelUtils.h BTW3dModel.h BTW3dModel.cpp
        dynamics/BTWClassicalDynamics.cpp dynamics/BTWClassicalDynamics.h dynamics/ModelDynamics.h dynamics/DynamicsFactory.cpp dynamics/DynamicsFactory.h dynamics/BTWRandom2Dynamics.cpp
        dynamics/BTWRandom2Dynamics.h dynamics/BTWDeterministicNNN.cpp dynamics/BTWDeterministicNNN.h)

add_executable(btwsim ${SOURCES})

add_library(${BINARY}_lib STATIC ${SOURCES})
target_link_libraries(${BINARY} ${Boost_LIBRARIES} ${Boost_LOG_LIBRARY})
