#!/bin/sh

if [ "${API_URL}" ]; then sed -i "s/localhost:8444/${API_URL}/g" /backend/build/static/js/*; fi

python smart_sec_cam/server/server.py --redis-url sec-cam-server --video-dir /backend/data/videos/