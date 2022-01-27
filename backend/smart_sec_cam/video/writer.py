import datetime
import os
import time
from typing import Tuple

import cv2


class VideoWriter:
    FILENAME_DELIM = "__"

    def __init__(self, channel: str, path="data/videos/", filetype: str = ".webm",
                 resolution: Tuple[int, int] = (640, 480)):
        date = datetime.datetime.now()
        filename = channel + self.FILENAME_DELIM + date.isoformat() + filetype
        self.full_filepath = os.path.join(path, filename)
        self._make_target_dir(path)
        self.resolution = resolution
        self.frame_buffer = []
        self.first_frame_time = time.monotonic()

    @staticmethod
    def _make_target_dir(path: str):
        if not os.path.exists(path):
            os.makedirs(path)

    def add_frame(self, frame):
        resized_frame = cv2.resize(frame, self.resolution)
        if not self.frame_buffer:
            self.first_frame_time = time.monotonic()
        self.frame_buffer.append(resized_frame)

    def write(self):
        print("Writing video to: " + self.full_filepath + " ...")
        fourcc = cv2.VideoWriter_fourcc(*'VP90')
        fps = self._calculate_fps()
        writer = cv2.VideoWriter(self.full_filepath, fourcc, fps, self.resolution)
        for frame in self.frame_buffer:
            writer.write(frame)

    def release(self):
        self.writer.release()

    def _calculate_fps(self) -> int:
        elapsed_time = time.monotonic() - self.first_frame_time
        return int(len(self.frame_buffer) / elapsed_time)
