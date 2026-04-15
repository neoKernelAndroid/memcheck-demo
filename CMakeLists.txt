cmake_minimum_required(VERSION 3.10)
project(memcheck_demo C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_library(memcheck_sample STATIC
    tools/memcheck/sample_good.c
)
