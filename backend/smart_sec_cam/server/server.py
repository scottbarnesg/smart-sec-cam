import json
import os
import time
from functools import wraps

import eventlet
import jwt.exceptions
from flask import Flask, send_from_directory, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO, join_room

from smart_sec_cam.auth.authentication import Authenticator
from smart_sec_cam.auth.database import AuthDatabase
from smart_sec_cam.auth.models import User
from smart_sec_cam.redis import RedisImageReceiver
from smart_sec_cam.video.manager import VideoManager

# SocketIO & CORS
eventlet.monkey_patch()
app = Flask(__name__, static_url_path='', static_folder='/backend/build', template_folder='/backend/build')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
# Authentication
auth_db = AuthDatabase()
authenticator = Authenticator(auth_db)
# Application-specific data
VIDEO_DIR = "data/videos"
rooms = {}
ENABLE_USER_REGISTRATION = False


def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        client_ip_addr = request.remote_addr
        # return 401 if token is not passed
        if not token:
            return json.dumps({'status': "ERROR", "error": "Missing token"}), 401, {'ContentType': 'application/json'}
        try:
            if not authenticator.validate_token(token, client_ip_addr):
                return json.dumps({'status': "ERROR", "error": "Invalid token"}), 401, {'ContentType': 'application/json'}
        except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError):
            return json.dumps({'status': "ERROR", "error": "Invalid token"}), 401, {'ContentType': 'application/json'}
        # returns the current logged in users contex to the routes
        return f(*args, **kwargs)
    return decorated


"""
SocketIO endpoints
"""


@socketio.on('join')
def on_join(data):
    # Validate token
    token = data['token']
    client_ip_addr = request.remote_addr
    try:
        if not authenticator.validate_token(token, client_ip_addr):
            return json.dumps({'status': "ERROR", "error": "Invalid token"})
    except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError):
        return json.dumps({'status': "ERROR", "error": "Invalid token"})
    # Join room
    room = data['room']
    join_room(room)


"""
UI Endpoints
"""


@app.route('/register', defaults={'path': 'register'})
@app.route('/videos', defaults={'path': 'videos'})
@app.route('/stream', defaults={'path': 'stream'})
@app.route('/', defaults={'path': ''})
def serve_react_ui(path):
    return render_template("index.html")


"""
API Endpoints
"""


@app.route("/api/auth/login", methods=["POST"])
def authenticate():
    # Get data from request body
    username = request.json.get("username")
    password = request.json.get("password")
    client_ip_addr = request.remote_addr
    # Authenticate request
    try:
        token = authenticator.authenticate(username, password, client_ip_addr)
    except ValueError:
        return json.dumps({'status': "ERROR", "error": "Incorrect username or password"}), 401, \
               {'ContentType': 'application/json'}
    if not token:
        return json.dumps({'status': "ERROR", "error": "Incorrect username or password"}), 401, \
               {'ContentType': 'application/json'}
    return json.dumps({'status': "OK", 'token': token}), 200, {'ContentType': 'application/json'}


@app.route("/api/auth/num-users", methods=["GET"])
def get_num_users():
    return json.dumps({'status': "OK", 'users': auth_db.get_num_users()}), 200, {'ContentType': 'application/json'}


@app.route("/api/auth/register", methods=["POST"])
def register():
    # Check if any users exist and if user registration is enabled
    if auth_db.get_num_users() > 0 and not ENABLE_USER_REGISTRATION:
        return json.dumps({'status': "ERROR", 'error': "User registration is disabled"}), 403, \
               {'ContentType': 'application/json'}
    # Create new user
    username = request.json.get("username")
    password = request.json.get("password")
    new_user = User(username)
    new_user.generate_id()
    new_user.set_password(password)
    try:
        auth_db.add_user(new_user)
    except ValueError:
        return json.dumps({'status': "ERROR", "error": "Username taken"}), 404, {'ContentType': 'application/json'}
    return json.dumps({'status': "OK"}), 200, {'ContentType': 'application/json'}


@app.route("/api/token/validate", methods=["POST"])
def validate_token():
    token = request.json.get("token")
    client_ip_addr = request.remote_addr
    try:
        if not authenticator.validate_token(token, client_ip_addr):
            return json.dumps({'status': "ERROR", "error": "Invalid token"}), 401, {'ContentType': 'application/json'}
    except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError, jwt.exceptions.ImmatureSignatureError):
        return json.dumps({'status': "ERROR", "error": "Invalid token"}), 401, {'ContentType': 'application/json'}
    return json.dumps({'status': "OK"}), 200, {'ContentType': 'application/json'}


@app.route("/api/token/ttl", methods=["GET"])
def get_token_ttl():
    token = request.args.get("token")
    client_ip_addr = request.remote_addr
    # Validate token
    try:
        if not authenticator.validate_token(token, client_ip_addr):
            return json.dumps({'status': "ERROR", "error": "Invalid token"}), 401, {'ContentType': 'application/json'}
    except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError):
        return json.dumps({'status': "ERROR", "error": "Invalid token"}), 401, {'ContentType': 'application/json'}
    # Return TTL
    ttl = authenticator.get_token_ttl(token)
    return json.dumps({'status': "OK", "ttl": ttl}), 200, {'ContentType': 'application/json'}


@app.route("/api/token/refresh", methods=["POST"])
def refresh_token():
    token = request.json.get("token")
    client_ip_addr = request.remote_addr
    try:
        if not authenticator.validate_token(token, client_ip_addr):
            return json.dumps({'status': "ERROR", "error": "Invalid token"}), 401, {'ContentType': 'application/json'}
    except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError):
        return json.dumps({'status': "ERROR", "error": "Invalid token"}), 401, {'ContentType': 'application/json'}
    new_token = authenticator.refresh_token(token, client_ip_addr)
    return json.dumps({'status': "OK", "token": new_token}), 200, {'ContentType': 'application/json'}


@app.route("/api/video/rooms", methods=["GET"])
@require_token
def get_rooms():
    global rooms
    return json.dumps({'rooms': rooms}), 200, {'ContentType': 'application/json'}


@app.route("/api/video/video-list", methods=["GET"])
@require_token
def get_video_list():
    video_type = request.args.get("video-format")  # "webm" or "mp4"
    global VIDEO_DIR
    video_manager = VideoManager(video_dir=VIDEO_DIR)
    return json.dumps({'videos': video_manager.get_video_filenames(video_type)}), 200, {'ContentType': 'application/json'}


@app.route("/api/video/<file_name>", methods=["GET"])
def get_video(file_name: str):
    # Validate token
    token = request.args.get("token")
    client_ip_addr = request.remote_addr
    if not token:
        return json.dumps({'status': "ERROR", "error": "Missing token"}), 401, {'ContentType': 'application/json'}
    try:
        if not authenticator.validate_token(token, client_ip_addr):
            return json.dumps({'status': "ERROR", "error": "Invalid token"}), 401, {'ContentType': 'application/json'}
    except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError):
        return json.dumps({'status': "ERROR", "error": "Invalid token"}), 401, {'ContentType': 'application/json'}
    # Return video
    global VIDEO_DIR
    if "webm" in file_name:
        mime_type = 'video/webm'
    elif "mp4" in file_name:
        mime_type = 'video/mp4'
    else:
        return json.dumps({'status': "ERROR"}), 404, {'ContentType': 'application/json'}
    return send_from_directory(VIDEO_DIR, file_name, as_attachment=True, mimetype=mime_type)


def listen_for_images(redis_url: str, redis_port: int):
    global rooms
    started_listener_thread = False
    image_receiver = RedisImageReceiver(redis_url, redis_port)
    while True:
        # Check for new channels
        # TODO: This should only be done every N seconds
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
    parser.add_argument('--redis-url', help='Server address to stream images to', type=str, default='localhost')
    parser.add_argument('--redis-port', help='Server port to stream images to', type=int, default=6379)
    parser.add_argument('--video-dir', help='Directory in which video files are stored', type=str,
                        default="data/videos")
    args = parser.parse_args()

    VIDEO_DIR = args.video_dir
    ENABLE_USER_REGISTRATION = bool(int(os.environ.get("ENABLE_REGISTRATION")))

    socketio.start_background_task(listen_for_images, args.redis_url, args.redis_port)
    socketio.run(app, host='0.0.0.0', port="8443", debug=True, certfile='certs/sec-cam-server.cert',
                 keyfile='certs/sec-cam-server.key')
