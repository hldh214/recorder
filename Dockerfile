FROM jrottenberg/ffmpeg:6.1-vaapi2404

ARG PYPI_MIRROR=https://pypi.org/simple
ARG TZ=Asia/Hong_Kong

ENV TZ=${TZ} \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=$PYTHONPATH:/app

WORKDIR /app

COPY . .

RUN apt-get -y update && \
    apt-get install -y --no-install-recommends python3 python3-pip nodejs && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/* && \
    pip install -i ${PYPI_MIRROR} pipenv && \
    PIPENV_VENV_IN_PROJECT=1 pipenv sync --pypi-mirror ${PYPI_MIRROR} && \
    pipenv --clear && \
    rm -rf /tmp/* && \
    rm -rf /root/.local/* && \
    pip uninstall pipenv -y

ENTRYPOINT []

CMD ["python3", "-m", "recorder"]
