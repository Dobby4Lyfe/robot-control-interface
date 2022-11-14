
import json
import string

class mqttMessage():
    pass

class servoMovementMessage(mqttMessage):
    def __init__(self, tilt = 0, mode = 0, rotate = 0, pan = 0) -> None:
        self.tilt: int = tilt
        self.mode: string = mode or 'home'
        self.rotate: int = rotate
        self.pan: int = pan

message = servoMovementMessage()

if (issubclass(type(message), mqttMessage)):
    print('is subclass')
    print(json.dumps(message.__dict__))