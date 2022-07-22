import ReactPlayer from 'react-player'

const SERVER_URL = "https://localhost:8443"
const VIDEO_ENDPOINT = "/api/video/"

export default function VideoPlayer(props) {
    const videoUrl = SERVER_URL + VIDEO_ENDPOINT + props.videoFileName + "?token=" + props.token;
    console.log(videoUrl);
    return (
        <ReactPlayer url={videoUrl} width="100%" height="90vh" controls={true} />
    );
}