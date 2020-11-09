from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socket = SocketIO(app)


# Sent from cameras, with a new image
@socket.on("new-image")
def get_image(data):
    print("Got new image")
    print(data['hostname'])
    # socket.emit('image', data, room=data['hostname']) # TODO: Create room from hostname
    socket.emit('image', data)


if __name__ == '__main__':
    socket.run(app, host='0.0.0.0')
