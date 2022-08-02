const SERVER_URL = "https://localhost:8443"
const TOKEN_TTL_ENDPOINT = "/api/token/ttl"


export function getTokenTTL(token, callback) {
    const url = SERVER_URL + TOKEN_TTL_ENDPOINT + "?token=" + token;
    fetch(url)
        .then(response => response.json())
        .then(data => handleTokenTTLResponse(data))
        .then(TTL => callback(TTL))
}

function handleTokenTTLResponse(data){
    if (data.status === "OK") {
        console.log("TTL: " + String(data.ttl));
        return data.ttl;
    }
    else {
        return -1;
    }
}