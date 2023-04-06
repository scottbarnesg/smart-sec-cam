import queue
import threading
import time
from typing import List

import cv2
import imutils
import numpy as np

from smart_sec_cam.video.writer import VideoWriter


class MotionDetector:
    def __init__(self, channel_name: str, motion_threshold: int = 10000, video_duration_seconds: int = 10,
                 video_dir: str = "data/videos"):
        self.channel_name = channel_name
        self.motion_threshold = motion_threshold
        self.video_duration = video_duration_seconds
        self.video_dir = video_dir
        self.video_writer = VideoWriter(self.channel_name, path=self.video_dir)
        self.frame_queue = queue.Queue()
        self.detection_thread = threading.Thread(target=self.run, daemon=True)
        self.shutdown = False

    def add_frame(self, frame: bytes):
        self.frame_queue.put(frame)

    def run(self):
        last_frame = None
        last_frame_greyscale = None
        recorded_video = False
        while not self.shutdown:
            decoded_frame_greyscale = self._get_decoded_frame(greyscale=True)
            decoded_frame = self._get_decoded_frame()
            if last_frame is not None:
                if self._detect_motion(last_frame_greyscale, decoded_frame_greyscale):
                    print("Detected motion for channel: " + self.channel_name)
                    self._record_video([last_frame, decoded_frame])
                    recorded_video = True
            # Set current frame to last frame
            if not recorded_video:
                last_frame = decoded_frame
                last_frame_greyscale = decoded_frame_greyscale
            else:
                print("Done recording video for channel: " + str(self.channel_name))
                last_frame = None
                last_frame_greyscale = None
                recorded_video = False

    def run_in_background(self):
        self.detection_thread.start()

    def stop(self):
        self.shutdown = True

    def _has_decoded_frame(self) -> bool:
        return not self.frame_queue.empty()

    def _get_decoded_frame(self, greyscale=False):
        new_frame = self.frame_queue.get()
        if greyscale:
            return self._decode_frame_greyscale(new_frame)
        else:
            return self._decode_frame(new_frame)

    def _detect_motion(self, old_frame_greyscale, new_frame_greyscale) -> bool:
        """
        Detection motion between two frames using contours.
        Returns a boolean indicating if the difference exceeds the motion threshold
        """
        if old_frame_greyscale is None:
            return False
        # Calculate background subtraction
        frame_delta = cv2.absdiff(old_frame_greyscale, new_frame_greyscale)
        # Calculate and dilate threshold
        threshold = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        threshold = cv2.dilate(threshold, None, iterations=2)
        # Extract contours from the threshold image
        contours = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        # Iterate over contours and determine if any are large enough to count as motion
        for contour in contours:
            if cv2.contourArea(contour) >= self.motion_threshold:
                return True
        return False

    def _draw_motion_areas_on_frame(self, old_frame, new_frame):
        if old_frame is None:
            return new_frame
        # Convert frames to greyscale
        old_frame_greyscale = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
        new_frame_greyscale = cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)
        # Calculate background subtraction
        frame_delta = cv2.absdiff(old_frame_greyscale, new_frame_greyscale)
        # Calculate and dilate threshold
        threshold = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        threshold = cv2.dilate(threshold, None, iterations=2)
        # Extract contours from the threshold image
        contours = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        # Iterate over contours and determine if any are large enough to count as motion
        modified_frame = new_frame.copy()
        for contour in contours:
            if cv2.contourArea(contour) >= self.motion_threshold:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(modified_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return modified_frame

    def _record_video(self, first_frames: List):
        start_time = time.monotonic()
        self.video_writer.reset()
        old_frame = None
        for frame in first_frames:
            self.video_writer.add_frame(frame)
            old_frame = frame
        while not self._done_recording_video(start_time):
            if self._has_decoded_frame():
                new_frame = self._get_decoded_frame()
                new_frame_with_motion_area = self._draw_motion_areas_on_frame(old_frame, new_frame)
                self.video_writer.add_frame(new_frame_with_motion_area)
                old_frame = new_frame
            else:
                time.sleep(0.01)
        self.video_writer.write()

    def _done_recording_video(self, start_time: float) -> bool:
        return time.monotonic() - start_time > self.video_duration

    @staticmethod
    def _decode_frame(frame: bytes):
        return cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), cv2.IMREAD_COLOR)

    @staticmethod
    def _decode_frame_greyscale(frame: bytes):
        # Convert frame to greyscale and blur it
        greyscale_frame = cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        return cv2.GaussianBlur(greyscale_frame, (21, 21), 0)
