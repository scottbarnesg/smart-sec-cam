import cv2
import time
import socketio
import socket as sock
from threading import Thread

# Global variables
error = False
new_raw_img = False
new_image = False

IMAGE_QUALITY = 60

socketio_client = socketio.Client()


class Streamer:
    def __init__(self, capture_delay=0.1, camera_port=0, compression_ratio=1.0, server_url="http://localhost:5000"):
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
                encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), IMAGE_QUALITY]
                self.data = (cv2.imencode('.jpeg', self.image, encode_params)[1]).tobytes()
                new_image = True
                new_raw_img = False
            else:
                time.sleep(0.01)  # Prevents encoding from eating cpu time
        print('Exiting encoder thread')

    def send_image(self):
        global error, new_image
        socketio_client.connect(self.server_url)
        while not error:
            if new_image:
                try:
                    socketio_client.emit("new-image", {'hostname': self.hostname, 'image': self.data})
                    new_image = False
                except socketio.exceptions.BadNamespaceError as e:
                    print("Caught socketio exception: " + str(e))
                    socketio_client.disconnect()
                    socketio_client.connect(self.server_url)
            else:
                time.sleep(0.01)

    def reconnect(self):
        socketio_client.disconnect()
        socketio_client.connect(self.server_url)

    @socketio_client.on('error')
    def handle_error(self):
        print("Got error message from server, reconnecting...")
        self.reconnect()

    def write(self):
        cv2.imwrite('image.jpeg', self.image)


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
