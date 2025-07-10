import React, { useState, useEffect } from "react";
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
    const [rooms, setRooms] = useState([]);
    const [hasValidToken, setHasValidToken] = useState(null);
    const [tokenTTL, setTokenTTL] = useState(null);
    const [cookies, setCookie] = useCookies(["token"]);
    const [selectedRoom, setSelectedRoom] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        if (cookies.token == null) {
            navigate('/', {});
        } else {
            try {
                validateToken(cookies.token, setHasValidToken);
            } catch {
                navigate('/', {});
            }
        }
    }, []);

    useEffect(() => {
        if (hasValidToken) {
            getTokenTTL(cookies.token, setTokenTTL);
            const requestOptions = {
                method: 'GET',
                headers: { 'x-access-token': cookies.token },
            };
            fetch(SERVER_URL + ROOMS_ENDPOINT, requestOptions)
                .then((resp) => resp.json())
                .then((data) => updateRooms(data['rooms']));
            socket.on('rooms', (payload) => updateRooms(payload.rooms));
        } else if (hasValidToken === false) {
            navigate('/', {});
        }
    }, [hasValidToken]);

    useEffect(() => {
        if (tokenTTL == null) return;
        if (tokenTTL < 0) {
            navigate('/', {});
        }
        let tokenRefreshInterval = (tokenTTL - 60) * 1000;
        if (tokenRefreshInterval < 0) tokenRefreshInterval = 0;
        const timer = setTimeout(() => {
            refreshToken(cookies.token, setCookie);
            setHasValidToken(null);
        }, tokenRefreshInterval);
        return () => clearTimeout(timer);
    }, [tokenTTL]);

    useEffect(() => {
        if (cookies == null || cookies.token == null) return;
        try {
            validateToken(cookies.token, setHasValidToken);
        } catch {
            navigate('/', {});
        }
    }, [cookies]);

    useEffect(() => {
        if (rooms.length > 0 && selectedRoom === null) {
            setSelectedRoom(rooms[0]);
        }
    }, [rooms]);

    function updateRooms(rooms) {
        setRooms(rooms != null ? Object.keys(rooms) : []);
    }

    return (
        <div className="App">
            <NavBar token={cookies.token} />
            <div className="main-container">
                <div className="sidebar">
                    {rooms.map((room) => (
                        <div
                            key={room}
                            onClick={() => setSelectedRoom(room)}
                            className="thumbnail-wrapper"
                        >
                            <ImageViewer room={room} className="thumbnail" />
                        </div>
                    ))}
                </div>
                <div className="main-view">
                    {selectedRoom && <ImageViewer room={selectedRoom} className="large-view" />}
                </div>
            </div>
        </div>
    );
}