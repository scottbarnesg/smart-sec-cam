import React from "react";
import io from "socket.io-client";
import "./ImageViewer.css";

const SERVER_URL = "https://localhost:8443"
let socket = io(SERVER_URL)

class ImageViewer extends React.Component {

    constructor(props){
        super(props)
        this.state = {
            srcBlob: null,
            oldUrl: null
        }
        socket.emit('join', {"room": this.props.room});
    }

    componentDidMount(){
        socket.on('image', (payload) => {
            if (payload.room === this.props.room){
                var image = new Blob( [ new Uint8Array( payload.data ) ], { type: "image/jpeg" } )
                this.setState({
                    oldUrl: this.state.srcBlob,
                    srcBlob: URL.createObjectURL( image )
                })
                if (this.state.oldUrl != null){
                    URL.revokeObjectURL(this.state.oldUrl)
                }
                image = null;
            }
        });
    }

    render() {
        return (
            <div className="imageviewer">
                <img src={this.state.srcBlob} alt={this.props.room} ></img>
            </div>
        );
    }

}

export default ImageViewer