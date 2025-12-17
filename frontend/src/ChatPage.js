import { useEffect, useState } from "react";
import { socket } from "./socket";

function ChatPage({ room, username }) {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");

  useEffect(() => {
    socket.on("receive_message", (data) => {
      setMessages((prev) => [...prev, data]);
    });

    return () => {
      socket.off("receive_message");
    };
  }, []);

  const sendMessage = () => {
    if (!text.trim()) return;

    socket.emit("send_message", {
      room: room,
      message: text,
    });

    setText("");
  };

  return (
    <div className="card">
      <h3>Room: {room}</h3>

      <div className="chat-box">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={msg.username === username ? "bubble me" : "bubble other"}
          >
            <span>{msg.username}</span>
            <p>{msg.message}</p>
          </div>
        ))}
      </div>

      <input
        placeholder="Type a message..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && sendMessage()}
      />

      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

export default ChatPage;
