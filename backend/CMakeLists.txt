cmake_minimum_required(VERSION 3.10)
project(SpectrumAnalyzer)

# Specify the C standard
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED True)

# Find BladeRF
find_path(BLADERF_INCLUDE_DIR NAMES libbladeRF.h
    PATHS /opt/bladeRF/host/libraries/libbladeRF/include
          /usr/include
          /usr/local/include
)

find_library(BLADERF_LIBRARY NAMES bladeRF
    PATHS /opt/bladeRF/build/host/libraries/libbladeRF/src
          /usr/lib
          /usr/local/lib
)

if(NOT BLADERF_INCLUDE_DIR OR NOT BLADERF_LIBRARY)
    message(FATAL_ERROR "BladeRF not found. Please install BladeRF or specify its location.")
endif()

include_directories(${BLADERF_INCLUDE_DIR})

# Find FFTW3
find_path(FFTW_INCLUDE_DIRS NAMES fftw3.h
    PATHS /usr/include
          /usr/local/include
)

find_library(FFTW_LIBRARIES NAMES fftw3f
    PATHS /usr/lib64
          /usr/lib
          /usr/local/lib
)

if(NOT FFTW_INCLUDE_DIRS OR NOT FFTW_LIBRARIES)
    message(FATAL_ERROR "FFTW3 not found. Please install FFTW3 or specify its location.")
endif()

include_directories(${FFTW_INCLUDE_DIRS})

# Add your source files
add_library(spectrumanalyzer SHARED
    src/spectrum_analyzer.c
)

# Include local headers
target_include_directories(spectrumanalyzer PRIVATE include)

# Link against BladeRF, FFTW3, and math library
target_link_libraries(spectrumanalyzer
    ${BLADERF_LIBRARY}
    ${FFTW_LIBRARIES}
    m
)

# Installation rules
install(TARGETS spectrumanalyzer
    LIBRARY DESTINATION lib
    PUBLIC_HEADER DESTINATION include
)

# Status messages for debugging
message(STATUS "BLADERF_INCLUDE_DIR: ${BLADERF_INCLUDE_DIR}")
message(STATUS "BLADERF_LIBRARY: ${BLADERF_LIBRARY}")
message(STATUS "FFTW_INCLUDE_DIRS: ${FFTW_INCLUDE_DIRS}")
message(STATUS "FFTW_LIBRARIES: ${FFTW_LIBRARIES}")