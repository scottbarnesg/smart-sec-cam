import ReactPlayer from 'react-player'

const SERVER_URL = "https://localhost:8443"
const VIDEO_ENDPOINT = "/video/"

export default function VideoPlayer({videoFileName}) {
    const videoUrl = SERVER_URL + VIDEO_ENDPOINT + videoFileName;
    console.log(videoUrl);
    return (
        <ReactPlayer url={videoUrl} width="100%" height="90vh" controls={true} />
    );
}