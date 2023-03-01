# 此文件仅为方便源码跳转，不做编译之用

project(xv6-analysis)
cmake_minimum_required(VERSION 3.24)

include_directories(xv6-lab)
include_directories(xv6-lab/kernel)

aux_source_directory(xv6-lab/user U)
add_executable(xv6-lab ${U})
