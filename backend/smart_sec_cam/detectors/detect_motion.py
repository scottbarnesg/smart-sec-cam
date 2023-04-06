import os
import time

from smart_sec_cam.detectors.motion import MotionDetector
from smart_sec_cam.redis import RedisImageReceiver


CHANNEL_LIST_INTERVAL = 10
SLEEP_TIME = 0.01


def main(redis_url: str, redis_port: int, video_dir: str, motion_threshold: int):
    # Fetch list of channels
    # Subscribe to each channel to get frames
    image_receiver = RedisImageReceiver(redis_url, redis_port)
    active_channels = image_receiver.get_all_channels()
    last_channel_check_time = time.monotonic()
    image_receiver.set_channels(active_channels)
    image_receiver.start_listener_thread()
    # Create and start MotionDetection instance for each channel
    motion_detectors = {channel: MotionDetector(channel, motion_threshold=motion_threshold, video_dir=video_dir)
                        for channel in active_channels}
    for detector in motion_detectors.values():
        detector.run_in_background()
    while True:
        # Check for new frames from each channel and push to the corresponding MotionDetection instance
        if image_receiver.has_message():
            message = image_receiver.get_message()
            frame = message.get("data")
            channel = message.get("channel").decode("utf-8")
            motion_detectors.get(channel).add_frame(frame)
        else:
            time.sleep(SLEEP_TIME)
        # Periodically check for updated channel list in background thread
        if time.monotonic() - last_channel_check_time > CHANNEL_LIST_INTERVAL:
            active_channels = image_receiver.get_all_channels()
            # Check for new channels
            new_channels = []
            for channel in active_channels:
                if channel not in motion_detectors.keys():
                    print(f"Detected new channel: {channel}")
                    new_channels.append(channel)
                    motion_detectors[channel] = MotionDetector(channel,
                                                               motion_threshold=motion_threshold,
                                                               video_dir=video_dir)
            # Check for removed channels
            removed_channels = []
            for channel in motion_detectors.keys():
                if channel not in active_channels:
                    print(f"Removing channel: {channel}")
                    removed_channels.append(channel)
                    motion_detectors.get(channel).stop()
                    del motion_detectors[channel]
            # If the active channel list changed, update the redis subscription list
            if new_channels or removed_channels:
                image_receiver.set_channels(active_channels)
            last_channel_check_time = time.monotonic()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--redis-url', help='Server address to stream images to', type=str, default='localhost')
    parser.add_argument('--redis-port', help='Server port to stream images to', type=int, default=6379)
    parser.add_argument('--video-dir', help='Directory in which video files are stored', type=str,
                        default="data/videos")
    args = parser.parse_args()

    motion_threshold = int(os.environ.get("MOTION_THRESHOLD"))

    main(args.redis_url, args.redis_port, args.video_dir, motion_threshold)