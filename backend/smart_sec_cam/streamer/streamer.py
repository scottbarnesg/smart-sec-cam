import queue
import time
import socket
from threading import Thread

import redis.exceptions

from camera import UsbCamera, RPiCamera
from smart_sec_cam.redis import RedisImageSender


shutdown = False


class Streamer:
    def __init__(self, server_address: str, server_port: int, capture_delay: float = 0.1, camera_port: int = 0,
                 use_pi_camera: bool = False, image_rotation: int = 0):
        self.cap_delay = capture_delay
        if use_pi_camera:
            self.camera = RPiCamera(image_rotation=image_rotation)
        else:
            self.camera = UsbCamera(camera_port, image_rotation=image_rotation)
        # Image data queues
        self.image_queue = queue.Queue(maxsize=int(5.0/capture_delay))  # Only queue 5 seconds of video
        # Image sending client
        self.server_address = server_address
        self.server_port = int(server_port)
        self.image_sender = RedisImageSender(socket.gethostname(), self.server_address, self.server_port)

    def capture_images(self):
        global shutdown
        print('Starting image capture thread')
        while not shutdown:
            try:
                self.image_queue.put(self.camera.capture_image())
                time.sleep(self.cap_delay)  # Prevents capture from eating cpu time
            except RuntimeError as e:
                print(e)
                shutdown = True
                break
        self.camera.close()
        print('Exited image capture thread')

    def send_images(self):
        global shutdown
        print("Started image sending thread.")
        while not shutdown:
            image_data = self.image_queue.get()
            try:
                self.image_sender.send_message(image_data)
            except redis.exceptions.ConnectionError:
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
    parser.add_argument('--pi-cam', help="Use Raspberry Pi camera module", action='store_true')
    parser.add_argument('--rotation', help="Angle to rotate image to", default=0)
    parser.add_argument('--capture-delay', help="Delay between capturing a new frame", default=0.1)
    args = parser.parse_args()
    # Setup streamer and start threads
    streamer = Streamer(args.redis_url,
                        args.redis_port,
                        use_pi_camera=args.pi_cam,
                        image_rotation=args.rotation,
                        capture_delay=args.capture_delay)
    captureThread = Thread(target=streamer.capture_images)
    senderThread = Thread(target=streamer.send_images)
    captureThread.start()
    senderThread.start()
