const SERVER_URL = "https://localhost:8443"
const VALIDATE_TOKEN_ENDPOINT = "/api/token/refresh"


export function refreshToken(token, setCookie) {
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
            .then(data => handleRefreshTokenResponse(data, setCookie))
}

function handleRefreshTokenResponse(data, setCookie){
    if (data.status === "OK") {
        console.log("Token refresh successful")
        setCookie("token", data.token, {path: "/"});
        return true;
    }
    else {
        console.log("Token refresh failed");
        return false;
    }
}