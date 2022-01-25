import React from "react";
import VideoPlayer from "./VideoPlayer";
import "./VideoList.css"


const SERVER_URL = process.env.REACT_APP_API_URL
const VIDEOS_ENDPOINT = "/videos"

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
        fetch(SERVER_URL + VIDEOS_ENDPOINT)
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
        );
    }

};

export default VideoList;