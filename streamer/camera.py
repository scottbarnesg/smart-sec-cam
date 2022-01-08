from typing import Tuple
from io import BytesIO

import cv2


class UsbCamera:
    def __init__(self, usb_port: int = 0, resolution: Tuple[int, int] = (480, 640)):
        self.usb_port = usb_port
        self.resolution = resolution
        self.camera = cv2.VideoCapture(int(self.usb_port))
        self._set_resolution()

    def capture_image(self):
        ret, frame = self.camera.read()
        if not ret:
            raise RuntimeError('Failed to capture image - check camera port value')
        return frame

    def close(self):
        self.camera.release()

    def _set_resolution(self):
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        image = self.capture_image()
        print("Video resolution: " + str(image.shape))


class RPiCamera:
    def __init__(self):
        from picamera import PiCamera  # Only import picamera at runtime, since it won't install on other systems
        self.camera = PiCamera()

    def capture_image(self):
        stream = BytesIO()
        self.camera.capture(stream, format='bgr')
        return stream

    def close(self):
        self.camera.release()

