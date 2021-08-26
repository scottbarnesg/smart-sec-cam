from flask import Flask, send_file
from flask_socketio import SocketIO, join_room
import json
import io
import eventlet
from engineio.payload import Payload

Payload.max_decode_packets = 500
eventlet.monkey_patch()

app = Flask(__name__)
socket = SocketIO(app, cors_allowed_origins="*")
rooms = []


# Sent from cameras, with a new image
@socket.on("new-image")
def get_image(data):
    print("Got new image, emitting to clients")
    # Create room from hostname
    room = data['hostname']
    if room not in rooms:
        rooms.append(room)
    # Emit to room
    socket.emit('image', {'room': room, 'data': data['image']}, room=room)
    # socket.emit('image', {'data': data['image']})


@socket.on('join')
def on_join(data):
    room = data['room']
    join_room(room)


@app.route("/rooms", methods=["GET"])
def get_rooms():
    return json.dumps({'rooms': rooms}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    socket.run(app, host='0.0.0.0')
