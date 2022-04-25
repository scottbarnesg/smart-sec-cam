import React from "react";
import { isIOS } from 'react-device-detect' 

import VideoPlayer from "./VideoPlayer";
import NavBar from "./NavBar";
import "./VideoList.css"


const SERVER_URL = "https://localhost:8443"
const VIDEOS_ENDPOINT = "/video-list"

class VideoList extends React.Component {
    
    constructor(props){
        super(props);
        this.state = {
            videoFileNames: [],
            selectedVideoFile: null,
        };
    }

    setVideoList(videoList) {
        console.log(videoList);
        this.setState({
            videoFileNames: videoList,
            selectedVideoFile: videoList[0],
        });
        
    }

    componentDidMount() {
        // Get room list
        let videoFormat = "webm";
        if (isIOS) {
            videoFormat = "mp4"
        }
        const requestUrl = SERVER_URL + VIDEOS_ENDPOINT + "?video-format=" + videoFormat;
        console.log(requestUrl);
        fetch(requestUrl)
            .then((resp) => resp.json())
            .then((data) => this.setVideoList(data['videos']));
    }

    handleClick(videoFileName) {
        this.setState({
            selectedVideoFile: videoFileName,
        });
    }

    render() {
        return (
            <div>
                <NavBar />
                <div className="videoContainer">
                    <div className="videoList">
                        <React.Fragment>
                            <ul className="list-group">
                            {this.state.videoFileNames.map(videoFileName => (
                                <li>
                                    <button value={videoFileName} onClick={event => this.handleClick(event.target.value)}>
                                        {videoFileName}
                                    </button>
                                </li>
                            ))}
                            </ul>
                        </React.Fragment>
                    </div>
                    <div className="videoPlayer">
                        <VideoPlayer videoFileName={this.state.selectedVideoFile} />
                    </div>
                </div>
            </div>
        );
    }

};

export default VideoList;