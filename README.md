# BladeRF Spectrum Analyzer

## Overview

This project implements a real-time spectrum analyzer using a BladeRF software-defined radio. It consists of a C backend for interfacing with the BladeRF hardware and performing FFT calculations, and a Python frontend for the user interface. The spectrum analyzer provides both a traditional spectrum plot and a waterfall display, allowing for a more detailed display.

## Features

- Real-time spectrum analysis
- Waterfall display for time-domain signal visualization
- Adjustable center frequency, sample rate, bandwidth, and gain
- Color-coded signal strength representation
- Cross-platform compatibility (Linux, macOS, Windows)

## Requirements

### Hardware

- BladeRF software-defined radio (tested with BladeRF XA9)
- Host computer with USB 3.0 port

### Software

- C compiler (GCC recommended)
- CMake (version 3.10 or higher)
- Python 3.6 or higher
- BladeRF libraries and drivers
- FFTW3 library

See `requirements.txt` for Python package dependencies.

## Installation

1. Clone the repository:

git clone https://github.com/jaw1999/bladerf_tool.git

cd bladerf-tool

2. Install the BladeRF libraries and drivers following the instructions at [Nuand's BladeRF repository](https://github.com/Nuand/bladeRF).

3. Install FFTW3:
- On Ubuntu/Debian: `sudo apt-get install libfftw3-dev`
- On macOS with Homebrew: `brew install fftw`
- On Windows, download from [FFTW's website](http://www.fftw.org/install/windows.html)

4. Build the C backend:


cd backend
mkdir build && cd build
cmake ..
make
sudo make install

5. Install Python dependencies:

cd ../../frontend
pip install -r requirements.txt

## Usage

1. Connect your BladeRF device to your computer.

2. Run the spectrum analyzer:

cd frontend

python spectrum_analyzer_ui.py

3. Use the UI controls to adjust:
- Center Frequency
- Sample Rate
- Bandwidth
- Gain

4. The spectrum plot shows the current frequency domain representation of the signal.

5. The waterfall plot shows signal strength over time, with the most recent data at the top.

## Troubleshooting

- If you encounter "library not found" errors, ensure that `libspectrumanalyzer.so` (or `.dll` on Windows) is in your system's library path. You may need to add its location to `LD_LIBRARY_PATH` on Linux or `PATH` on Windows.

- For "device not found" errors, check your BladeRF connection and ensure the drivers are properly installed.

- If you see no signal or unexpected results, try adjusting the gain setting.

