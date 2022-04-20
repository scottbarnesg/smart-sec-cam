import os
from datetime import datetime
from typing import List, Dict

from smart_sec_cam.video.writer import VideoWriter


class VideoManager:
    VIDEO_FORMATS = {
        "webm": ".webm",
        "mp4": ".mp4"
    }

    def __init__(self, video_dir="data/videos/"):
        self.video_dir = video_dir

    def get_video_filenames(self, video_format: str = "webm") -> List[str]:
        file_names = [filename for filename in self._get_all_filenames() if self._is_video_file(filename, video_format)]
        # Get video timestamps from the filename
        datetimes_to_filenames = {}
        for file_name in file_names:
            try:
                name = self._remove_file_type(file_name, self.VIDEO_FORMATS.get(video_format))
            except ValueError:
                continue
            channel, timestamp_iso = name.split(VideoWriter.FILENAME_DELIM)
            video_timestamp = datetime.fromisoformat(timestamp_iso)
            datetimes_to_filenames.update({video_timestamp: file_name})
        # Return sorted list of video files, with most recent video first
        datetimes = list(datetimes_to_filenames.keys())
        datetimes.sort(reverse=True)
        return [datetimes_to_filenames[key] for key in datetimes]

    def get_video_filenames_by_date(self, video_format: str = "webm") -> Dict[str, List[str]]:
        all_filenames = [filename for filename in self._get_all_filenames() if self._is_video_file(filename, video_format)]
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

    @staticmethod
    def _is_video_file(filename: str, file_type: str) -> bool:
        return file_type in filename

    @staticmethod
    def _remove_file_type(filename: str, file_type: str) -> str:
        if file_type in filename:
            return filename.replace(file_type, "")
        raise ValueError("File is not a supported file type")
