#!/bin/bash

sudo iwconfig wlan0 power off
python3 streamer.py --redis-url sec-cam-server
