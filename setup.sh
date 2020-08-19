#!/bin/bash

ws_uri=$1
shared_secret=$2
user_name=$3
version=$4

raspi-config nonint get_i2c
raspi-config nonint do_i2c 0
curl -fsSL https://get.docker.com | sh

docker run \
    --privileged \
    --net host \
    -d \
    --restart unless-stopped \
    --name quantum-lamps-client \
    -e WS_URI=$ws_uri \
    -e SHARED_SECRET=$shared_secret \
    -e USER_NAME=$user_name \
    avenmia/quantum-lamps-client:master

cat << 'EOF' > /etc/cron.hourly/docker-pull-lamps
#!/bin/bash
REGISTRY="registry.hub.docker.com"
REPOSITORY="quantum-lamps-client"
TAG="master"

RUNNING=`docker inspect "$REGISTRY/$REPOSITORY" | grep Id | sed "s/\"//g" | sed "s/,//g" |  tr -s ' ' | cut -d ' ' -f3`

docker pull $REGISTRY/$REPOSITORY

NEW=`docker inspect "$REGISTRY/$REPOSITORY" | grep Id | sed "s/\"//g" | sed "s/,//g" |  tr -s ' ' | cut -d ' ' -f3`

if [ "$RUNNING" != "$NEW" ];then
    docker restart quantum-lamps-client
    echo y | docker system prune -a
fi
EOF

chmod +x /etc/cron.hourly/docker-pull-lamps

reboot
