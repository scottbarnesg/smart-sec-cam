import os
from typing import List, Dict

from smart_sec_cam.video.writer import VideoWriter


class VideoManager:
    FILE_TYPES = [".mp4"]

    def __init__(self, video_dir="data/videos/"):
        self.video_dir = video_dir

    def get_video_filenames(self) -> List[str]:
        return [filename for filename in self._get_all_filenames() if self._is_video_file(filename)]

    def get_video_filenames_by_date(self) -> Dict[str, List[str]]:
        all_filenames = self._get_all_filenames()
        filenames_by_date = {}
        for filename in all_filenames:
            try:
                name = self._remove_file_type(filename)
            except ValueError:
                continue
            channel, timestamp_iso = name.split(VideoWriter.FILENAME_DELIM)
            date = timestamp_iso.split("T")[0]
            if date not in filenames_by_date.keys():
                filenames_by_date[date] = []
            filenames_by_date[date].append(filename)
        return filenames_by_date

    def _get_all_filenames(self) -> List[str]:
        return os.listdir(self.video_dir)

    def _is_video_file(self, filename: str) -> bool:
        return any(file_type in filename for file_type in self.FILE_TYPES)

    def _remove_file_type(self, filename: str) -> str:
        for file_type in self.FILE_TYPES:
            if file_type in filename:
                return filename.replace(file_type, "")
        raise ValueError("File is not a supported file type")
