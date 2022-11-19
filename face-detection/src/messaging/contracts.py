
import json
import string
import time

class mqttMessage():
    pass

class servoMovementMessage(mqttMessage):
    def __init__(self, tilt = 0, mode = 0, rotate = 0, pan = 0, ts = None) -> None:
        self.tilt: int = tilt
        self.mode: string = mode or 'home'
        self.rotate: int = rotate
        self.pan: int = pan
        self.ts: int = ts or time.time() 