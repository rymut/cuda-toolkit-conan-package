cmake_minimum_required(VERSION 3.1)

project(test_package)

enable_language(CUDA)
find_package(cudart REQUIRED)

add_executable(${PROJECT_NAME} test_package.cu)
target_link_libraries(${PROJECT_NAME})
