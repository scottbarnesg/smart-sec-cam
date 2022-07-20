import React from "react";
import { isIOS } from 'react-device-detect' 

import VideoPlayer from "./VideoPlayer";
import NavBar from "./NavBar";
import "./VideoList.css"


const SERVER_URL = "https://localhost:8443"
const VIDEOS_ENDPOINT = "/video-list"

export default function VideoList(props) {
    const [videoFileNames, setVideoFileNames] = React.useState([]);
    const [selectedVideoFile, setSelectedVideoFile] = React.useState(null);

    React.useEffect(() => {
        // TODO: Check that we got a token from the props. If not, navigate to the login screen
        // Get room list
        let videoFormat = "webm";
        if (isIOS) {
            videoFormat = "mp4"
        }
        const requestUrl = SERVER_URL + VIDEOS_ENDPOINT + "?video-format=" + videoFormat;
        console.log(requestUrl);
        fetch(requestUrl)
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
                    <VideoPlayer videoFileName={selectedVideoFile} />
                </div>
            </div>
        </div>
    );

};
