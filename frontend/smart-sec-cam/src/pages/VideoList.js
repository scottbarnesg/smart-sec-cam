import React from "react";
import { useNavigate } from 'react-router-dom';

import { isIOS } from 'react-device-detect' 
import { useCookies } from 'react-cookie';

import VideoPlayer from "../components/VideoPlayer";
import NavBar from "../components/NavBar";

import { validateToken } from "../utils/ValidateToken";
import "./VideoList.css"


const SERVER_URL = "https://localhost:8443"
const VIDEOS_ENDPOINT = "/api/video/video-list"

export default function VideoList(props) {
    const [videoFileNames, setVideoFileNames] = React.useState([]);
    const [selectedVideoFile, setSelectedVideoFile] = React.useState(null);
    const [hasValidToken, setHasValidToken] = React.useState(null);
    const [cookies, setCookie] = useCookies(["token"]);
    const navigate = useNavigate();

    React.useEffect(() => {
        // Check cookie for valid token. If not, navigate to the login screen
        if (cookies.token == null) {
            navigate('/', { });
        }
        else {
            validateToken(cookies.token, setHasValidToken);
        }  
    }, []);

    React.useEffect(() => {
        if (hasValidToken) {
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
