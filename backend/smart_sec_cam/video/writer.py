import datetime
import os
from typing import Tuple

import cv2


class VideoWriter:
    FILENAME_DELIM = "__"

    def __init__(self, channel: str, path="data/videos/", filetype: str = ".mp4", fps: int = 10,
                 resolution: Tuple[int, int] = (640, 480)):
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        date = datetime.datetime.now()
        filename = channel + self.FILENAME_DELIM + date.isoformat() + filetype
        full_filepath = os.path.join(path, filename)
        self.writer = cv2.VideoWriter(full_filepath, fourcc, fps, resolution)
        self._make_target_dir(path)
        self.resolution = resolution
        print("Writing video to: " + full_filepath + " ...")

    @staticmethod
    def _make_target_dir(path: str):
        if not os.path.exists(path):
            os.makedirs(path)

    def add_frame(self, frame):
        resized_frame = cv2.resize(frame, self.resolution)
        self.writer.write(resized_frame)

    def release(self):
        self.writer.release()
