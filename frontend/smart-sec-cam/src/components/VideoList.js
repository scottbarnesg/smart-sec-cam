import React from "react";


const SERVER_URL = process.env.REACT_APP_API_URL
const VIDEOS_ENDPOINT = "/videos"

class VideoList extends React.Component {
    
    constructor(props){
        super(props);
        this.state = {
            videoFileNames: [],
        };
    }

    async setVideoList(videoList) {
        console.log(videoList);
        this.setState({
            videoFileNames: videoList,
        });
        
    }

    componentDidMount() {
        // Get room list
        fetch(SERVER_URL + VIDEOS_ENDPOINT)
            .then((resp) => resp.json())
            .then((data) => this.setVideoList(data['videos']));
    }

    render() {
        return (
            <div>
                <React.Fragment>
                    <ul className="list-group">
                    {this.state.videoFileNames.map(videoFileName => (
                        <li>
                            {videoFileName}
                        </li>
                    ))}
                    </ul>
                </React.Fragment>
            </div>
        );
    }

};

export default VideoList;