import React from "react";

import { useCookies } from 'react-cookie';
import io from "socket.io-client";

import "./ImageViewer.css";

const SERVER_URL = "https://localhost:8443"
let socket = io(SERVER_URL)

export default function ImageViewer(props) {
    const [srcBlob, setSrcBlob] = React.useState(null);
    const [oldUrl, setOldUrl] = React.useState(null);
    const [cookies, setCookie] = useCookies(["token"]);


    React.useEffect(() => {
        socket.on('image', (payload) => {
            if (payload.room === props.room){
                var image = new Blob( [ new Uint8Array( payload.data ) ], { type: "image/jpeg" } )
                setOldUrl(srcBlob);
                setSrcBlob(URL.createObjectURL( image ));
                if (oldUrl != null){
                    URL.revokeObjectURL(oldUrl)
                }
                image = null;
            }
        });
        socket.emit('join', {"room": props.room, "token": cookies.token});
    }, []);

    return (
        <div className="imageviewer">
            <img src={srcBlob} alt={props.room} ></img>
        </div>
    );

};