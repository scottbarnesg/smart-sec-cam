import React from "react";
import { useNavigate, useLocation } from 'react-router-dom';

import { isIOS } from 'react-device-detect' 

import VideoPlayer from "./VideoPlayer";
import NavBar from "./NavBar";
import "./VideoList.css"


const SERVER_URL = "https://localhost:8443"
const VIDEOS_ENDPOINT = "/video-list"

export default function VideoList(props) {
    const [videoFileNames, setVideoFileNames] = React.useState([]);
    const [selectedVideoFile, setSelectedVideoFile] = React.useState(null);
    const location = useLocation();
    const navigate = useNavigate();

    React.useEffect(() => {
        // TODO: Check that we got a token from the props. If not, navigate to the login screen
        console.log(location);
        if (location.state == null || location.state.token == null) {
            navigate('/', { });
            return;
        }
        const requestOptions = {
            method: 'GET',
            headers: { 'x-access-token': location.state.token },
        };
        // Get room list
        let videoFormat = "webm";
        if (isIOS) {
            videoFormat = "mp4"
        }
        const requestUrl = SERVER_URL + VIDEOS_ENDPOINT + "?video-format=" + videoFormat;
        fetch(requestUrl. requestOptions)
            .then((resp) => resp.json())
            .then((data) => setVideoList(data['videos']));
    }, []);

    function setVideoList(videoList) {
        console.log(videoList);
        setVideoFileNames(videoList);
        setSelectedVideoFile(videoList[0]);
        
    }

    function handleClick(videoFileName) {
        setSelectedVideoFile(videoFileName);
    }

    return (
        <div>
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
                    <VideoPlayer videoFileName={selectedVideoFile} token={location.state.token} />
                </div>
            </div>
        </div>
    );

};
