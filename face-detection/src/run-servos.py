# Servo file to control servo position
#   todo  face tracking mode AUTO


#  pan  ID=1  limitset 165 -500- 840   (offset -20)
#  tilt ID=3  limitset 350 -500- 600   (offset +30)
# rotate ID=2  limitset 389 -500- 622   (offset +60)

import time
from messaging.mqtt import MqttClient
from messaging.contracts import servoMovementMessage
from config import config
import json
import serial
from lewansoul_lx16a import ServoController, Servo

SERIAL_PORT = '/dev/ttyUSB0'

controller = ServoController(
    serial.Serial(SERIAL_PORT, 115200, timeout=1),
)

dobby = MqttClient('dobby-servos', config)

global name, pan, tilt, rotate, delay, pan_last, tilt_last, rotate_last
global mode
pan = 500
tilt = 500
rotate = 500
delay = 3
pan_last = 500  # set home position 500 for all servos
tilt_last = 500
rotate_last = 500
mode = 'home'

# define servo addressing
pan_servo = controller.servo(1)
rotate_servo = controller.servo(2)
tilt_servo = controller.servo(3)


def servo_move_home():
    # set servos to home position
    pan_servo.move(500, 1000)
    tilt_servo.move(500, 1000)
    rotate_servo.move(500, 1000)


def servo_move_destination(payload: servoMovementMessage):
    global mode, pan, tilt, rotate, pan_servo, rotate_servo, tilt_servo
    print(f'Age of message is {time.time() - payload.ts}')
    pan = 1000 - ((payload.pan * 2 - 500) * .25 + 500)
    tilt = 1000 - ((payload.tilt * 2 - 500) * .3 +500)
    print(f'Raw pan position {payload.pan} mapped to {pan}')
    print(f'Raw pan position {payload.tilt} mapped to {tilt}')
    # pan = 1000 - int((payload.pan) * 2)  # 0 to 800 pixels = 165 to 840 counts
    # tilt = int((payload.tilt)*.3)  # 0 to 600 pixels = 350 to 600 counts
    # rotate = payload.rotate
    distance = pan_servo.get_position() - pan
    if distance < 0:
        distance = distance * - 1
    speed = (distance / 100) * 400
    if (distance > 20):
        print(f'Moving {distance} steps in {speed}ms')
        pan_servo.move(pan, speed)
    tilt_servo.move(tilt, 500)
    time.sleep(1)


def servo_move_incremental(payload: servoMovementMessage):
    global mode, pan, tilt, rotate
    pan = pan + payload.pan
    tilt = tilt + payload.tilt
    rotate = rotate + payload.rotate
    print("mode is INCREMENTAL  pan : ", pan, " tilt : ", tilt)
    # time.sleep(1)


def servo_move(p=500, t=480, r=500):  # executed on mode/ topic change
    global mode, pan, tilt, rotate
    if mode == "home":
        pan_servo.move(p, 1000)
        tilt_servo.move(t, 1000)
        rotate_servo.move(r, 1000)
        print("mode is HOME  pan : ", p, " tilt : ", t, "rotate : ", r)
    if mode == "servo":  # this payload contains pixels not servo counts
        pan = int((pan-400)*.3)  # 0 to 800 pixels = 165 to 840 counts
        tilt = int((tilt-300)*.3)  # 0 to 600 pixels = 350 to 600 counts
        print("mode is SERVO   pan : ", pan, " tilt : ", tilt)
        playphrase()
    if mode == "inc":
        print("mode is INCREMENTAL  pan : ", pan, " tilt : ", tilt)
        playphrase()


def playphrase():  # executed on phrase/ topic change
    global mode, pan, tilt, rotate, delay, pan_last, tilt_last, rotate_last
    # get current position of all servos
    time.sleep(0.1)
    pan_last = pan_servo.get_position()
    time.sleep(0.05)
    tilt_last = tilt_servo.get_position()
    time.sleep(0.05)
    rotate_last = rotate_servo.get_position()
    time.sleep(0.05)
    print(pan_last, tilt_last, rotate_last)
    print(int(pan_last+pan), int(tilt_last+tilt))
    # move servo to new position -take current position and add counts from payload, pan,tilt,rotate
    pan_servo.move_prepare(int(pan_last+pan), 1000)
    time.sleep(0.05)
    tilt_servo.move_prepare(int(tilt_last+tilt), 1000)
    time.sleep(0.05)
    rotate_servo.move_prepare(500, 1000)
    time.sleep(0.05)
    #rotate_servo.move_prepare(int(rotate_last+rotate), 2000)
    time.sleep(0.05)
    controller.move_start()
    # move servos back to orig position (not required for inc"remental" function)
    if not (mode != "inc" or mode != "servo"):
        time.sleep(delay)
        pan_servo.move(pan_last, 1000)
        tilt_servo.move(tilt_last, 1000)
        rotate_servo.move(rotate_last, 1000)
        time.sleep(0.5)


def mode_payload(payload: servoMovementMessage):
    if payload.mode == 'home':
        servo_move_home()
    elif payload.mode == 'inc':
        servo_move_incremental(payload)
    elif payload.mode == 'servo':
        servo_move_destination(payload)
    else:
        raise ValueError(payload.mode)


def phrase_payload(msg):
    global pan, tilt, rotate, delay
    payload = json.loads(msg['payload'])
    pan = payload['pan']
    tilt = payload['tilt']
    rotate = payload['rotate']
    delay = payload['delay']
    playphrase()


servo_move_home()

dobby.subscribe('/servo-control', mode_payload)
# dobby.subscribe('/phrase', phrase_payload)

time.sleep(3)


while 1:
    #print("mode : ", mode,"   pan : ", pan,"Tilt : ", tilt, "rotate : ", rotate,"delay : " ,delay)
    time.sleep(20)
