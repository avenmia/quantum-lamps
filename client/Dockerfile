FROM arm32v6/python:3.8-alpine

ARG VERSION=dev
ENV VERSION="${VERSION}"

RUN apk update && \
    apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    py3-numpy \
    py3-rpigpio \
    py3-dotenv

ENV PYTHONPATH=/usr/lib/python3.8/site-packages

WORKDIR /app

RUN pip install \
    adafruit-circuitpython-lis3dh \
    adafruit-circuitpython-neopixel \
    adafruit-blinka \
    adafruit-circuitpython-busdevice \
    rpi_ws281x \
    websockets

COPY . .

CMD [ "python3", "quantum_lamps.py" ]
