# Self-Hosted Home Security Camera System

A self-hosted home security camera solution that lets you turn any linux system (e.g. a raspberry pi) into a smart security camera.

## Features:
- Multi-camera support w/ minimal configuration
- Motion detection that automatically saves videos.
- Self-Hosted
- Free and Open Source

## Setting up the server

#### Docker:
1. Clone this repository
2. Update the value of `REACT_APP_API_URL` in `frontend/smart-sec-cam/.env` to match the hostname of the server's host.
3. Build and run the docker containers: `./start-server.sh`

## Adding a camera

#### Installation:

NOTE: These instructions assume you are deploying to a raspberry pi running Raspbian OS.

1. Clone this repository
2. Install the requirements: `python3 -m pip install -r streamer/requirements.txt`
3. Install OpenCV. Here's a 
[helper script](https://github.com/scottbarnesg/Automated-OpenCV-Install/blob/master/opencv-py3-install.sh) 
for compiling it from source if needed.**
4. Update `--server_url` in `run.sh` to point at the host you deployed the server to.
5. In the Web UI, you should see live video from that camera.

** NOTE: If you have 1 GB of memory or less, you will need to increase the size of the swap on the host before compiling.