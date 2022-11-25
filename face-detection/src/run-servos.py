import time
import serial

from messaging.mqtt import MqttClient
from messaging.contracts import gestureRequestMessage, servoMovementMessage
from messaging.telemetry import TelemetryClient

from config import config

from lewansoul_lx16a import ServoController, Servo

SERIAL_PORT = '/dev/ttyUSB0'

controller = ServoController(
    serial.Serial(SERIAL_PORT, 115200, timeout=1),
)

mqtt_client = MqttClient('dobby-servos', config)

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

def printLocations():
    global telemetry
    payload = {
        "ts": time.time(),
        "pan": pan_servo.get_position(),
        "tilt": tilt_servo.get_position(),
        "rotate": rotate_servo.get_position()
    }
    telemetry.publish(payload)


def prepare_movement(servo: Servo, destination: int, threshold: int = 5):
    global telemetry

    # Smaller == faster
    SPEED_FACTOR = 4

    # Calculate the steps we need to traverse, always as a positive number
    distance = servo.get_position() - destination
    distance = distance if distance > 0 else distance * -1

    if distance > threshold:
        # Calculate the duration to spend on this movement and prepare it
        speed = distance * SPEED_FACTOR
        servo.move_prepare(destination, speed)
        
        telemetry.debug(f'Moving {distance} steps in {speed}ms',
                        f'Servo Id:{servo.__dict__["servo_id"]}')
        return speed


def move_to_destination(msg: servoMovementMessage):
    global mode, pan, tilt, rotate, pan_servo, rotate_servo, tilt_servo, telemetry

    telemetry.debug(
        f'Processing movement command - pan: {msg.pan} tilt: {msg.tilt} rotate: {msg.rotate}. Message age: {time.time() - msg.ts}ms', "Servo Movement")

    # Calculate the position to look from the centre position of 500x500y, always a positive number
    pan = 1000 - ((msg.pan * 2 - 500) * .25 + 500)
    tilt = 1000 - ((msg.tilt * 2 - 500) * .3 + 500)

    # Prepare the movements, including providing the 'dead-zone' for each
    # servo to prevent stuttering and micro movements
    pan_time: float = prepare_movement(pan_servo, pan, 30) or 0
    tilt_time: float = prepare_movement(tilt_servo, tilt, 10) or 0

    # Get the longest movement and convert from ms to seconds
    movement_time = (pan_time if pan_time > tilt_time else tilt_time) / 1000

    # Begin the movement
    controller.move_start()

    telemetry.debug(f'Movement Time: {movement_time}', 'Servo Movement')

    # Sleep while movement occurs, but allow interuption in the last tenth
    time.sleep(movement_time * 0.9)


def gesture_movement(msg: gestureRequestMessage):  # executed on phrase/ topic change
    global mode, pan, tilt, rotate, delay, pan_last, tilt_last, rotate_last, telemetry
    # get current position of all servos

    telemetry.debug(
        f'Processing gesture {msg.gesture_name} - pan: {msg.pan} tilt: {msg.tilt} rotate: {msg.rotate}. Message age: {time.time() - msg.ts}ms')

    # Set where we want to go
    pan = msg.pan
    tilt = msg.tilt
    rotate = msg.rotate
    delay = msg.duration_seconds

    # Record current positions
    time.sleep(0.1)
    pan_last = pan_servo.get_position()
    time.sleep(0.05)
    tilt_last = tilt_servo.get_position()
    time.sleep(0.05)
    rotate_last = rotate_servo.get_position()
    time.sleep(0.05)

    # Move servo to new position - take current position and add counts from payload, pan,tilt,rotate
    prepare_movement(pan_servo, int(pan_last+pan))
    time.sleep(0.05)
    prepare_movement(tilt_servo, int(tilt_last+tilt))
    time.sleep(0.05)
    prepare_movement(rotate_servo, int(rotate_last + rotate))
    time.sleep(0.05)
    #rotate_servo.move_prepare(int(rotate_last+rotate), 2000)
    time.sleep(0.05)

    # Begin the movement of the gesture
    controller.move_start()

    # Sleep for the duration the gesture required
    time.sleep(delay)

    # Prepare the return movement and get the longest movement duration
    pan_duration: float = prepare_movement(pan_servo, pan_last, 5)
    tilt_duration: float = prepare_movement(tilt_servo, tilt_last, 5)
    rotate_duration: float = prepare_movement(rotate_servo, rotate_last, 5)
    movement_time = max(pan_duration, tilt_duration, rotate_duration)

    # Return to original position and wait for the movement to complete
    controller.move_start()
    time.sleep(movement_time)


def mode_payload(payload: servoMovementMessage):
    if payload.mode == 'home':
        servo_move_home()
    elif payload.mode == 'servo':
        move_to_destination(payload)
    else:
        raise ValueError(payload.mode)


servo_move_home()

mqtt_client.subscribe('/servo-control', mode_payload)
mqtt_client.subscribe('/servo-gesture', gesture_movement)

telemetry = TelemetryClient(mqtt_client, "servo-controller")





while 1:
    #   print("mode : ", mode,"   pan : ", pan,"Tilt : ", tilt, "rotate : ", rotate,"delay : " ,delay)
    time.sleep(.5)
    printLocations()
#
