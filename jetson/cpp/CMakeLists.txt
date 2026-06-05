cmake_minimum_required(VERSION 3.18)
project(arena_vision LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "" FORCE)
endif()
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")

# OpenCV must be built WITH the aruco contrib module, and (for GPU preprocessing)
# WITH CUDA (cudaimgproc, cudawarping). See README for build notes.
find_package(OpenCV REQUIRED)
find_package(Threads REQUIRED)

add_executable(arena_vision
  src/main.cpp
  src/config.cpp
  src/arena.cpp
  src/capture.cpp
  src/detector.cpp
  src/homography.cpp
  src/tracking.cpp
  src/match_state.cpp
  src/protocol.cpp
  src/lora.cpp
  src/pipeline.cpp
)

target_include_directories(arena_vision PRIVATE
  ${OpenCV_INCLUDE_DIRS}
  ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(arena_vision PRIVATE
  ${OpenCV_LIBS}
  Threads::Threads
)

# Enable GPU preprocessing only if OpenCV reports a CUDA build.
if(DEFINED OpenCV_CUDA_VERSION)
  target_compile_definitions(arena_vision PRIVATE HAVE_CUDA_PREPROC=1)
  message(STATUS "OpenCV CUDA ${OpenCV_CUDA_VERSION} found -> GPU preprocessing ENABLED")
else()
  message(WARNING "OpenCV built without CUDA -> CPU preprocessing fallback")
endif()

message(STATUS "OpenCV version: ${OpenCV_VERSION}")
