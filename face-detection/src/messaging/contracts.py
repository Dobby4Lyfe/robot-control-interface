
import json
import string
import time
from turtle import tilt

class mqttMessage():
    pass

# Used for directing the servo to a specific location
class servoMovementMessage(mqttMessage):
    def __init__(self, tilt = 0, mode = 0, rotate = 0, pan = 0, ts = None) -> None:
        self.tilt: int = tilt
        self.mode: string = mode or 'home'
        self.rotate: int = rotate
        self.pan: int = pan
        self.ts: int = ts or time.time() 

class gestureRequestMessage(mqttMessage):
    def __init__(self, tilt = 0, pan = 0, rotate = 0, ts = None, soundByte = None) -> None:
        self.tilt: int = tilt
        self.pan: int = pan
        self.rotate: int = rotate
        self.ts: int = ts or time.time() 
        self.soundByte: string = soundByte