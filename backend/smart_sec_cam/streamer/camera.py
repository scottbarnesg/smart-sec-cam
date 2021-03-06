from typing import Tuple

import cv2
import numpy as np


class UsbCamera:
    def __init__(self, usb_port: int = 0, resolution: Tuple[int, int] = (640, 480), jpeg_quality: int = 70):
        self.usb_port = usb_port
        self.resolution = resolution
        self.encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
        self.camera = cv2.VideoCapture(int(self.usb_port))
        self._set_resolution()

    def capture_image(self):
        ret, frame = self.camera.read()
        if not ret:
            raise RuntimeError('Failed to capture image - check camera port value')
        processed_image_data = (cv2.imencode('.jpeg', frame, self.encode_params)[1]).tobytes()
        return processed_image_data

    def close(self):
        self.camera.release()

    def _set_resolution(self):
        # OpenCV is (height, width), not (width, height)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[1])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[0])


class RPiCamera:
    def __init__(self, resolution: Tuple[int, int] = (640, 480), jpeg_quality: int = 70, image_rotation: int = 0):
        from picamera import PiCamera  # Only import picamera at runtime, since it won't install on other systems

        self.encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
        self.camera = PiCamera()
        self._set_resolution(resolution)
        self._set_rotation(image_rotation)

    def capture_image(self):
        frame = np.empty((self.camera.resolution[1], self.camera.resolution[0], 3), dtype=np.uint8)
        self.camera.capture(frame, format='bgr', use_video_port=True)
        processed_image_data = (cv2.imencode('.jpeg', frame, self.encode_params)[1]).tobytes()
        return processed_image_data

    def close(self):
        self.camera.release()

    def _set_resolution(self, resolution: Tuple[int, int]):
        self.camera.resolution = resolution

    def _set_rotation(self, rotation: int):
        self.camera.rotation = rotation

