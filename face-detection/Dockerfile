FROM python:3.10-buster

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && \
    apt-get install -y ffmpeg libsm6 libxext6 cmake libgl1-mesa-glx libxkbcommon-x11-0 libxkbcommon0 -y \
    && rm -rf /var/lib/apt/lists/*

# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
COPY requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
   && rm -rf /tmp/pip-tmp

COPY src /face-detection/

# Don't allow core dump file to be created
RUN ulimit -c 0 

ENV MQTT_HOST= MQTT_PORT= MQTT_USERNAME= MQTT_CLIENT_NAME= USE_PI_CAMERA= MAX_FPS= SEND_FRAME_FREQUENCY=

ENTRYPOINT [ "python3", "-u" ]

CMD [ "/face-detection/run.py" ]