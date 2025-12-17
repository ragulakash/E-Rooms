import { io } from "socket.io-client";

export const socket = io(
  "https://e-rooms.onrender.com",
  {
    transports: ["websocket"],
  }
);
