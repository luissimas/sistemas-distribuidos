import cv2
from PIL import Image


class VideoCapture:
    """A video capture device."""

    def __init__(self, device: int = 0) -> None:
        self.capture = cv2.VideoCapture(device)

    def capture_frame(self) -> Image.Image:
        """Capture a video frame as an image."""
        _, frame = self.capture.read()
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        return Image.fromarray(image)
