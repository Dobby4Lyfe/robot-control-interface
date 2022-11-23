#! /usr/bin/python
from ast import While
import json
import time
import threading
import queue
from typing import Dict

from config import Config, config
from messaging.contracts import gestureRequestMessage, servoMovementMessage
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

def process_gesture(msg: gestureRequestMessage):
    print(json.dumps(msg.__dict__))
    imageQueue.put(msg)

mqtt_client.subscribe('/dobby/gesture', process_gesture)

while PROCESS:
    time.sleep(.5)
    telemetry.debug('Current State: {state}'.format(
        state=dobby.current_state), "Control Flow")
    try:
        if imageQueue.not_empty and not dobby.is_gesturing:
            queuedMessage = imageQueue.get(True, timeout=0.1)
            if isinstance(queuedMessage, tuple):
                dobby.set_face_location(queuedMessage[0], queuedMessage[1])
                mqtt_client.publish_message('/servo-control', servoMovementMessage(pan = dobby.target_x,tilt = dobby.target_y, mode= 'servo'))
                imageQueue.task_done()
            elif isinstance(queuedMessage, gestureRequestMessage):
                mqtt_client.publish_message('/servo-gesture',queuedMessage)
                dobby.set_gesturing(queuedMessage)
            else:
                dobby.set_no_face()
    except (queue.Empty):
        dobby.set_no_face()

print('Stop Processing')