# quantum-lamps

[![CI/CD](https://github.com/avenmia/quantum-lamps/workflows/CI/CD/badge.svg)](https://github.com/avenmia/quantum-lamps/actions?query=workflow%3ACI%2FCD)

## Docker

### Client

```bash
curl https://raw.githubusercontent.com/avenmia/quantum-lamps/master/client/setup.sh | bash -s ws://quantum-lamps-server secret username latest
```

### Server

```bash
docker run -d --restart unless-stopped -p 8080:8080 -e SHARED_SECRET=secret -e PORT=8080 avenmia/quantum-lamps-server:latest
```

## Raspberry Pi Deployment

Recommended steps before running setup script:

```bash
# Change password for user pi
passwd pi
# Update installed packages
apt-get update && apt-get upgrade -y
# Set locale, timezone, keyboard layout, hostname
raspi-config
# reboot
reboot
```
