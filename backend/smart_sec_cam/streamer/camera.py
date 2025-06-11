from typing import Tuple
import cv2
import numpy as np

class UsbCamera:
    def __init__(self, usb_port: int = 0, resolution: Tuple[int, int] = (480, 640), jpeg_quality: int = 70,
                 image_rotation: int = 0):
        self.usb_port = usb_port
        self.resolution = resolution
        self.encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
        self.camera = cv2.VideoCapture(int(self.usb_port))
        self._set_resolution()
        self.image_rotation = image_rotation

    def capture_image(self):
        ret, frame = self.camera.read()
        if not ret:
            raise RuntimeError('Failed to capture image - check camera port value')
        if self.image_rotation:
            frame = self._rotate_image(frame)
        processed_image_data = cv2.imencode('.jpeg', frame, self.encode_params)[1].tobytes()
        return processed_image_data

    def close(self):
        self.camera.release()

    def _set_resolution(self):
        # OpenCV is (height, width), not (width, height)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[1])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[0])

    def _rotate_image(self, frame):
        if self.image_rotation == 90:
            return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        elif self.image_rotation in (-90, 270):
            return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif self.image_rotation == 180:
            return cv2.rotate(frame, cv2.ROTATE_180)
        else:
            print(f"Invalid rotation value: {self.image_rotation}")
            return frame


class RPiCamera:
    def __init__(self, resolution: Tuple[int, int] = (640, 480), jpeg_quality: int = 70, image_rotation: int = 0):
        from picamera2 import Picamera2 # Only import picamera at runtime, since it won't install on other systems

        self.encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
        self.camera = Picamera2()
        config = self.camera.create_preview_configuration(main={"size": resolution, "format": "BGR888"})
        self.camera.configure(config)
        self.camera.start()
        self.image_rotation = image_rotation

    def capture_image(self):
        frame = self.camera.capture_array("main")
        if self.image_rotation:
            frame = self._rotate_image(frame)
        processed_image_data = cv2.imencode('.jpeg', frame, self.encode_params)[1].tobytes()
        return processed_image_data

    def close(self):
        self.camera.stop()
        self.camera.close()

    def _rotate_image(self, frame):
        if self.image_rotation == 90:
            return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        elif self.image_rotation in (-90, 270):
            return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif self.image_rotation == 180:
            return cv2.rotate(frame, cv2.ROTATE_180)
        else:
            print(f"Invalid rotation value: {self.image_rotation}")
            return frame

