import json
import time

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO, join_room
import eventlet
from engineio.payload import Payload

from redis_image_receiver import RedisImageReceiver

ROOM_TIMEOUT = 60

Payload.max_decode_packets = 500
eventlet.monkey_patch()

app = Flask(__name__)
CORS(app)
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


@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)


@app.route("/rooms", methods=["GET"])
def get_rooms():
    return json.dumps({'rooms': rooms}), 200, {'ContentType': 'application/json'}


def listen_for_images():
    started_listener_thread = False
    image_receiver = RedisImageReceiver()
    while True:
        # Check for new channels
        channel_list = image_receiver.get_all_channels()
        if channel_list != image_receiver.subscribed_channels:
            image_receiver.set_channels(channel_list)
            print(image_receiver.subscribed_channels)
            if not started_listener_thread:
                image_receiver.start_listener_thread()  # TODO: Can't call this until we have a subscribed channel
        # Check for new messages
        if image_receiver.has_message() and image_receiver.subscribed_channels:
            message = image_receiver.get_message()
            image = message.get("data")
            room = str(message.get("channel"))
            rooms[room] = time.time()
            socketio.emit('image', {'room': room, 'data': image}, room=room)
            print("Emitted message to: " + room)
        time.sleep(0.01)


if __name__ == '__main__':
    socketio.start_background_task(target=listen_for_images)
    socketio.run(app, host='0.0.0.0')
