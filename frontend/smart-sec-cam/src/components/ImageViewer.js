import React from "react";

import { useCookies } from 'react-cookie';
import io from "socket.io-client";

import "./ImageViewer.css";

const SERVER_URL = "https://localhost:8443"
let socket = io(SERVER_URL)

export default function ImageViewer({ room, isPreview }) {
  const [srcBlob, setSrcBlob] = React.useState(null);
  const [cookies, setCookie] = useCookies(["token"]);

  React.useEffect(() => {
    socket.on('image', (payload) => {
      if (payload.room === room) {
        setSrcBlob(payload.data);
      }
    });
    socket.emit('join', { room, token: cookies.token });
  }, [room]);

  return (
    <div className={`imageviewer ${isPreview ? 'preview' : 'main'}`}>
      {srcBlob && <img src={`data:image/jpeg;base64,${srcBlob}`} alt={room} />}
    </div>
  );
}