import { io } from "socket.io-client";

const SERVER_URL = "https://localhost:8443";
const socket = io(SERVER_URL);

export default socket;