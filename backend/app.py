from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_cors import CORS
import random
import string

app = Flask(__name__)
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}          # room_code -> [socket_ids]
users = {}          # socket_id -> username
random_queue = []   # waiting socket_ids


def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))


def leave_current_room(sid):
    for room, members in list(rooms.items()):
        if sid in members:
            members.remove(sid)
            leave_room(room)

            emit("receive_message", {
                "username": "System",
                "message": "User left the chat"
            }, room=room)

            if not members:
                rooms.pop(room)
            return


@socketio.on("connect")
def connect():
    print("Connected:", request.sid)


@socketio.on("join_random")
def join_random(data):
    username = data.get("username")
    sid = request.sid
    users[sid] = username

    if random_queue:
        other_sid = random_queue.pop(0)
        room_code = generate_room_code()

        rooms[room_code] = [sid, other_sid]

        join_room(room_code, sid)
        join_room(room_code, other_sid)

        emit("room_joined", {"room": room_code}, room=room_code)
    else:
        random_queue.append(sid)


@socketio.on("create_room")
def create_room(data):
    username = data.get("username")
    sid = request.sid
    users[sid] = username

    room_code = generate_room_code()
    rooms[room_code] = [sid]

    join_room(room_code)
    emit("room_created", {"room": room_code})


@socketio.on("join_room_with_code")
def join_room_with_code(data):
    room_code = data.get("room")
    username = data.get("username")
    sid = request.sid
    users[sid] = username

    if room_code in rooms:
        rooms[room_code].append(sid)
        join_room(room_code)
        emit("room_joined", {"room": room_code}, room=room_code)
    else:
        emit("error", {"message": "Invalid Room Code"})


@socketio.on("send_message")
def send_message(data):
    room = data["room"]
    message = data["message"]
    username = users.get(request.sid, "Stranger")

    emit("receive_message", {
        "username": username,
        "message": message
    }, room=room)


@socketio.on("next_chat")
def next_chat(data):
    sid = request.sid
    username = users.get(sid)

    leave_current_room(sid)

    # put user back to random queue
    random_queue.append(sid)


@socketio.on("disconnect")
def disconnect():
    sid = request.sid
    users.pop(sid, None)

    if sid in random_queue:
        random_queue.remove(sid)

    leave_current_room(sid)
    print("Disconnected:", sid)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)

