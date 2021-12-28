import queue
import time
import socket
from threading import Thread

import cv2

from redis_image_sender import RedisImageSender


shutdown = False

IMAGE_QUALITY = 70


class Streamer:
    def __init__(self, server_address: str, server_port: int, capture_delay: float = 0.15, camera_port: int = 0,
                 compression_ratio: float = 1.0):
        self.cap_delay = capture_delay
        self.cam = cv2.VideoCapture(int(camera_port))  # Machine dependent
        # Set video resolution
        self._set_video_resolution(compression_ratio)
        # Image data queues
        self.raw_image_queue = queue.Queue()
        self.ready_image_queue = queue.Queue()
        # Image sending client
        self.server_address = server_address
        self.server_port = int(server_port)
        self.image_sender = RedisImageSender(socket.gethostname(), self.server_address, self.server_port)

    def _set_video_resolution(self, compression_ratio: float):
        # Capture initial image
        image = self.capture_image()
        print('Source video resolution: ' + str(image.shape))
        # Get scaled-down resolution
        width = compression_ratio * image.shape[0]
        height = compression_ratio * image.shape[1]
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        # Capture a second image and verify it worked
        image = self.capture_image()
        print('Compressed video resolution: ' + str(image.shape))

    def capture_image(self):
        global shutdown
        ret, frame = self.cam.read()
        if not ret:
            shutdown = True
            raise RuntimeError('Failed to capture image - check camera port value')
        return frame

    def run(self):
        global shutdown
        print('Starting image capture thread')
        while not shutdown:
            self.raw_image_queue.put(self.capture_image())
            time.sleep(self.cap_delay)  # Prevents capture from eating cpu time
        print('Exited image capture thread')

    def encode_images(self):
        global shutdown
        print('Starting encoding thread')
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), IMAGE_QUALITY]
        while not shutdown:
            raw_image = self.raw_image_queue.get()
            processed_image_data = (cv2.imencode('.jpeg', raw_image, encode_params)[1]).tobytes()
            self.ready_image_queue.put(processed_image_data)
        print('Exiting encoder thread')

    def send_images(self):
        global shutdown
        print("Started image sending thread.")
        while not shutdown:
            image_data = self.ready_image_queue.get()
            try:
                self.image_sender.send_message(image_data)
            except ConnectionError:
                print("Caught connection error to server, trying to reconnect...")
                time.sleep(1)
                self.reconnect()
        print("Exited image sending thread")

    def reconnect(self):
        self.image_sender = RedisImageSender(socket.gethostname(), self.server_address, self.server_port)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--redis-url', help='Server address to stream images to', default='localhost')
    parser.add_argument('--redis-port', help='Server port to stream images to', default=6380)
    args = parser.parse_args()
    # Setup streamer and start threads
    streamer = Streamer(args.redis_url, args.redis_port)
    captureThread = Thread(target=streamer.run)
    encoderThread = Thread(target=streamer.encode_images)
    senderThread = Thread(target=streamer.send_images)
    captureThread.start()
    encoderThread.start()
    senderThread.start()
