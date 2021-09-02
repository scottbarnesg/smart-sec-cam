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


    componentDidMount(){
        fetch(SERVER_URL + ROOMS_ENDPOINT)
        .then(resp => resp.json())
        .then(data => this.setState({
                rooms: data.get('rooms')
            })
        )
        .then(data => console.log(data.get('rooms')))
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
