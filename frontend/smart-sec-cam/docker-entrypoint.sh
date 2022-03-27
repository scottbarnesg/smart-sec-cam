#!/bin/sh

if [ "${API_URL}" ]; then sed -i "s/localhost:8443/${API_URL}/g" /frontend/build/static/js/*; fi

serve -s build -l 3000 --ssl-cert ./certs/sec-cam-server.cert --ssl-key ./certs/sec-cam-server.key