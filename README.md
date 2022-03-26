# Self-Hosted Home Security Camera System

A privacy-focused, intelligent security camera system.

## Features:
- Multi-camera support w/ minimal configuration. Supports USB cameras and the Raspberry Pi camera module.
- Motion detection that automatically saves videos and lets you view them in the web app.
- Encrypted in transit, both from the cameras to the server and the server to your browser.
- Self-Hosted
- Free and Open Source ([GPLv3](LICENSE))

## Example screenshots

#### Multiple live video feeds on a single UI:
![](docs/Live_Video_Example.png)

#### Replay of recorded vidoes triggered by motion detection:
![](docs/Replay_Example.png)

## Setup

Sec-cam-server is designed to be deployed flexibly. There are 2 core components:
#### Camera: 
A device capable of capturing video and streaming to the server. Requirements:
- Must be able to run Python
- Must have a device capable of capturing video (e.g. a USB camera, webcam, or raspberry pi camera module)
- Must be able to communicate to the server over a network. During setup, you will point the camera at the server's
hostname or IP address.

#### Server: 
The server components aggregates feeds from the cameras, performs motion detection, and makes video available in a web
UI via an API. The server can be a standalone host, or can run on one of your cameras (e.g. a Raspberry Pi). Requirements:
- Must be able to run Docker.
- Must be accessible to your camera(s) over a network.

#### Example deployment configurations:

Example 1: A standalone server, with the hostname `sec-cam-server.local`, and 2 cameras, with hostnames `camera1.local` and 
`camera2.local`.
1. On `sec-cam-server.local`, follow the instructions in "Setting up the server". Replace `<server-hostname:server-port>` with 
`sec-cam-server.local:8443`.
2. On each camera, follow the instructions in "Adding a camera". In Step 3, `run.sh` should be updated to contain 
`--server_url sec-cam-server.local`.
3. The web UI with camera feeds will be available at `https://sec-cam-server.local:8443`

Example 2: 2 cameras  with hostnames `camera1.local` and `camera2.local`, with the "server" running `camera1.local`
1. On `camera1.local`, follow the steps to install the server.
2. On `camera1.local`, follow the steps to install the in "Adding a camera". In Step 3, `run.sh` should be updated to contain 
`--server_url localhost`.
3. On `camera2.local`, follow the steps to install the in "Adding a camera". In Step 3, `run.sh` should be updated to contain 
`--server_url camera1.local`.
4. The web UI with camera feeds will be available at `https://camera1.local:8443`

### Setting up the server

#### Docker:
0. Install Docker following [the instructions on their website](https://docs.docker.com/engine/install/ubuntu/).
1. Clone this repository
2. Generate SSL certificates: `./create-certs.sh`. Alternatively, you may place your own certs in the `certs` dir
3. Build and run the docker containers: `API_URL=<server-hostname:server-port> docker-compose up -d --build`. 
For example, if the server was running on the host `sec-cam-server` and port `8443` (the default), you should use 
`API_URL=sec-cam-server:8443`.
4. You should now be able to view the UI at `https://<server-hostname>:8443`. (NOTE: The web UI will be blank until you add a camera).

### Adding a camera

#### Installation:

NOTE: These instructions assume you are deploying to a Debian-based OS.

0. Install the `python3-opencv` package and dependencies: `sudo apt-get install python3-opencv libatlas-base-dev`
1. Clone this repository
2. Install the package: `cd backend && python3 -m pip install .[streamer]`. If you are using the Raspberry Pi camera
module, run `cd backend && python3 -m pip install .[streamer,picam]`.
3. Update `--server_url` in `run.sh` to point at the host you deployed the server to.
4. In the Web UI, you should see live video from that camera.
