# Self-Hosted Home Security Camera System

A privacy-focused, intelligent security camera system.

## Features:
- Multi-camera support w/ minimal configuration. Supports USB cameras and the Raspberry Pi camera module.
- Motion detection that automatically saves videos.
- Encrypted in transit, both from the cameras to the server and the server to your browser.
- Self-Hosted
- Free and Open Source

## Setting up the server

#### Docker:
1. Clone this repository
2. Update the value of `REACT_APP_API_URL` in `frontend/smart-sec-cam/.env` to match the hostname of the server's host.
3. Generate SSL certificates: `./create-certs.sh`. Alternatively, you pay place your own certs in the `certs` dir
4. Build and run the docker containers: `docker-compose up -d --build`

## Adding a camera

#### Installation:

NOTE: These instructions assume you are deploying to a raspberry pi running Raspbian OS.

0. Install the `python3-opencv` package and dependencies: `sudo apt-get install python3-opencv libatlas-base-dev`
1. Clone this repository
2. Install the package: `cd backend && python3 -m pip install .[streamer]`
3. Update `--server_url` in `run.sh` to point at the host you deployed the server to.
4. In the Web UI, you should see live video from that camera.
