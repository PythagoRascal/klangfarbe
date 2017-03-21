#!/usr/bin/python -u

import signal, sys
from threading import Thread
import numpy as np
import pyaudio as pa

class Recorder:
    def __init__(self, size, channels, rate):
        self.SIZE = size
        self.CHANNELS = channels
        self.RATE = rate
        self.FORMAT = pa.paInt16

        self.streamCallback = None
        self._audioWaveData = []
        self._isStarted = False

    def open(self):
        self._audioHandle = pa.PyAudio()
        self._audioStream = self._audioHandle.open(
            format = self.FORMAT,
            channels = self.CHANNELS,
            rate = self.RATE,
            input = True,
            frames_per_buffer = self.SIZE
        )

    def stream(self):
        while self._isStarted:
            self._audioWaveData = self._audioStream.read(self.SIZE)
            if self.streamCallback != None:
                self.streamCallback(self._audioWaveData)

    def start(self):
        if self._isStarted:
            return

        self._isStarted = True
        self.open()
        self._streamingThread = Thread(
            name = "Klangfarbe - recording",
            target = self.stream
        )
        self._streamingThread.start()

    def stop(self):
        self._isStarted = False
        self._streamingThread.join()
        self._audioStream.close()
        self._audioHandle.terminate()

    def setStreamCallback(self, callback):
        self.streamCallback = callback;

    def getWaveData(self):
        return self._audioWaveData

SIZE = 2**11
CHANNELS = 1
RATE = 24000
#INTERVAL = 0.1

def stream_callback(data):
    print data

recorder = Recorder(SIZE, CHANNELS, RATE)
recorder.setStreamCallback(stream_callback)
recorder.start()

def sigterm_handler(signal, frame):
    recorder.stop()
    sys.exit(0)
signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGINT, sigterm_handler)
