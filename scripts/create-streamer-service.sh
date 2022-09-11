#!/bin/bash

# Copy base file to the actual file
cp smart-sec-cam.base.service smart-sec-cam.service
# Set current user as user to run service as
echo "Setting user $USER as streamer service user..."
sed -i "/^User=/ s/$/$USER\n/" smart-sec-cam.service
# Use current path to set execution path for service file
echo "Setting execution path for streamer service..."
path=$(cd ../ && pwd)
echo "ExecStart=$path/smart_sec_cam/streamer/run.sh" >> smart-sec-cam.service
echo "WorkingDirectory=$path/smart_sec_cam/streamer/" >> smart-sec-cam.service
# Copy service file to systemd directory
echo "Copying service file to systemd service directory..."
sudo cp smart-sec-cam.service /etc/systemd/system/
# Enable and start service
echo "Enabling and starting service..."
sudo systemctl enable smart-sec-cam
sudo systemctl start smart-sec-cam
echo "Done!"