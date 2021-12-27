import json
import time

import eventlet
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO, join_room

from redis_image_receiver import RedisImageReceiver


eventlet.monkey_patch()
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}


@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)


@app.route("/rooms", methods=["GET"])
def get_rooms():
    global rooms
    return json.dumps({'rooms': rooms}), 200, {'ContentType': 'application/json'}


def listen_for_images(redis_url: str, redis_port: int):
    global rooms
    started_listener_thread = False
    image_receiver = RedisImageReceiver(redis_url, redis_port)
    while True:
        # Check for new channels
        channel_list = image_receiver.get_all_channels()
        if channel_list != image_receiver.subscribed_channels:
            image_receiver.set_channels(channel_list)
            if not started_listener_thread:
                image_receiver.start_listener_thread()
        # Check for new messages
        if image_receiver.has_message() and image_receiver.subscribed_channels:
            message = image_receiver.get_message()
            image = message.get("data")
            room = str(message.get("channel"))
            rooms[room] = time.time()
            socketio.emit('image', {'room': room, 'data': image}, room=room)
        time.sleep(0.01)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--redis-url', help='Server address to stream images to', default='localhost')
    parser.add_argument('--redis-port', help='Server port to stream images to', default=6379)
    args = parser.parse_args()

    socketio.start_background_task(listen_for_images, args.redis_url, args.redis_port)
    socketio.run(app, host='0.0.0.0')
