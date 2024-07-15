# audio_player.py
import pyaudio
from threading import Thread
from queue import Queue
import structlog

logger = structlog.get_logger(__name__)

class AudioPlayer:
    def __init__(self, rate: int = 44100, chunk: int = 1024) -> None:
        self.rate = rate
        self.chunk = chunk
        self.format = pyaudio.paInt16
        self.channels = 1
        self.queue = Queue()
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.rate,
                                  output=True,
                                  frames_per_buffer=self.chunk)
        self.thread = Thread(target=self._play_loop, daemon=True)

    def start_playing(self):
        self.thread.start()

    def _play_loop(self):
        while True:
            data = self.queue.get()
            logger.debug("Playing audio data", data_length=len(data))
            self.stream.write(data)

    def add_audio_data(self, data: bytes):
        logger.debug("Received audio data", data_length=len(data))
        self.queue.put(data)

