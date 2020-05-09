# quantum-lamps

[![Node CI](https://github.com/avenmia/quantum-lamps/workflows/Node%20CI/badge.svg)](https://github.com/avenmia/quantum-lamps/actions?query=workflow%3A%22Node+CI%22) [![Python CI](https://github.com/avenmia/quantum-lamps/workflows/Python%20CI/badge.svg)](https://github.com/avenmia/quantum-lamps/actions?query=workflow%3A%22Python+CI%22) [![Docker CI](https://github.com/avenmia/quantum-lamps/workflows/Docker%20CI/badge.svg)](https://github.com/avenmia/quantum-lamps/actions?query=workflow%3A%22Docker+CI%22) [![Docker CD](https://github.com/avenmia/quantum-lamps/workflows/Docker%20CD/badge.svg)](https://github.com/avenmia/quantum-lamps/actions?query=workflow%3A%22Docker+CD%22)

## Docker

### Client

Newer verison of Raspbian expose the `/dev/gpiomem` device, which can be easily shared with the Docker container.
`--device /dev/gpiomem` enables the use of GPIO pins in the Docker container.
If the device is unavaliable due to running an older version or another reason, `--privledged` flag can also be used to enable the use of GPIO pins in the Docker container.

```sh
docker run --device /dev/gpiomem -d quantum-lamps-client
```

### Server

Docker configuration required to use packages:
https://help.github.com/en/packages/using-github-packages-with-your-projects-ecosystem/configuring-docker-for-use-with-github-packages

```sh
docker run -p 8080 -d quantum-lamps-server
```

## Azure

### Create Web App in Azure App Service

### Configure Application Settings

- Add `NODE_ENV=production` and other environment variables as needed.

### CD Deploy

Added GitHub Actions workflow to deploy to Azure Web App.
Will require AZURE_WEBAPP_PUBLISH_PROFILE secret to be configured in GitHub.

![Publish profile download screenshot](https://user-images.githubusercontent.com/5100938/73516915-98d2fc80-43bf-11ea-8727-6b2e0f7046a8.png)
The Azure Web App is also expected to have the environment variables configured (https://docs.microsoft.com/en-us/azure/app-service/configure-common#configure-app-settings)
