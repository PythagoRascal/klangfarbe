import time, math
from threading import Thread
from scipy import fftpack, signal
import numpy as np

class Processor:
    def __init__(self, recorder):
        self._recorder = recorder

        self._specData = []
        self._freqs = []
        self._isStarted = False

        self._mapToPitch = lambda freq: math.log(freq / 440.0, 2)

    def start(self):
        if self._isStarted:
            return

        self._isStarted = True
        self.processingThread = Thread(
            name = "Klangfarbe - processing",
            target = self.process
        )
        self.processingThread.start()

    def stop(self):
        self._isStarted = False
        self.processingThread.join()

    def processData(self):
        waveData = self._recorder.getWaveData()
        if len(waveData) <= 0:
            return

        specData = np.abs(fftpack.rfft(waveData))
        freqs = fftpack.rfftfreq(len(waveData)) * self._recorder.RATE

        freqs = map(self._mapToPitch, freqs[20:])
        specData = specData[20:]

        uniqueFreqs = np.unique(freqs)
        summedSpecData = []
        for freq in uniqueFreqs:
            summedSpecData.append(specData[freqs == freq].sum())

        freqs = uniqueFreqs
        specData = np.array(summedSpecData)
        specData = specData / (self._recorder.SIZE * self._recorder.RATE)

        self._specData = specData
        self._freqs = freqs

    def process(self):
        while self._isStarted:
            self.processData()
            time.sleep(0.1)

    def getSpectrumData(self):
        return self._specData, self._freqs
