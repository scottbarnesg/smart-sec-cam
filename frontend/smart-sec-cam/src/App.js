import React from "react";
import ImageViewer from "./components/ImageViewer";
import NavBar from "./components/NavBar";

import './App.css';

import io from "socket.io-client";

const SERVER_URL = process.env.REACT_APP_API_URL
const ROOMS_ENDPOINT = "/rooms"
let socket = io(SERVER_URL)

class App extends React.Component {
    constructor(props){
        super(props)
        this.state = {
            rooms: [],
            components: [],
        }
    }

    updateRooms(rooms) {
        this.setState({
            rooms: Object.keys(rooms),
        }, () => {
            this.renderComponents();
            console.log(this.state.rooms);
        })
    }

    renderComponents() {
        let components = []
        for (const room_name of this.state.rooms) {
            components.push(<ImageViewer key={room_name} room={room_name}/>)
        }
        this.setState({
           components: components,
        });
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
                <NavBar />
                {this.state.components}
            </div>
        );
    }
}

export default App;
