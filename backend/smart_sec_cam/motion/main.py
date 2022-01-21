from smart_sec_cam.motion.detection import MotionDetector
from smart_sec_cam.redis import RedisImageReceiver


def main(redis_url: str, redis_port: int):
    # Fetch list of channels
    # Subscribe to each channel to get frames
    image_receiver = RedisImageReceiver(redis_url, redis_port)
    active_channels = image_receiver.get_all_channels()
    image_receiver.set_channels(active_channels)
    image_receiver.start_listener_thread()
    # Create and start MotionDetection instance for each channel
    motion_detectors = {channel: MotionDetector(channel) for channel in active_channels}
    for detector in motion_detectors.values():
        detector.run_in_background()
    print(motion_detectors)
    while True:
        # Check for new frames from each channel and push to the corresponding MotionDetection instance
        message = image_receiver.get_message()
        frame = message.get("data")
        channel = message.get("channel").decode("utf-8")
        motion_detectors.get(channel).add_frame(frame)
        # TODO: Periodically check for updated channel list in background thread
    # Shut down detector threads
    for detector in motion_detectors.values():
        detector.stop()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--redis-url', help='Server address to stream images to', default='localhost')
    parser.add_argument('--redis-port', help='Server port to stream images to', default=6379)

    args = parser.parse_args()

    main(args.redis_url, args.redis_port)
