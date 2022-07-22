import React from "react";
import { useNavigate, useLocation } from 'react-router-dom';

import ImageViewer from "./components/ImageViewer";
import NavBar from "./components/NavBar";

import './App.css';

import io from "socket.io-client";

const SERVER_URL = "https://localhost:8443"
const ROOMS_ENDPOINT = "/api/video/rooms"
let socket = io(SERVER_URL)

export default function App() {
    const [rooms, setRooms] = React.useState([]);
    const [components, setComponents] = React.useState([]);
    const location = useLocation();
    const navigate = useNavigate();

    React.useEffect(() => {
        // TODO: Check cookie for valid token
        // Check that we got a token from the props. If not, navigate to the login screen
        if (location.state == null || location.state.token == null) {
            navigate('/', { });
            return;
        }
        const requestOptions = {
            method: 'GET',
            headers: { 'x-access-token': location.state.token },
        };
        // Get room list
        fetch(SERVER_URL + ROOMS_ENDPOINT, requestOptions)
            .then((resp) => resp.json())
            .then((data) => {console.log(data); updateRooms(data['rooms'])})
        // Configure socket
        socket.on('rooms', (payload) => {
            updateRooms(payload.rooms);
        });
    }, []);

    React.useEffect(() => {
        renderComponents();
    }, [rooms])

    function updateRooms(rooms) {
        setRooms(Object.keys(rooms))
        // renderComponents();
    }

    function renderComponents() {
        let components = []
        for (const room_name of rooms) {
            components.push(<ImageViewer key={room_name} room={room_name}/>)
        }
        setComponents(components);
    }

    return (
        <div className="App">
            <NavBar token={location.state.token}/>
            {components}
        </div>
    );
};
