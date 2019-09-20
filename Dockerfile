FROM alpine:3.10

WORKDIR /app

COPY requirements.txt /app

# credit: https://github.com/frol/docker-alpine-python3/blob/master/Dockerfile
RUN apk add --no-cache python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    \
   python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    \
    apk add --update --no-cache ffmpeg

RUN pip3 install -r requirements.txt

COPY . /app

CMD ['python3', '/app/recorder/recorder.py']
