#!/bin/sh

if [ "${API_URL}" ]; then sed -i "s/localhost:8443/${API_URL}/g" /backend/build/static/js/*; fi

python smart_sec_cam/server/server.py --redis-url redis --video-dir /backend/data/videos/