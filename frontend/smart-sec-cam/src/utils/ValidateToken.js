const SERVER_URL = "https://localhost:8443"
const VALIDATE_TOKEN_ENDPOINT = "/api/token/validate"


export function validateToken(token, callback) {
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
            .then(data => handleValidateTokenResponse(data))
            .then(isTokenValid => callback(isTokenValid))
}

function handleValidateTokenResponse(data){
    if (data.status === "OK") {
        console.log("Token validation successful")
        return true;
    }
    else {
        console.log("Token validation failed");
        return false;
    }
}