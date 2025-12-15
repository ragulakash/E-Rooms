import { useEffect, useState } from "react";
import { io } from "socket.io-client";

const socket = io("https://e-rooms.onrender.com/");

function EntryPage({ setRoom, setUsername }) {
  const [name, setName] = useState("");
  const [roomCode, setRoomCode] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    socket.on("room_created", (data) => {
      setRoom(data.room);
      setUsername(name);
    });

    socket.on("room_joined", (data) => {
      setRoom(data.room);
      setUsername(name);
    });

    socket.on("error", (data) => {
      setError(data.message);
    });

    return () => {
      socket.off("room_created");
      socket.off("room_joined");
      socket.off("error");
    };
  }, [name, setRoom, setUsername]);

  const validate = () => {
    if (!name.trim()) {
      setError("Enter your name");
      return false;
    }
    return true;
  };

  return (
    <div className="card">
      <h2>E-Room Chat</h2>

      {error && <p className="error">{error}</p>}

      <input
        placeholder="Enter your name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />

      <button onClick={() => validate() && socket.emit("join_random", { username: name })}>
        Join Random E-Room
      </button>

      <button onClick={() => validate() && socket.emit("create_room", { username: name })}>
        Create E-Room
      </button>

      <input
        placeholder="Enter Room Code"
        value={roomCode}
        onChange={(e) => setRoomCode(e.target.value)}
      />

      <button
        onClick={() =>
          validate() &&
          socket.emit("join_room_with_code", {
            room: roomCode.toUpperCase(),
            username: name,
          })
        }
      >
        Join With Code
      </button>
    </div>
  );
}

export default EntryPage;
