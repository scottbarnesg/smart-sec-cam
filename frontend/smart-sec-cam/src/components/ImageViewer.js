import React from "react";

import { useCookies } from 'react-cookie';
import io from "socket.io-client";

import "./ImageViewer.css";

const SERVER_URL = "https://localhost:8443"
let socket = io(SERVER_URL)

export default function ImageViewer(props) {
    const [srcBlob, setSrcBlob] = React.useState(null);
    const [cookies, setCookie] = useCookies(["token"]);


    React.useEffect(() => {
        socket.on('image', (payload) => {
            if (payload.room === props.room){
                const data = new Uint8Array(payload.data);
                const dataBase64 = btoa(String.fromCharCode.apply(null, data));
                setSrcBlob(dataBase64);
            }
        });
        socket.emit('join', {"room": props.room, "token": cookies.token});
    }, []);

    return (
        <div className="imageviewer">
            <img src={`data:image/jpeg;base64,${srcBlob}`} alt={props.room} ></img>
        </div>
    );

};