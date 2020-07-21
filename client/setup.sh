#!/bin/bash

apt-get update
apt-get install -y curl
raspi-config nonint get_i2c
raspi-config nonint do_i2c 0
curl -fsSL https://get.docker.com | sh

curl -fsSL -o master.zip https://github.com/avenmia/quantum-lamps/archive/master.zip
unzip master.zip
rm master.zip
cd quantum-lamps-master/client
docker build -t quantum-lamps-client .

cat << EOF > .env
WS_URL=
SHARED_SECRET=
EOF

docker run --privileged --net host -d --restart unless-stopped -v $(pwd)/.env:/app/.env quantum-lamps-client
