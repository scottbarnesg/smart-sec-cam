from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socket = SocketIO(app)


# Sent from cameras, with a new image
@socket.on("new-image")
def get_image(image):
    pass


if __name__ == '__main__':
    socket.run(app, host='0.0.0.0')
