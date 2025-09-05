import React, { useCallback } from "react";

import { useCookies } from 'react-cookie';
import io from "socket.io-client";

import "./ImageViewer.css";
import { base64ToBlob } from "../utils/base64ToBlob";

const SERVER_URL = "https://localhost:8443"
let socket = io(SERVER_URL)

export default function ImageViewer({ room, isPreview }) {
  const [srcUrl, setSrcUrl] = React.useState(null);
  const [cookies] = useCookies(["token"]);

  // Stable handler so we can deregister it reliably
  const imageHandler = useCallback((payload) => {
    if (payload.room !== room) return;
    if (!payload.data) return;
    try {
      const blob = base64ToBlob(payload.data);
      const newUrl = URL.createObjectURL(blob);
      // Revoke the previous URL to free memory
      if (srcUrl) {
        URL.revokeObjectURL(srcUrl);
      }
      setSrcUrl(newUrl);
    } catch (e) {
      // Silently ignore malformed data
    }
  }, [room, srcUrl]);

  React.useEffect(() => {
    // Register listener and join the room
    socket.on('image', imageHandler);
    socket.emit('join', { room, token: cookies.token });

    // Cleanup on unmount or when room changes
    return () => {
      if (srcUrl) {
        URL.revokeObjectURL(srcUrl);
      }
      socket.off('image', imageHandler);
    };
  }, [room, cookies.token, imageHandler]);

  return (
    <div className={`imageviewer ${isPreview ? 'preview' : 'main'}`}>
      {srcUrl && <img src={srcUrl} alt={room} />}
    </div>
  );
}