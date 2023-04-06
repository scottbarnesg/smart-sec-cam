import queue
import threading
import time

import cv2
import numpy as np

from smart_sec_cam.video.writer import VideoWriter


class FaceDetector:
    scale_factor = 1.05
    min_neighbors = 16

    def __init__(self, channel_name: str, video_duration_seconds: int = 10, video_dir: str = "data/videos"):
        self.channel_name = channel_name
        self.video_duration = video_duration_seconds
        self.video_dir = video_dir
        self.video_writer = VideoWriter(self.channel_name, path=self.video_dir)
        self.frame_queue = queue.Queue()
        self.face_detector = cv2.CascadeClassifier('smart_sec_cam/detectors/haarcascade_frontalface_default.xml')
        self.detection_thread = threading.Thread(target=self.run, daemon=True)
        self.shutdown = False

    def add_frame(self, frame: bytes):
        self.frame_queue.put(frame)

    def run(self):
        while not self.shutdown:
            # Get latest frame
            decoded_frame_greyscale = self._get_decoded_frame(greyscale=True)
            decoded_frame = self._get_decoded_frame()
            # Check for faces
            faces = self.face_detector.detectMultiScale(decoded_frame_greyscale, self.scale_factor, self.min_neighbors)
            if len(faces) != 0:
                print(f"Detected face for {self.channel_name}")
                self._record_video(decoded_frame, faces)

    def _get_decoded_frame(self, greyscale=False):
        new_frame = self.frame_queue.get()
        if greyscale:
            return self._decode_frame_greyscale(new_frame)
        else:
            return self._decode_frame(new_frame)

    @staticmethod
    def _decode_frame(frame: bytes):
        return cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), cv2.IMREAD_COLOR)

    @staticmethod
    def _decode_frame_greyscale(frame: bytes):
        # Convert frame to greyscale and blur it
        greyscale_frame = cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        return cv2.GaussianBlur(greyscale_frame, (21, 21), 0)

    def _record_video(self, first_frame, first_frame_faces):
        start_time = time.monotonic()
        self.video_writer.reset()
        # Add first frame to video writer
        first_frame_with_face = self._draw_face_on_frame(first_frame, first_frame_faces)
        self.video_writer.add_frame(first_frame_with_face)
        while not self._done_recording_video(start_time):
            if self._has_decoded_frame():
                new_frame = self._get_decoded_frame()
                new_frame_greyscale = self._get_decoded_frame(greyscale=True)
                faces = self.face_detector.detectMultiScale(new_frame_greyscale, self.scale_factor, self.min_neighbors)
                new_frame_with_face = self._draw_face_on_frame(new_frame, faces)
                self.video_writer.add_frame(new_frame_with_face)
            else:
                time.sleep(0.01)
        self.video_writer.write()

    def _done_recording_video(self, start_time: float) -> bool:
        return time.monotonic() - start_time > self.video_duration

    def _has_decoded_frame(self) -> bool:
        return not self.frame_queue.empty()

    @staticmethod
    def _draw_face_on_frame(frame, faces):
        modified_frame = frame.copy()
        for (x, y, w, h) in faces:
            cv2.rectangle(modified_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        return modified_frame

    def run_in_background(self):
        self.detection_thread.start()




