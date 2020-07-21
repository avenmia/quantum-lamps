#!/bin/bash

apt-get update
apt-get install -y curl
hostnamectl set-hostname quantum-lamps-1
raspi-config nonint get_i2c
raspi-config nonint do_i2c 0
curl -fsSL https://get.docker.com | sh

cat << EOF > .env
WS_URL=
SHARED_SECRET=
EOF

docker login docker.pkg.github.com

docker run \
    --privileged \
    --net host \
    -d \
    --restart unless-stopped \
    -v $(pwd)/.env:/app/.env \
    docker.pkg.github.com/avenmia/quantum-lamps/client:v6

reboot
