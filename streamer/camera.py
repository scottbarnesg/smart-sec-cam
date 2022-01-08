from typing import Tuple

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
