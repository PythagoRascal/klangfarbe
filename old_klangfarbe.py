import pyaudio as pa
import numpy as np
from scipy import fftpack, signal
from multiprocessing import Process
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg

# CONSTANTS
SIZE = 2**10
FORMAT = pa.paInt16
CHANNELS = 1
RATE = 48000
INTERVAL = 0.2

# INIT WINDOW
app = QtGui.QApplication([])
window = QtGui.QWidget()
layout = QtGui.QGridLayout()
window.setLayout(layout)
window.setWindowTitle("Klangfarbe")

# INIT WAVEFORM PLOT
plotWaveform = pg.PlotWidget(title = "Waveform")
xRangeWaveform = np.arange(SIZE)
yRangeWaveform = np.linspace(-(2**15), 2**15 - 1)
plotWaveform.setRange(xRange = xRangeWaveform, yRange = yRangeWaveform)
layout.addWidget(plotWaveform, 0, 0)

# INIT SPECTRUM PLOT
plotSpectrum = pg.PlotWidget(title = "Spectrum")
xRangeSpectrum = np.arange(SIZE / 2, dtype = float)
#yRangeSpectrum = np.arange(RATE)
#plotSpectrum.setRange(xRange = xRangeSpectrum, yRange = yRangeSpectrum)
layout.addWidget(plotSpectrum, 1, 0)

# INIT AUDIO STREAM
audioHandle = pa.PyAudio()
audioStream = audioHandle.open(format = FORMAT, channels = CHANNELS, rate = RATE, input = True, frames_per_buffer = SIZE)

# DATA HANDLING FUNCTION
def update_data():
    byteString = audioStream.read(SIZE)
    waveData = np.fromstring(byteString, dtype = np.int16)

    specData = np.abs(fftpack.rfft(waveData))
    freqs = fftpack.rfftfreq(len(specData))

    specData = specData / max(specData)

    plotWaveform.clear()
    plotWaveform.plot(range(len(waveData)), waveData)

    plotSpectrum.clear()
    plotSpectrum.plot(np.abs(freqs), specData)

# UPDATING TIMER
timer = QtCore.QTimer()
timer.timeout.connect(update_data)
timer.start(0)

# SHOW WINDOW
window.show()
app.exec_()
