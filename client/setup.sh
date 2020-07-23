#!/bin/bash

hostname=$1
version=$2
ws_uri=$3
shared_secret=$4

hostnamectl set-hostname ${hostname:-quantum-lamps}
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
    avenmia/quantum-lamps-client:${version:-latest}

cat << 'EOF' > /etc/cron.hourly/docker-pull-lamps
#!/bin/bash
REGISTRY="registry.hub.docker.com"
REPOSITORY="quantum-lamps-client"

LATEST="`wget -qO- https://$REGISTRY/v1/repositories/$REPOSITORY/tags`"
LATEST=`echo $LATEST | sed "s/{//g" | sed "s/}//g" | sed "s/\"//g" | cut -d ' ' -f2`

RUNNING=`docker inspect "$REGISTRY/$REPOSITORY" | grep Id | sed "s/\"//g" | sed "s/,//g" |  tr -s ' ' | cut -d ' ' -f3`

if [ "$RUNNING" != "$LATEST" ];then
    docker pull $REGISTRY/$REPOSITORY
    docker restart quantum-lamps-client
    echo y | docker system prune -a
fi
EOF

chmod +x /etc/cron.hourly/docker-pull-lamps

reboot
