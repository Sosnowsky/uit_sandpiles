file(GLOB SRCS *.cpp)
set(BINARY ${CMAKE_PROJECT_NAME}_tst)

add_executable(${BINARY} ${SRCS} BTWClassicalDynamics.cpp BTWRandom2Dynamics.cpp BTWDeterministicNNNTest.cpp)

target_link_libraries(${BINARY} PUBLIC ${CMAKE_PROJECT_NAME}_lib libgtest)

add_test(NAME ${BINARY} COMMAND ${BINARY})