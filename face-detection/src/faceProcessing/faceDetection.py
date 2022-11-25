import face_recognition
import imutils
import cv2
import time
import queue

from imutils.video import VideoStream
from imutils.video import FPS
from imutils import opencv2matplotlib
from PIL import Image

from config import Config

from .imageHelper import pil_image_to_byte_array
from messaging.mqtt import MqttClient
from messaging.telemetry import TelemetryClient
from messaging.contracts import servoMovementMessage


def face_seek(imageQueue: queue.Queue, config: Config, usePiCamera = True):
    fps = FPS()
    # Initializing the video stream

    time.sleep(2.0)
    mqttClient = MqttClient('dobby-face-processing', config)
    telemetry = TelemetryClient(mqttClient, "Face Detection")

    telemetry.debug('Opening camera', "Face Detection Debug")
    video_stream = VideoStream(usePiCamera=usePiCamera).start()

    telemetry.debug('Starting face detection loop...')
    fps.start()
    frame_count = 0
    while True:
        # grab the frame from the threaded video stream and resize it
        # to 500px (to speedup processing)
        start = time.monotonic()
        frame = video_stream.read()
        frame_count = frame_count + 1
        #frame = imutils.resize(frame, width=800, height=200)
        # frame = imutils.resize(frame, width=500)
        # Detect the fce boxes
        boxes = face_recognition.face_locations(frame, number_of_times_to_upsample=0)
        # names = []
        # loop over the recognized faces
        # left = x1, top = y1, right = x2, bottom = y2
        for (top, right, bottom, left) in (boxes):
            # print('face detected')
            # draw the predicted face name on the image - color is in BGR
            midpoint_x = int((left + right)/2)
            midpoint_y = int((top + bottom)/2)
            cv2.rectangle(frame, (left, top),
                          (right, bottom), (0, 255, 225), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, '', (left, y),
                        cv2.FONT_HERSHEY_SIMPLEX, .8, (0, 255, 255), 2)
            cv2.circle(frame, (midpoint_x, midpoint_y), 5, (0, 0, 255), -1)
            # Enable printing of co-ordinates to help with debugging
            # print("Left top co-ordinates - ", left,", ",top)
            # print("Bottom right co-ordinates - ", bottom,", ",right)
            # push messages out over MQTT
            if (imageQueue.full()):
                imageQueue.get(True)
                imageQueue.task_done()
            imageQueue.put(tuple([midpoint_x, midpoint_y]))
            telemetry.debug(f'Midpoint detected - x:{midpoint_x}  y:{midpoint_y}',"Face Detection Result")
            mqttClient.publishMessages(left, top, right, bottom,
                                       midpoint_x, midpoint_y)
            
        if (config.SEND_FRAME_FREQUENCY > 0 and frame_count % config.SEND_FRAME_FREQUENCY == 0):
            np_array_RGB = opencv2matplotlib(frame)
            image = Image.fromarray(np_array_RGB)  # PIL image
            last_frame = pil_image_to_byte_array(image)
            mqttClient.publishLastFrame(last_frame)

        # update the FPS counter
        fps.update()

        if (frame_count % 10 == 0):
            fps.stop()
            telemetry.debug("Approx. FPS: {:.2f}".format(
                fps.fps()), "Face Detection Debug")
            fps = FPS().start()

        updateSpeed = 1 / config.MAX_FPS
        delta = (time.monotonic() - start)
        sleep = .001 if delta >= updateSpeed else updateSpeed - delta
        time.sleep(sleep)
