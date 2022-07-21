import React from "react";
import { useNavigate } from "react-router-dom";

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import {useCookies} from 'react-cookie';

const SERVER_URL = "https://localhost:8443"
const AUTH_ENDPOINT = "/auth"
const VALIDATE_TOKEN_ENDPOINT = "/validate-token"
const REFRESH_TOKEN_ENDPOINT = "/refresh-token"


export default function Login(props) {
    const [username, setUsername] = React.useState("");
    const [password, setPassword] = React.useState("");
    const [token, setToken] = React.useState("");
    const [hasValidToken, setHasValidToken] = React.useState(false);
    const [cookies, setCookie, removeCookie] = useCookies(["token"]);
    const navigate = useNavigate();

    React.useEffect(() => {
        // Check cookies to see if we have a JWT. If so, auto-redirect to video stream page
        const cachedToken = cookies.token;
        // Validate token
        validateToken(cachedToken);
    }, []);

    React.useEffect(() => {
        const cachedToken = cookies.token;
        if (cachedToken != null && hasValidToken) {
            // Refresh token
            refreshToken(cachedToken);
        }
    }, [hasValidToken])

    React.useEffect(() => {
        if (token != null && hasValidToken) {
            // Navigate to video stream page
            navigate('/stream', {state: { token: token }});
        }
    }, [token])

    function validateToken(token) {
        const url = SERVER_URL + VALIDATE_TOKEN_ENDPOINT;
        const payload = {
            "token": token
        }
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        };
        fetch(url, requestOptions)
            .then(response => response.json())
            .then(data => handleValidateTokenResponse(data)); 
    }

    function handleValidateTokenResponse(data){
        if (data.status === "OK") {
            console.log("Token validation successful")
            setHasValidToken(true);
        }
        else {
            // TODO: Show error message on UI somewhere
            console.log("Token validation failed");
            setHasValidToken(false);
        }
    }

    function refreshToken(token) {
        const url = SERVER_URL + REFRESH_TOKEN_ENDPOINT;
        const payload = {
            "token": token
        }
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        };
        fetch(url, requestOptions)
            .then(response => response.json())
            .then(data => handleRefreshTokenResponse(data)); 
    }

    function handleRefreshTokenResponse(data){
        if (data.status === "OK") {
            setToken(data["token"]);
            // Write token to cookie
            setCookie("token", data["token"], {path: "/"})
        }
        else {
            // TODO: Show error message on UI somewhere
            console.log("Token refresh failed");
        }
    }

    function handleLogin() {
        // Submit username and password to /auth
        const url = SERVER_URL + AUTH_ENDPOINT;
        const payload = {
            "username": username,
            "password": password,
        }
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        };
        fetch(url, requestOptions)
        .then(response => response.json())
        .then(data => handleAuthResponse(data));        
    };

    function handleAuthResponse(data) {
        if (data.status === "OK") {
            setToken(data["token"]);
            // Write token to cookie
            setCookie("token", data["token"], {path: "/"})
            // Navigate to App page, with token as prop
            navigate('/stream', {state: { token: data["token"] }});
        }
        else {
            // TODO: Show error message on UI somewhere
            console.log("Login failed")
        }
    }

    return (
        <div>
            <Box
                component="form"
                sx={{
                    '& > :not(style)': { m: 1, width: '25ch', paddingTop: '30vh' },
                }}
                noValidate
                autoComplete="off"
                display="flex"
                justifyContent="center"
                alignItems="center"
                flexDirection="column"
            >
                <Typography variant="h5" align="center" gutterBottom component="div">
                    Smart Sec Cam Login
                </Typography>
            </Box>
            <Box
                component="form"
                sx={{
                    '& > :not(style)': { m: 1, width: '25ch', padding: '10' },
                }}
                noValidate
                autoComplete="off"
                display="flex"
                justifyContent="center"
                alignItems="center"
                flexDirection="column"
            >
                <TextField
                    required
                    id="username"
                    label="Username"
                    value={username}
                    onChange={event => setUsername(event.target.value)}
                />
                <TextField
                    required
                    id="password"
                    label="Password"
                    value={password}
                    onChange={event => setPassword(event.target.value)}
                />
                <Button variant="contained" onClick={() => handleLogin()}>Login</Button>
            </Box>
        </div>
    );
}