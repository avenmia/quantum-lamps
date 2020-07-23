# quantum-lamps

[![CI/CD](https://github.com/avenmia/quantum-lamps/workflows/CI/CD/badge.svg)](https://github.com/avenmia/quantum-lamps/actions?query=workflow%3ACI%2FCD)

## Docker

### Client

```bash
client/setup.sh PI_HOSTNAME IMAGE_VERSION WS_URI SHARED_SECRET

# one off command
curl https://raw.githubusercontent.com/avenmia/quantum-lamps/master/client/setup.sh | bash -s quantum-lamps latest ws://quantum-lamps-server secret
```

### Server

```bash
docker run -d --restart unless-stopped -p 8080:8080 -e SHARED_SECRET=stuff -e PORT=8080 avenmia/quantum-lamps-server:latest
```
