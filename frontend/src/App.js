import { useState } from "react";
import EntryPage from "./EntryPage";
import ChatPage from "./ChatPage";
import "./App.css";

function App() {
  const [room, setRoom] = useState(null);
  const [username, setUsername] = useState("");

  return (
    <div className="app">
      {!room ? (
        <EntryPage setRoom={setRoom} setUsername={setUsername} />
      ) : (
        <ChatPage room={room} username={username} />
      )}
    </div>
  );
}

export default App;
