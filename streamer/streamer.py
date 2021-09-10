import cv2
import time
import socketio
import socket as sock
from threading import Thread

error = False
new_raw_img = False
new_image = False


class Streamer:
    def __init__(self, capture_delay=0.15, camera_port=0, compression_ratio=0.8, server_url="http://localhost:5000"):
        self.cap_delay = capture_delay
        self.cam_port = camera_port
        self.cam = cv2.VideoCapture(int(self.cam_port)) # Machine dependent
        self.image = self.capture_image()
        print('Source video resolution: ' + str(self.image.shape))
        self.compression(compression_ratio)
        self.image = self.capture_image()
        print('Compressed video resolution: ' + str(self.image.shape))
        self.data = None
        # Socketio for emitter
        self.server_url = server_url
        self.socket = socketio.Client()
        self.hostname = sock.gethostname()

    def capture_image(self, init=False):
        global error
        ret, frame = self.cam.read()
        if not ret:
            if init:
                raise ValueError('Failed to capture image - check camera port value')
            else:
                error = True
                print('Exiting capture thread')
                exit()
        return frame

    def compression(self, compression_ratio):
        width = compression_ratio * self.image.shape[0]
        height = compression_ratio * self.image.shape[1]
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def run(self):
        print('Starting image capture')
        global new_raw_img
        while True:
            self.image = self.capture_image()
            new_raw_img = True
            # print("Got new image")
            time.sleep(self.cap_delay)  # Prevents capture from eating cpu time

    def encode(self):
        print('Starting encoding')
        global error, new_image, new_raw_img
        while not error:
            if new_raw_img:
                self.data = (cv2.imencode('.jpeg', self.image)[1]).tobytes()
                new_image = True
                new_raw_img = False
                # print("Encoded new image")
            else:
                time.sleep(0.01)  # Prevents encoding from eating cpu time
        print('Exiting encoder thread')

    def send_image(self):
        global error, new_image
        self.socket.connect(self.server_url)
        while not error:
            if new_image:
                self.socket.emit("new-image", {'hostname': self.hostname, 'image': self.data})
                new_image = False
                # print("Sent new image")
            else:
                time.sleep(0.01)

    def write(self):
        cv2.imwrite('image.jpeg', streamer.image)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--server_url', help='Server to stream images to', default='http://localhost:5000')
    args = parser.parse_args()
    # Setup streamer and start threads
    streamer = Streamer(server_url=args.server_url)
    captureThread = Thread(target=streamer.run)
    encoderThread = Thread(target=streamer.encode)
    senderThread = Thread(target=streamer.send_image)
    captureThread.start()
    encoderThread.start()
    senderThread.start()
