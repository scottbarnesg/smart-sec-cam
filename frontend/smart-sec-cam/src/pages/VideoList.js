import React from "react";
import { useNavigate } from 'react-router-dom';

import { isIOS } from 'react-device-detect' 
import { useCookies } from 'react-cookie';

import VideoPlayer from "../components/VideoPlayer";
import NavBar from "../components/NavBar";

import { validateToken } from "../utils/ValidateToken";
import { getTokenTTL } from "../utils/GetTokenTTL";
import { refreshToken } from "../utils/RefreshToken";
import "./VideoList.css"


const SERVER_URL = "https://localhost:8443"
const VIDEOS_ENDPOINT = "/api/video/video-list"

export default function VideoList(props) {
    const [videoFileNames, setVideoFileNames] = React.useState([]);
    const [selectedVideoFile, setSelectedVideoFile] = React.useState(null);
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
            // Get video data
            const requestOptions = {
                method: 'GET',
                headers: { 'x-access-token': cookies.token },
            };
            // Get room list
            let videoFormat = "webm";
            if (isIOS) {
                videoFormat = "mp4"
            }
            const requestUrl = SERVER_URL + VIDEOS_ENDPOINT + "?video-format=" + videoFormat;
            fetch(requestUrl, requestOptions)
                .then((resp) => resp.json())
                .then((data) => setVideoList(data['videos']));
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
        setTimeout(function(){
            refreshToken(cookies.token, setCookie);
            // Set hasValidToken to null so that it gets picked up by the hook
            setHasValidToken(null);
        }, tokenRefreshInterval);
    }, [tokenTTL]);

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

    function setVideoList(videoList) {
        setVideoFileNames(videoList);
        setSelectedVideoFile(videoList[0]);
        
    }

    function handleClick(videoFileName) {
        setSelectedVideoFile(videoFileName);
    }

    return (
        <div className="VideoList">
            <NavBar />
            <div className="videoContainer">
                <div className="videoList">
                    <React.Fragment>
                        <ul className="list-group">
                        {videoFileNames.map(videoFileName => (
                            <li>
                                <button value={videoFileName} onClick={event => handleClick(event.target.value)}>
                                    {videoFileName}
                                </button>
                            </li>
                        ))}
                        </ul>
                    </React.Fragment>
                </div>
                <div className="videoPlayer">
                    <VideoPlayer videoFileName={selectedVideoFile} token={cookies.token} />
                </div>
            </div>
        </div>
    );

};
