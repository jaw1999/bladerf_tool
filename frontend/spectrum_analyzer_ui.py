import sys
import ctypes
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, 
                             QHBoxLayout, QTabWidget, QFormLayout, QSplitter, QStyleFactory)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QLinearGradient, QPalette

# Load the shared library
try:
    lib = ctypes.CDLL('libspectrumanalyzer.so')
except OSError as e:
    print(f"Error loading library: {e}")
    print("Try setting LD_LIBRARY_PATH to include the directory containing libspectrumanalyzer.so")
    sys.exit(1)

# Define function prototypes
lib.sa_init.restype = ctypes.c_void_p
lib.sa_close.argtypes = [ctypes.c_void_p]
lib.sa_set_frequency.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
lib.sa_set_sample_rate.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
lib.sa_set_bandwidth.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
lib.sa_set_gain.argtypes = [ctypes.c_void_p, ctypes.c_int]
lib.sa_get_frequency.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint64)]
lib.sa_get_sample_rate.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
lib.sa_get_bandwidth.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
lib.sa_get_gain.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
lib.sa_get_fft.argtypes = [ctypes.c_void_p, np.ctypeslib.ndpointer(dtype=np.float32), ctypes.c_int]

class SpectrumAnalyzerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sa = lib.sa_init()
        if not self.sa:
            print("Failed to initialize spectrum analyzer")
            sys.exit(1)
        self.fft_size = 1024
        self.waterfall_history = 100
        self.waterfall_data = np.zeros((self.waterfall_history, self.fft_size))
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Sexy Spectrum Analyzer')
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel, QTabWidget, QPushButton, QLineEdit {
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3d3d3d;
                border: 1px solid #5a5a5a;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #5a5a5a;
                padding: 3px;
                border-radius: 3px;
            }
            QTabWidget::pane {
                border: 1px solid #5a5a5a;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }
            QTabBar::tab:selected {
                background-color: #2d2d2d;
            }
        """)

        # Create main layout
        main_layout = QHBoxLayout()

        # Create splitter for resizable layout
        splitter = QSplitter(Qt.Horizontal)

        # Create widget for plots
        plots_widget = QWidget()
        plots_layout = QVBoxLayout(plots_widget)

        # Spectrum plot
        self.spectrum_plot = pg.PlotWidget(title="Spectrum")
        plots_layout.addWidget(self.spectrum_plot)
        self.spectrum_curve = self.spectrum_plot.plot(pen=pg.mkPen(color=(0, 255, 255), width=2))
        self.spectrum_plot.setLabel('left', 'Power', units='dB')
        self.spectrum_plot.setLabel('bottom', 'Frequency', units='Hz')
        self.spectrum_plot.setBackground('#2d2d2d')

        # Waterfall plot
        self.waterfall_plot = pg.PlotWidget(title="Waterfall")
        plots_layout.addWidget(self.waterfall_plot)
        self.waterfall_img = pg.ImageItem()
        self.waterfall_plot.addItem(self.waterfall_img)
        self.waterfall_plot.setLabel('left', 'Time')
        self.waterfall_plot.setLabel('bottom', 'Frequency', units='Hz')
        self.waterfall_plot.setBackground('#2d2d2d')

        # Create a color map
        colors = [
            (0, 0, 0),        # Black for low intensity
            (0, 0, 255),      # Blue
            (0, 255, 255),    # Cyan
            (0, 255, 0),      # Green
            (255, 255, 0),    # Yellow
            (255, 0, 0)       # Red for high intensity
        ]
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, len(colors)), color=colors)
        lut = cmap.getLookupTable(0.0, 1.0, 256)
        self.waterfall_img.setLookupTable(lut)
        self.waterfall_img.setLevels([-80, 10])

        # Add plots widget to splitter
        splitter.addWidget(plots_widget)

        # Create settings widget
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)

        # Create tabs for settings
        tabs = QTabWidget()
        settings_layout.addWidget(tabs)

        # Device settings tab
        device_tab = QWidget()
        device_layout = QFormLayout(device_tab)

        self.freq_input = QLineEdit(str(self.get_frequency()))
        self.sample_rate_input = QLineEdit(str(self.get_sample_rate()))
        self.bandwidth_input = QLineEdit(str(self.get_bandwidth()))
        self.gain_input = QLineEdit(str(self.get_gain()))

        device_layout.addRow("Frequency (Hz):", self.freq_input)
        device_layout.addRow("Sample Rate (Hz):", self.sample_rate_input)
        device_layout.addRow("Bandwidth (Hz):", self.bandwidth_input)
        device_layout.addRow("Gain (dB):", self.gain_input)

        apply_button = QPushButton("Apply Settings")
        apply_button.clicked.connect(self.apply_settings)
        device_layout.addRow(apply_button)

        tabs.addTab(device_tab, "Device Settings")

        # Add settings widget to splitter
        splitter.addWidget(settings_widget)

        # Set the splitter as the central widget
        main_layout.addWidget(splitter)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(50)  # Update every 50 ms

    def apply_settings(self):
        self.set_frequency()
        self.set_sample_rate()
        self.set_bandwidth()
        self.set_gain()

    def set_frequency(self):
        try:
            freq = int(self.freq_input.text())
            if lib.sa_set_frequency(self.sa, freq) != 0:
                print("Failed to set frequency")
            else:
                print(f"Frequency set to {freq} Hz")
                self.update_plot_axes()
        except ValueError:
            print("Invalid frequency value")

    def set_sample_rate(self):
        try:
            rate = int(self.sample_rate_input.text())
            if lib.sa_set_sample_rate(self.sa, rate) != 0:
                print("Failed to set sample rate")
            else:
                print(f"Sample rate set to {rate} Hz")
                self.update_plot_axes()
        except ValueError:
            print("Invalid sample rate value")

    def set_bandwidth(self):
        try:
            bw = int(self.bandwidth_input.text())
            if lib.sa_set_bandwidth(self.sa, bw) != 0:
                print("Failed to set bandwidth")
            else:
                print(f"Bandwidth set to {bw} Hz")
        except ValueError:
            print("Invalid bandwidth value")

    def set_gain(self):
        try:
            gain = int(self.gain_input.text())
            if lib.sa_set_gain(self.sa, gain) != 0:
                print("Failed to set gain")
            else:
                print(f"Gain set to {gain} dB")
        except ValueError:
            print("Invalid gain value")

    def get_frequency(self):
        freq = ctypes.c_uint64()
        if lib.sa_get_frequency(self.sa, ctypes.byref(freq)) == 0:
            return freq.value
        return 0

    def get_sample_rate(self):
        rate = ctypes.c_uint32()
        if lib.sa_get_sample_rate(self.sa, ctypes.byref(rate)) == 0:
            return rate.value
        return 0

    def get_bandwidth(self):
        bw = ctypes.c_uint32()
        if lib.sa_get_bandwidth(self.sa, ctypes.byref(bw)) == 0:
            return bw.value
        return 0

    def get_gain(self):
        gain = ctypes.c_int()
        if lib.sa_get_gain(self.sa, ctypes.byref(gain)) == 0:
            return gain.value
        return 0

    def update_plot_axes(self):
        center_freq = self.get_frequency()
        sample_rate = self.get_sample_rate()
        start_freq = center_freq - sample_rate / 2
        end_freq = center_freq + sample_rate / 2
        self.spectrum_plot.setXRange(start_freq, end_freq)
        self.waterfall_plot.setXRange(start_freq, end_freq)

    def update_plot(self):
        fft_data = np.zeros(self.fft_size, dtype=np.float32)
        if lib.sa_get_fft(self.sa, fft_data, self.fft_size) == 0:
            # Update spectrum plot
            freq_range = np.linspace(self.get_frequency() - self.get_sample_rate()/2, 
                                     self.get_frequency() + self.get_sample_rate()/2, 
                                     self.fft_size)
            self.spectrum_curve.setData(freq_range, fft_data)

            # Update waterfall plot
            self.waterfall_data = np.roll(self.waterfall_data, 1, axis=0)
            self.waterfall_data[0] = fft_data
            self.waterfall_img.setImage(self.waterfall_data, autoLevels=False)
            self.waterfall_img.setRect(pg.QtCore.QRectF(freq_range[0], 0, freq_range[-1] - freq_range[0], self.waterfall_history))
        else:
            print("Failed to get FFT data")

    def closeEvent(self, event):
        self.timer.stop()
        lib.sa_close(self.sa)
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))  # Use Fusion style for a modern look
    window = SpectrumAnalyzerUI()
    window.show()
    sys.exit(app.exec_())