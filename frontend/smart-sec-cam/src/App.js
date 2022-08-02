import React from "react";
import { useNavigate } from 'react-router-dom';

import { useCookies } from 'react-cookie';

import ImageViewer from "./components/ImageViewer";
import NavBar from "./components/NavBar";

import { validateToken } from "./utils/ValidateToken";
import { getTokenTTL } from "./utils/GetTokenTTL";

import './App.css';

import io from "socket.io-client";
import { refreshToken } from "./utils/RefreshToken";

const SERVER_URL = "https://localhost:8443"
const ROOMS_ENDPOINT = "/api/video/rooms"
let socket = io(SERVER_URL)

export default function App() {
    const [rooms, setRooms] = React.useState([]);
    const [components, setComponents] = React.useState([]);
    const [hasValidToken, setHasValidToken] = React.useState(null);
    const [tokenTTL, setTokenTTL] = React.useState(null);
    const [cookies, setCookie] = useCookies(["token"]);
    const navigate = useNavigate();

    React.useEffect(() => {
        // Check cookie for valid token. If not, navigate to the login screen
        if (cookies.token == null) {
            navigate('/', { });
        }
        else {
            // Validate token
            try {
                validateToken(cookies.token, setHasValidToken);
            }
            catch {
                navigate('/', { });
            }
        }
    }, []);

    React.useEffect(() => {
        if (hasValidToken) {
            // Get Token's TTL
            getTokenTTL(cookies.token, setTokenTTL);
            const requestOptions = {
                method: 'GET',
                headers: { 'x-access-token': cookies.token },
            };
            // Get room list
            fetch(SERVER_URL + ROOMS_ENDPOINT, requestOptions)
                .then((resp) => resp.json())
                .then((data) => {updateRooms(data['rooms'])})
            // Configure socket
            socket.on('rooms', (payload) => {
                updateRooms(payload.rooms);
            });
        }
        else if (hasValidToken === false) {
            navigate('/', { });
        }
    }, [hasValidToken]);

    React.useEffect(() => {
        if (tokenTTL == null) {
            return;
        }
        // If TTL is negative, token is expired or invalid. Navigate to login
        if (tokenTTL < 0) {
            navigate('/', { });
        }
        // Subtract a minute from the token interval and convert it to milliseconds
        let tokenRefreshInterval = 0;
        if (tokenTTL - 60 >= 0) {
             tokenRefreshInterval = (tokenTTL - 60) * 1000;
        }
        // Start timer to refresh token in background
        const interval = setInterval(() => {
            refreshToken(cookies.token, setCookie);
        }, tokenRefreshInterval);
        return () => clearInterval(interval);
    }, [tokenTTL])

    React.useEffect(() => {
        if (cookies == null || cookies.token == null) {
            return;
        }
        // Validate Token
        try {
            validateToken(cookies.token, setHasValidToken);
        }
        catch {
            navigate('/', { });
        }
    }, [cookies])

    React.useEffect(() => {
        renderComponents();
    }, [rooms])

    function updateRooms(rooms) {
        setRooms(rooms != null ? Object.keys(rooms) : []);
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
            <NavBar token={cookies.token}/>
            {components}
        </div>
    );
};
