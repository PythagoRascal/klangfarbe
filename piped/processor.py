#!/usr/bin/python -u
import sys, math
import signal as sig
from threading import Thread
from datetime import datetime as dt
from scipy import fftpack, signal
import numpy as np

class Processor:
    def __init__(self, size, channels, rate, bufferlen, interval):
        self.SIZE = size
        self.CHANNELS = channels
        self.RATE = rate
        self.BUFFERLEN = bufferlen
        self.INTERVAL = interval

        self._isStarted = False
        self._waveDataBuffer = []
        self._mapToPitch = lambda freq: math.log(freq / 440.0, 2)

    def start(self):
        if self._isStarted:
            return

        self._isStarted = True
        self._processingThread = Thread(
            name = "Klangfarbe - processing",
            target = self.stream
        )
        self._processingThread.start()

    def stop(self):
        self._isStarted = False
        self._processingThread.join()

    def collect(self, data):
        if len(self._waveDataBuffer) >= self.BUFFERLEN:
            self._waveDataBuffer.pop(0)

        self._waveDataBuffer.append(
            np.fromstring(data, dtype = np.int16)
        )

    def process(self):
        waveData = np.sum(np.array(self._waveDataBuffer), axis = 0) / self.BUFFERLEN

        specData = np.abs(fftpack.rfft(waveData))
        freqs = fftpack.rfftfreq(len(waveData)) * self.RATE

        print freqs[0], freqs[-1], (freqs[-1] - freqs[0]), (freqs[-1] - freqs[0]) / 30.0

        specData = specData[20:]
        freqs = map(self._mapToPitch, freqs[20:])

        summedSpecData = []
        uniqueFreqs = np.unique(freqs)
        for idx, freq in enumerate(uniqueFreqs):
            summedSpecData.append(specData[freqs == freq].sum())

        freqs = uniqueFreqs
        specData = np.array(summedSpecData) / (self.SIZE * self.RATE)

    def stream(self):
        last = dt.now()
        while self._isStarted:
            diff = (dt.now() - last).microseconds / 1000
            if len(self._waveDataBuffer) < self.BUFFERLEN:
                continue
            if diff < (self.INTERVAL * 1000):
                continue

            self.process()
            last = dt.now()

SIZE = 2**11
CHANNELS = 1
RATE = 24000
BUFFERLEN = 50
INTERVAL = 0.1

processor = Processor(SIZE, CHANNELS, RATE, BUFFERLEN, INTERVAL)
processor.start()

def sigterm_handler(signum, frame):
    processor.stop()
    sys.exit(0)
sig.signal(sig.SIGTERM, sigterm_handler)
sig.signal(sig.SIGINT, sigterm_handler)

while True:
    line = sys.stdin.read(SIZE * 2) # Twice SIZE because 16bit chars
    if line == "\n":
        break
    processor.collect(line)
