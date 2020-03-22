FROM python:3.8

WORKDIR /usr/src/app
COPY . .

RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

CMD [ "python3", "qyantum-lamps.py" ]