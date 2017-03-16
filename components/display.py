from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np

class Display:
    def __init__(self, recorder, processor):
        self._recorder = recorder
        self._processor = processor
        self._isShown = False

        self.setup()

    def setup(self):
        self._app = QtGui.QApplication([])
        self._window = QtGui.QWidget()
        self._layout = QtGui.QGridLayout()
        self._window.setLayout(self._layout)
        self._window.setWindowTitle("Klangfarbe")

        self._plotWaveForm = pg.PlotWidget(title = "Waveform")
        xRangeWaveform = np.arange(self._recorder.SIZE)
        yRangeWaveform = np.linspace(-(2**15), 2**15 - 1)
        self._plotWaveForm.setRange(
            xRange = xRangeWaveform,
            yRange = yRangeWaveform
        )
        self._layout.addWidget(self._plotWaveForm, 0, 0)

        self._plotSpectrum = pg.PlotWidget(title = "Spectrum")
        #xRangeSpectum = np.arange(self._recorder.SIZE / 2, dtype = float)
        #yRangeSpectrum = np.arange(self._recorder.SIZE * self._recorder.RATE / 10)
        #self._plotSpectrum.setRange(
        #    xRange = xRangeSpectrum,
        #    yRange = yRangeSpectrum
        #)
        self._layout.addWidget(self._plotSpectrum, 1, 0)

    def update(self):
        waveData = self._recorder.getWaveData()
        xs = np.abs(range(len(waveData)))

        self._plotWaveForm.clear()
        self._plotWaveForm.plot(xs, waveData, pen = "#FDBE1D")

        specData, freqs = self._processor.getSpectrumData()
        self._plotSpectrum.clear()
        self._plotSpectrum.plot(freqs, specData, pen = "#36C7F3")

    def show(self):
        if self._isShown:
            return

        def callUpdate():
            self.update()

        self._updateTimer = QtCore.QTimer()
        self._updateTimer.timeout.connect(self.update)
        self._updateTimer.start(100)

        self._isShown = True
        self._window.show()
        self._app.exec_()

        self._updateTimer.stop()
        self._isShown = False
