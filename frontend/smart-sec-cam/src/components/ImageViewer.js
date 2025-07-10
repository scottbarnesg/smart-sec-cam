import React, { useEffect, useState } from "react";
import { useCookies } from 'react-cookie';
import "./ImageViewer.css";
import socket from "./socket"; // ✅ Import shared socket

export default function ImageViewer(props) {
    const [srcBlob, setSrcBlob] = useState(null);
    const [cookies] = useCookies(["token"]);

    useEffect(() => {
        // Remove all existing image listeners
        socket.off('image');

        // Subscribe to the current room's image stream
        socket.on('image', (payload) => {
            if (payload.room === props.room) {
                const data = new Uint8Array(payload.data);
                const dataBase64 = btoa(String.fromCharCode.apply(null, data));
                setSrcBlob(dataBase64);
            }
        });

        // Join the room with the current token
        socket.emit('join', { room: props.room, token: cookies.token });

        // Cleanup on unmount or when props change
        return () => {
            socket.off('image');
        };
    }, [props.room, cookies.token]);

    return (
        <div className={`imageviewer ${props.className || ''}`}>
            {srcBlob ? (
                <img
                    src={`data:image/jpeg;base64,${srcBlob}`}
                    alt={props.room}
                />
            ) : (
                <div className="loading">Loading feed for {props.room}...</div>
            )}
        </div>
    );
}