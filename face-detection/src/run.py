#! /usr/bin/python
import time
import threading
import queue

from config import config
from messaging.contracts import gestureRequestMessage, servoMovementMessage
from messaging.mqtt import MqttClient
from messaging.telemetry import TelemetryClient
from dobby import Dobby
from faceProcessing.faceDetection import face_seek


COMPONENT = 'dobby-control'


def start_face_detection(process_queue: queue.Queue):

    detection_thread = threading.Thread(
        target=face_seek,
        args=([process_queue, config, config.USE_PI_CAMERA]),
        daemon=True)

    detection_thread.start()
    return detection_thread


def process_gesture(msg: gestureRequestMessage):
    telemetry.debug(f'Received gesture {msg.gesture_name}')
    try:
        image_queue.get(block=False)
        image_queue.task_done()
    except queue.Empty:
        pass
    finally:
        image_queue.put(msg)    


print(f'{COMPONENT} is starting.')

mqtt = MqttClient(COMPONENT, config)
telemetry = TelemetryClient(mqtt, COMPONENT)
mqtt.subscribe('/dobby/gesture', process_gesture)

image_queue = queue.Queue(1)
faceDetectionThread = start_face_detection(image_queue)

dobby = Dobby(telemetry)

PROCESS = True
while PROCESS:
    telemetry.debug(f'Current State: {dobby.current_state}', "Control Flow")
    try:
        if not dobby.is_gesturing:
            queued_message = image_queue.get(True, timeout=1)
            if isinstance(queued_message, tuple):
                dobby.set_face_location(queued_message[0], queued_message[1])
                
                mqtt.publish_message('/servo-control', servoMovementMessage(
                    pan=dobby.target_x, tilt=dobby.target_y, mode='servo'))
            elif isinstance(queued_message, gestureRequestMessage):
                mqtt.publish_message('/servo-gesture', queued_message)

                dobby.set_gesturing(queued_message)
            else:
                dobby.set_no_face()

            image_queue.task_done()
        else:
            time.sleep(.25)
    except queue.Empty:
        dobby.set_no_face()

telemetry.debug("Exiting gracefully", "Control Flow")
