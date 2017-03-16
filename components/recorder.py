from threading import Thread
import numpy as np
import pyaudio as pa

class Recorder:
    def __init__(self, size, channels, rate, interval):
        self.SIZE = size
        self.CHANNELS = channels
        self.RATE = rate
        self.INTERVAL = min([interval, 1])
        self.FORMAT = pa.paInt16

        self._audioWaveData = []
        self._isStarted = False

    def record(self):
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
            self._audioWaveData = np.fromstring(
                self._audioStream.read(self.SIZE),
                dtype = np.int16
            )

    def start(self):
        if self._isStarted:
            return

        self._isStarted = True
        self.record()
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

    def getWaveData(self):
        return self._audioWaveData
