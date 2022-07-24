import React from "react";
import { useNavigate } from "react-router-dom";

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { useCookies } from 'react-cookie';

import { validateToken } from "../utils/ValidateToken";

import "./Login.css"


const SERVER_URL = "https://localhost:8443"
const AUTH_ENDPOINT = "/api/auth/login"
const NUM_USERS_ENDPOINT = "/api/auth/num-users"
const REFRESH_TOKEN_ENDPOINT = "/api/token/refresh"


export default function Login(props) {
    const [username, setUsername] = React.useState("");
    const [password, setPassword] = React.useState("");
    const [token, setToken] = React.useState("");
    const [hasRegisteredUser, setHasRegisteredUser] = React.useState(null);
    const [hasValidToken, setHasValidToken] = React.useState(null);
    const [cookies, setCookie] = useCookies(["token"]);
    const navigate = useNavigate();

    React.useEffect(() => {
        checkServerHasUser();
    }, []);


    React.useEffect(() => {
        if (hasRegisteredUser == null) {
            return;
        }
        if (hasRegisteredUser) {
            // Check cookies to see if we have a JWT. If so, auto-redirect to video stream page
            const cachedToken = cookies.token;
            // Validate token
            validateToken(cachedToken, setHasValidToken);
        }
        else if (hasRegisteredUser === false) {
            navigate('/register');
        }
    }, [hasRegisteredUser]);

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

    function checkServerHasUser() {
        const url = SERVER_URL + NUM_USERS_ENDPOINT;
        fetch(url)
            .then(response => response.json())
            .then(data => handleCheckServerHasUserResponse(data)); 
    }

    function handleCheckServerHasUserResponse(data) {
        setHasRegisteredUser(data["users"] > 0)
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
        // Submit username and password
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
        .then(data => handleLoginResponse(data));        
    };

    function handleLoginResponse(data) {
        if (data.status === "OK") {
            setToken(data["token"]);
            // Write token to cookie
            setCookie("token", data["token"], {path: "/"})
            // Navigate to App page,
            navigate('/stream');
        }
        else {
            // TODO: Show error message on UI somewhere
            console.log("Login failed")
        }
    }

    return (
        <div className="Login">
            <Box
                component="form"
                sx={{
                    '& > :not(style)': { m: 1, width: '100%', paddingTop: '30vh', paddingBottom: '2vh' },
                }}
                noValidate
                autoComplete="off"
                display="flex"
                justifyContent="center"
                alignItems="center"
                flexDirection="column"
            >
                <Typography variant="h4" align="center" gutterBottom component="div">
                    Smart Sec Cam
                </Typography>
            </Box>
            <Box
                component="form"
                sx={{
                    '& > :not(style)': { m: 1, width: '100%', padding: '10' },
                }}
                noValidate
                autoComplete="off"
                display="flex"
                justifyContent="center"
                alignItems="center"
                flexDirection="column"
            >  
                <Typography variant="h5" align="center" gutterBottom component="div">
                    Login
                </Typography>
                <TextField
                    required
                    id="username"
                    label="Username"
                    value={username}
                    onChange={event => setUsername(event.target.value)}
                    sx={{
                        maxWidth: '240px', 
                        minWidth: '120px', 
                        '& .MuiInputBase-input': {
                            color: 'white',
                        },
                        '& .MuiOutlinedInput-root': {
                            '& fieldset': {
                              borderColor: 'white',
                            }
                        },
                        "& .MuiInputLabel-root": {
                            color: "white"
                        }
                    }}
                />
                <TextField
                    required
                    id="password"
                    type="password"
                    label="Password"
                    value={password}
                    onChange={event => setPassword(event.target.value)}
                    sx={{
                        maxWidth: '240px', 
                        minWidth: '120px', 
                        '& .MuiInputBase-input': {
                            color: 'white',
                        },
                        '& .MuiOutlinedInput-root': {
                            '& fieldset': {
                              borderColor: 'white',
                            }
                        },
                        "& .MuiInputLabel-root": {
                            color: "white"
                        }
                    }}
                />
                <Button variant="contained" style={{maxWidth: '180px', maxHeight: '60px', minWidth: '50px', minHeight: '40px'}} onClick={() => handleLogin()}>Login</Button>
            </Box>
        </div>
    );
}