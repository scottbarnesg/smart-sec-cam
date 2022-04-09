import datetime
import os
import time
from typing import Tuple

import cv2
import ffmpeg


class VideoWriter:
    FILENAME_DELIM = "__"

    def __init__(self, channel: str, path="data/videos/", filetype: str = ".mp4",
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
        fps = self._calculate_fps()
        ffpmeg_process = (
            ffmpeg
                .input('pipe:',
                       format='rawvideo',
                       pix_fmt='rgb24',
                       framerate=fps,
                       s='{}x{}'.format(self.resolution[0], self.resolution[1]))
                .output(self.full_filepath)
                .overwrite_output()
                .run_async(pipe_stdin=True)
        )
        for frame in self.frame_buffer:
            ffpmeg_process.stdin.write(frame)

    def _calculate_fps(self) -> int:
        elapsed_time = time.monotonic() - self.first_frame_time
        return int(len(self.frame_buffer) / elapsed_time)
