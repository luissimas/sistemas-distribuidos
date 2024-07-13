from threading import Thread
from time import sleep
from typing import Callable

import cv2
from PIL import Image


class VideoCapture:
    """A video capture device."""

    def __init__(
        self,
        on_frame_captured: Callable[[Image.Image], None],
        device: int = 0,
    ) -> None:
        self.capture = cv2.VideoCapture(device)
        self.on_frame_captured = on_frame_captured
        self.thread = Thread(target=self._capture_loop, daemon=True)

    def start_capturing(self):
        """Starts a background thread to capture frames."""
        self.thread.start()

    def _capture_loop(self) -> Image.Image:
        while True:
            _, frame = self.capture.read()
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            self.on_frame_captured(Image.fromarray(image))
            sleep(0.03)
