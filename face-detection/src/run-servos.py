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

global name, pan, tilt, rotate, delay, pan_last, tilt_last, rotate_last, movement_id
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

mqtt_client = MqttClient('dobby-servos', config)
telemetry = TelemetryClient(mqtt_client, "servo-controller")

telemetry.debug("Moving to home position","Servo Movement")
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


def calculate_distance(servo: Servo, destination: int) -> int:
    # Calculate the steps we need to traverse, always as a positive number
    distance = servo.get_position() - destination
    distance = distance if distance > 0 else distance * -1
    return int(distance)

def run_movement(pan_destination: int, tilt_destination: int, rotate_destination = None):
    global mode, pan_servo, rotate_servo, tilt_servo, telemetry

    # Calculate how far each servo must move
    pan_distance = calculate_distance(pan_servo, pan_destination)
    tilt_distance = calculate_distance(tilt_servo, tilt_destination)

    # Get the larger of the two distances
    furthest_distance = max(pan_distance, tilt_distance)

    # This is the number of milliseconds we will spend on each servo step
    # Smaller == faster
    SPEED_FACTOR = 5
    movement_time = int(furthest_distance * SPEED_FACTOR)

    # Prepare the servos to move, if they need to move far enough
    MINIMUM_PAN_DISTANCE = 40
    if (pan_distance > MINIMUM_PAN_DISTANCE):
        pan_servo.move_prepare(pan_destination, movement_time)
        telemetry.debug(
            f'Moving {pan_distance} steps in {movement_time}ms', "Servo Pan   ↔️ ")
 
    MINIMUM_TILT_DISTANCE = 15
    if (tilt_distance > MINIMUM_TILT_DISTANCE):
        tilt_servo.move_prepare(tilt_destination, movement_time)
        telemetry.debug(
            f'Moving {tilt_distance} steps in {movement_time}ms', "Servo Tilt  ↕️ ")

    # Begin the movement
    controller.move_start()

    # Sleep while movement occurs, but allow interuption in the last tenth
    time.sleep((movement_time / 1000))

def move_to_destination(msg: servoMovementMessage) -> None:
    global mode, pan_servo, rotate_servo, tilt_servo, telemetry
    
    telemetry.debug(
        f'Processing movement command - pan: {msg.pan} tilt: {msg.tilt} rotate: {msg.rotate}. Message age: {((time.time() - msg.ts) * 1000):.0f}ms', "Servo Movement")

    # Calculate the position to look from the centre position of 500x500y, always a positive number
    # Maximum range - ((requested value * scale from video pixels to steps - as an offset from centre) * proportion of the movement range we want to use + centre position)
    pan_destination = 1000 - ((msg.pan * 2 - 500) * .25 + 500)
    tilt_destination = 1000 - ((msg.tilt * 1.5 - 500) * .3 + 500)

    run_movement(pan_destination, tilt_destination)
    
    telemetry.debug(f'Movement Complete', 'Servo Movement')


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

    pan_destination = pan_last + pan
    tilt_destination = tilt_last + tilt

    run_movement(pan_destination, tilt_destination)

    time.sleep(1)

    run_movement(pan_last, tilt_last)


def mode_payload(payload: servoMovementMessage):
    if payload.mode == 'home':
        servo_move_home()
    elif payload.mode == 'servo':
        move_to_destination(payload)
    else:
        raise ValueError(payload.mode)


mqtt_client.subscribe('/servo-control', mode_payload)
mqtt_client.subscribe('/servo-gesture', gesture_movement)

while 1:
    #   print("mode : ", mode,"   pan : ", pan,"Tilt : ", tilt, "rotate : ", rotate,"delay : " ,delay)
    time.sleep(.5)
    printLocations()
#
