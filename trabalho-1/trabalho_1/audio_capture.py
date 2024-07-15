# audio_capture.py
import pyaudio
from threading import Thread
from typing import Callable
import structlog
import time

logger = structlog.get_logger(__name__)

class AudioCapture:
    def __init__(self, on_audio_captured: Callable[[bytes], None], rate: int = 44100, chunk: int = 1024) -> None:
        self.on_audio_captured = on_audio_captured
        self.rate = rate
        self.chunk = chunk
        self.format = pyaudio.paInt16
        self.channels = 1
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunk)
        self.thread = Thread(target=self._capture_loop, daemon=True)

    def start_capturing(self):
        self.thread.start()

    def _capture_loop(self):
        while True:
            data = self.stream.read(self.chunk)
            logger.debug("Captured audio data", data_length=len(data))
            self.on_audio_captured(data)
