#!/bin/bash

apt-get update
apt-get install -y curl
hostnamectl set-hostname quantum-lamps-1
raspi-config nonint get_i2c
raspi-config nonint do_i2c 0
curl -fsSL https://get.docker.com | sh

docker run \
    --privileged \
    --net host \
    -d \
    --restart unless-stopped \
    -e WS_URL=ws://quantum-lamps-server \
    -e SHARED_SECRET=secret \
    avenmia/quantum-lamps-client:v0.6

reboot
