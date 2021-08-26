import json
import time

from flask import Flask
from flask_socketio import SocketIO, join_room
import eventlet
from engineio.payload import Payload

ROOM_TIMEOUT = 60

Payload.max_decode_packets = 500
eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
rooms = {}


# Sent from cameras, with a new image
@socketio.on("new-image")
def get_image(data):
    # Create room from hostname
    room = data.get('hostname')
    rooms[room] = time.time()
    # Emit to room
    image = data.get('image')
    socketio.emit('image', {'room': room, 'data': image}, room=room)
    # socket.emit('image', {'data': data['image']})


@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)


@app.route("/rooms", methods=["GET"])
def get_rooms():
    return json.dumps({'rooms': rooms}), 200, {'ContentType': 'application/json'}


def check_room_staleness():
    while True:
        for room, last_connection_time in rooms.items():
            if time.time() - last_connection_time > ROOM_TIMEOUT:
                print("Room timed out: " + room)
                socketio.emit("error")
        time.sleep(1)


if __name__ == '__main__':
    socketio.start_background_task(target=check_room_staleness)
    socketio.run(app, host='0.0.0.0')
