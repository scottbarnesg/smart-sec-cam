import React from "react";
import { useNavigate } from "react-router-dom";

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';

const SERVER_URL = "https://localhost:8443"
const AUTH_ENDPOINT = "/auth"


export default function Login(props) {
    const [username, setUsername] = React.useState("");
    const [password, setPassword] = React.useState("");
    const [token, setToken] = React.useState("");
    const navigate = useNavigate();

    React.useEffect(() => {
        // TODO: Check cookies to see if we have a JWT. If so, auto-redirect to video stream page
    }, []);

    async function handleLogin() {
        // TODO: Submit username and password to /auth
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
        // TODO: Get token from response
        
    };

    function handleAuthResponse(data) {
        console.log(data);
        console.log(data["token"]);
        if (data.status === "OK") {
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
                <Typography variant="h4" align="center" gutterBottom component="div">
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