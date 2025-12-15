import { useEffect, useState } from "react";
import { io } from "socket.io-client";

const socket = io("http://localhost:5000");

function ChatPage({ room, username }) {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [currentRoom, setCurrentRoom] = useState(room);

  useEffect(() => {
    socket.on("receive_message", (data) => {
      setMessages((prev) => [...prev, data]);
    });

    socket.on("room_joined", (data) => {
      setCurrentRoom(data.room);
      setMessages([]);
    });

    return () => {
      socket.off("receive_message");
      socket.off("room_joined");
    };
  }, []);

  const sendMessage = () => {
    if (text.trim()) {
      socket.emit("send_message", {
        room: currentRoom,
        message: text,
      });
      setText("");
    }
  };

  const nextChat = () => {
    setMessages([]);
    socket.emit("next_chat", { username });
  };

  return (
    <div className="card">
      <h3>Room: {currentRoom}</h3>

      <div className="chat-box">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={
              msg.username === username ? "bubble me" : "bubble other"
            }
          >
            <span>{msg.username}</span>
            <p>{msg.message}</p>
          </div>
        ))}
      </div>

      <input
        placeholder="Type message..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && sendMessage()}
      />

      <button onClick={sendMessage}>Send</button>
      <button onClick={nextChat}>Next Chat</button>
      <button className="leave-btn" onClick={() => window.location.reload()}>
        Leave
      </button>
    </div>
  );
}

export default ChatPage;
