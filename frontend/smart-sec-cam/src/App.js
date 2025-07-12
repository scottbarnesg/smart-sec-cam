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
    const [selectedRoom, setSelectedRoom] = React.useState(null);
    const [hasValidToken, setHasValidToken] = React.useState(null);
    const [tokenTTL, setTokenTTL] = React.useState(null);
    const [cookies, setCookie] = useCookies(["token"]);
    const navigate = useNavigate();

    React.useEffect(() => {
        if (cookies.token == null) {
            navigate('/', { });
        }
        else {
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
            getTokenTTL(cookies.token, setTokenTTL);
            const requestOptions = {
                method: 'GET',
                headers: { 'x-access-token': cookies.token },
            };
            fetch(SERVER_URL + ROOMS_ENDPOINT, requestOptions)
                .then((resp) => resp.json())
                .then((data) => updateRooms(data['rooms']))
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
        if (tokenTTL < 0) {
            navigate('/', { });
        }
        let tokenRefreshInterval = 0;
        if (tokenTTL - 60 >= 0) {
             tokenRefreshInterval = (tokenTTL - 60) * 1000;
        }
        const timer = setTimeout(function(){
            refreshToken(cookies.token, setCookie);
            setHasValidToken(null);
        }, tokenRefreshInterval);
        return () => clearTimeout(timer);
    }, [tokenTTL])

    React.useEffect(() => {
        if (cookies == null || cookies.token == null) {
            return;
        }
        try {
            validateToken(cookies.token, setHasValidToken);
        }
        catch {
            navigate('/', { });
        }
    }, [cookies])

    React.useEffect(() => {
        const requestOptions = {
            method: 'GET',
            headers: { 'x-access-token': cookies.token },
        };
        fetch(SERVER_URL + ROOMS_ENDPOINT, requestOptions)
            .then((resp) => resp.json())
            .then((data) => updateRooms(data['rooms']))
    }, []);

    function updateRooms(rooms) {
        const roomNames = rooms != null ? Object.keys(rooms) : [];
        setRooms(roomNames);
        if (roomNames.length > 0 && selectedRoom === null) {
            setSelectedRoom(roomNames[0]);
        }
    }

    return (
        <div className="App">
            <NavBar token={cookies.token} />
            <div className="app-container">
            <div className="sidebar">
                {rooms.map(room => (
                <div 
                    key={room} 
                    className="sidebar-item"
                    onClick={() => setSelectedRoom(room)}
                >
                    <ImageViewer room={room} />
                </div>
                ))}
            </div>
            <div className="main-view">
                {selectedRoom && <ImageViewer key={selectedRoom} room={selectedRoom} />}
            </div>
            </div>
        </div>
    );
};