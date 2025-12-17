import eventlet
eventlet.monkey_patch()

from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_cors import CORS
import random
import string

app = Flask(__name__)
CORS(app)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="eventlet"
)

rooms = {}          # room_code -> [socket_ids]
users = {}          # socket_id -> username
random_queue = []   # waiting socket_ids


def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))


def leave_all_rooms(sid):
    for room, members in list(rooms.items()):
        if sid in members:
            members.remove(sid)
            leave_room(room)

            if not members:
                del rooms[room]


@socketio.on("connect")
def on_connect():
    print("CONNECTED:", request.sid)


@socketio.on("join_random")
def join_random(data):
    sid = request.sid
    users[sid] = data["username"]

    if random_queue:
        other = random_queue.pop(0)
        room = generate_room_code()

        rooms[room] = [sid, other]

        join_room(room, sid)
        join_room(room, other)

        emit("room_joined", {"room": room}, room=room)
    else:
        random_queue.append(sid)


@socketio.on("create_room")
def create_room(data):
    sid = request.sid
    users[sid] = data["username"]

    room = generate_room_code()
    rooms[room] = [sid]

    join_room(room)
    emit("room_created", {"room": room})


@socketio.on("join_room_with_code")
def join_room_with_code(data):
    sid = request.sid
    users[sid] = data["username"]
    room = data["room"]

    if room in rooms:
        rooms[room].append(sid)
        join_room(room)

        emit("room_joined", {"room": room}, room=room)
    else:
        emit("error", {"message": "Invalid room code"})


@socketio.on("send_message")
def send_message(data):
    sid = request.sid
    room = data["room"]
    message = data["message"]
    username = users.get(sid, "Stranger")

    print(f"[{room}] {username}: {message}")

    # 🔥 THIS IS THE IMPORTANT PART
    emit(
        "receive_message",
        {
            "username": username,
            "message": message
        },
        room=room,
        include_self=True   # ✅ sender also receives message
    )


@socketio.on("disconnect")
def on_disconnect():
    sid = request.sid
    users.pop(sid, None)

    if sid in random_queue:
        random_queue.remove(sid)

    leave_all_rooms(sid)
    print("DISCONNECTED:", sid)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
