import queue
import threading
import time
from typing import List

import cv2
import numpy as np

from smart_sec_cam.video.writer import VideoWriter


class MotionDetector:
    def __init__(self, channel_name: str, motion_threshold: int = 1.5e6, video_duration: int = 10):
        self.channel_name = channel_name
        self.motion_threshold = motion_threshold
        self.video_duration = video_duration
        self.frame_queue = queue.Queue()
        self.detection_thread = threading.Thread(target=self.run, daemon=True)
        self.shutdown = False

    def add_frame(self, frame: bytes):
        self.frame_queue.put(frame)

    def run(self):
        last_frame = None
        recorded_video = False
        while not self.shutdown:
            decoded_frame = self._get_decoded_frame()
            if last_frame is not None:
                if self._detect_motion(last_frame, decoded_frame):
                    print("Detected motion for channel: " + self.channel_name)
                    self._record_video([last_frame, decoded_frame])
                    recorded_video = True
            # Set current frame to last frame
            if not recorded_video:
                last_frame = decoded_frame
            else:
                last_frame = None
                recorded_video = False

    def run_in_background(self):
        self.detection_thread.start()

    def stop(self):
        self.shutdown = True

    def _get_decoded_frame(self):
        new_frame = self.frame_queue.get()
        return self._decode_frame(new_frame)

    def _detect_motion(self, old_frame, new_frame) -> bool:
        """
        Performs background subtraction on the frames.
        Returns a boolean indicating if the difference exceeds the motion threshold
        """
        print(np.sum(cv2.subtract(new_frame, old_frame).flatten()))
        return np.sum(cv2.subtract(new_frame, old_frame).flatten()) > self.motion_threshold

    def _record_video(self, first_frames: List):
        start_time = time.monotonic()
        video_writer = VideoWriter(self.channel_name)
        for frame in first_frames:
            print(str(frame.shape))
            video_writer.add_frame(frame)
        while not self._done_recording_video(start_time):
            new_frame = self._get_decoded_frame()
            video_writer.add_frame(new_frame)
        video_writer.release()

    def _done_recording_video(self, start_time: float) -> bool:
        return time.monotonic() - start_time > self.video_duration

    @staticmethod
    def _decode_frame(frame: bytes):
        return cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), cv2.IMREAD_COLOR)
