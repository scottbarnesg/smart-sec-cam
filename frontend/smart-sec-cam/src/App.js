import React from "react";
import ImageViewer from "./components/ImageViewer";

import './App.css';

import io from "socket.io-client";

const SERVER_URL = "http://sec-cam-server:5000"
const ROOMS_ENDPOINT = "/rooms"
let socket = io(SERVER_URL)

class App extends React.Component {
    constructor(props){
        super(props)
        this.state = {
            rooms: [],
        }
    }

    updateRooms(rooms) {
        this.setState({
            rooms: Object.keys(rooms),
        }, () => {
            console.log(this.state.rooms);
        })
    }


    componentDidMount(){
        // Get room list
        fetch(SERVER_URL + ROOMS_ENDPOINT)
        .then((resp) => resp.json())
        .then((data) => this.updateRooms(data['rooms']))
        // Configure socket
        socket.on('rooms', (payload) => {
            this.updateRooms(payload.rooms);
        });
    }

    render() {
        return (
            <div className="App">
                <ImageViewer room={"pi-sec-cam-1"} />
                <ImageViewer room={"pi-sec-cam-2"} />
            </div>
        );
    }
}

export default App;
