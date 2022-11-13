#! /usr/bin/python
import time
import threading
import queue

from config import config
from messaging.mqtt import MqttClient
from messaging.telemetry import TelemetryClient
from stateMachine import Dobby
from faceProcessing.faceDetection import face_seek

# Pi Camera
# If you are using the Pi Camera, then set this to True
USE_PI_CAMERA = False


def start_face_detection(image_queue: queue.Queue):

    detection_thread = threading.Thread(
        target=face_seek, args=([image_queue, config, USE_PI_CAMERA]), daemon=True)
    detection_thread.start()


mqtt_client = MqttClient('dobby-control', config)
telemetry = TelemetryClient(mqtt_client, 'dobby-control')
dobby = Dobby(telemetry)

imageQueue = queue.Queue(2)
start_face_detection(imageQueue)

while True:
    time.sleep(1)
    telemetry.debug('Current State: {state}'.format(
        state=dobby.current_state), "Control Flow")
    try:
        if imageQueue.not_empty:
            points = imageQueue.get(True, timeout=0.1)
            if isinstance(points, tuple):
                dobby.set_face_location(points[0], points[1])
                imageQueue.task_done()
            else:
                dobby.set_no_face()
    except (queue.Empty):
        dobby.set_no_face()
