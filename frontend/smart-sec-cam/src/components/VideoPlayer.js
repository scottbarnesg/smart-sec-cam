import React from "react";


const SERVER_URL = process.env.REACT_APP_API_URL
const VIDEOS_ENDPOINT = "/videos"

class VideoList extends React.Component {
    
    constructor(props){
        super(props);
        this.state = {
            videoFileNames: null,
        };
    }

    async setVideoList(vidoeList) {
        this.setState({
            videoFileNames: vidoeList,
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
                {this.state.videoFileNames.map((item, index) => (
                    <Item key={index} item={item} />
                ))}
            </div>
        );
    }

};

export default VideoList;