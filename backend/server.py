from flask import Flask, send_file
from flask_socketio import SocketIO
import cv2
import numpy as np
import io
import eventlet
from engineio.payload import Payload

Payload.max_decode_packets = 500
eventlet.monkey_patch()

app = Flask(__name__)
socket = SocketIO(app, cors_allowed_origins="*")
img_data = None


# Sent from cameras, with a new image
@socket.on("new-image")
def get_image(data):
    global img_data
    # print("Got new image")
    # print(data['hostname'])
    # socket.emit('image', data, room=data['hostname']) # TODO: Create room from hostname
    socket.emit('image', {'data': data['image']})
    img_data = data['image']


@app.route("/image.jpeg", methods=["GET"])
def get_image():
    global img_data
    return send_file(
        io.BytesIO(img_data),
        mimetype='image/jpeg',
        as_attachment=True,
        attachment_filename='image.jpg')


if __name__ == '__main__':
    socket.run(app, host='0.0.0.0')
