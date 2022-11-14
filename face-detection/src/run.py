#! /usr/bin/python
from ast import While
import time
import threading
import queue
from typing import Dict

from config import Config, config
from messaging.mqtt import MqttClient
from messaging.telemetry import TelemetryClient
from stateMachine import Dobby
from faceProcessing.faceDetection import face_seek

# Pi Camera
# If you are using the Pi Camera, then set this to True
USE_PI_CAMERA = False
PROCESS = True


def start_face_detection(image_queue: queue.Queue):

    detection_thread = threading.Thread(
        target=face_seek, args=([image_queue, config, USE_PI_CAMERA]), daemon=True)
    detection_thread.start()
    return detection_thread

def process_control(msg: Dict):
    global PROCESS
    PROCESS = bool(msg['process'])
    global config
    config.SEND_FRAME_FREQUENCY = int(msg['sendFrames'])

mqtt_client = MqttClient('dobby-control', config)
telemetry = TelemetryClient(mqtt_client, 'dobby-control')
dobby = Dobby(telemetry)

imageQueue = queue.Queue(2)
faceDetectionThread = start_face_detection(imageQueue)

mqtt_client.subscribe('/face-detection/control/process', process_control)

while PROCESS:
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

print('Stop Processing')