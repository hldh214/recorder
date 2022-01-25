FROM jrottenberg/ffmpeg:5.0-ubuntu

ARG TZ=Asia/Hong_Kong

ENV TZ ${TZ} \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY . .

RUN apt-get -y update && \
    apt-get install -y --no-install-recommends python3 python3-pip nodejs && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    pip3 install -r requirements.txt

ENTRYPOINT []

CMD ["python3", "-m", "recorder"]
