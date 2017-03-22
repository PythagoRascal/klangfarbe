#!/usr/bin/python -u
import sys, math, colorsys
import signal as sig
from threading import Thread
from datetime import datetime as dt
from scipy import fftpack, signal
import numpy as np

class Processor:
    def __init__(self,
                 size = 2**12,
                 channels = 1,
                 rate = 48000,
                 bufferlen = 50,
                 interval = 0.1,
                 preCutoff = 1,
                 postCutoff = 0,
                 outputSize = 360):
        self.SIZE = size
        self.CHANNELS = channels
        self.RATE = rate
        self.BUFFERLEN = bufferlen
        self.INTERVAL = interval
        self.PRE_CUTOFF = preCutoff
        self.POST_CUTOFF = postCutoff if postCutoff < 0 else None
        self.OUTPUT_SIZE = outputSize

        self._isStarted = False
        self._waveDataBuffer = []
        self._mapFreqToPitch = lambda freq: math.log(freq / 440.0, 2)

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

        specData = np.abs(fftpack.rfft(waveData))[self.PRE_CUTOFF : self.POST_CUTOFF]
        freqs = (fftpack.rfftfreq(len(waveData)) * self.RATE)[self.PRE_CUTOFF : self.POST_CUTOFF]
        freqs = np.array(map(self._mapFreqToPitch, freqs))
        freqs = np.rint((freqs - min(freqs)) / (max(freqs) - min(freqs)) * (self.OUTPUT_SIZE - 1))

        summedSpecData = []
        uniqueFreqs = np.unique(freqs)
        for idx, freq in enumerate(uniqueFreqs):
            summedSpecData.append(specData[freqs == freq].sum())

        summedSpecData = np.rint(
            (summedSpecData - min(summedSpecData))
            / (max(summedSpecData) - min(summedSpecData))
            * 255
        )
	
	#print [x for x in summedSpecData]

        sys.stdout.write(summedSpecData.astype(np.int8).tobytes())
	#self.stop()

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
PRE_CUTOFF = 20
POST_CUTOFF = -228
OUTPUT_SIZE = 30

processor = Processor(
    size = SIZE,
    rate = RATE,
    bufferlen = BUFFERLEN,
    interval = INTERVAL,
    preCutoff = PRE_CUTOFF,
    postCutoff = POST_CUTOFF,
    outputSize = OUTPUT_SIZE
)
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
