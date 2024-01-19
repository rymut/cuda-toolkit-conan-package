cmake_minimum_required(VERSION 3.1)

project(test_package)

find_package(nvcuda REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
add_library(test_library SHARED test_library.cpp)
target_link_libraries(test_library PRIVATE nvcuda::nvcuda)

