import face_recognition
import imutils
import cv2
import time
import queue

from imutils.video import VideoStream
from imutils.video import FPS
from imutils import opencv2matplotlib
from PIL import Image

from .imageHelper import pil_image_to_byte_array
from messaging.mqtt import MqttClient
from messaging.telemetry import TelemetryClient

# We'll try and keep the update rate with dynamic sleep
MAX_FPS = 4

# Send the actual frame to node-red only this often
SEND_FRAME_EVERY = 2


def face_seek(imageQueue: queue.Queue, config, usePiCamera = True):
    fps = FPS()
    # Initializing the video stream

    time.sleep(2.0)
    mqttClient = MqttClient('dobby-face-processing', config)
    telemetry = TelemetryClient(mqttClient, "Face Detection Debug")

    telemetry.debug('Opening camera', "Face Detection Debug")
    video_stream = VideoStream(usePiCamera=usePiCamera, resolution=[320, 240], framerate=MAX_FPS).start()

    telemetry.debug('Starting face detection loop...')
    fps.start()
    frame_count = 0
    while True:
        # grab the frame from the threaded video stream and resize it
        # to 500px (to speedup processing)
        start = time.monotonic()
        frame = video_stream.read()
        frame_count = frame_count + 1
        # frame = imutils.resize(frame, width=500)
        frame = imutils.resize(frame, width=300)
        # Detect the fce boxes
        boxes = face_recognition.face_locations(frame)
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
            mqttClient.publishMessages(left, top, right, bottom,
                                       midpoint_x, midpoint_y)

        if (frame_count % SEND_FRAME_EVERY == 0):
            np_array_RGB = opencv2matplotlib(frame)
            image = Image.fromarray(np_array_RGB)  # PIL image
            last_frame = pil_image_to_byte_array(image)
            mqttClient.publishLastFrame(last_frame)

        # update the FPS counter
        fps.update()

        if (frame_count % 10 == 0):
            fps.stop()
            telemetry.debug("[Debug] approx. FPS: {:.2f}".format(
                fps.fps()), "Face Detection Debug")
            fps = FPS().start()

        updateSpeed = 1 / MAX_FPS
        delta = (time.monotonic() - start)
        sleep = .001 if delta >= updateSpeed else updateSpeed - delta
        time.sleep(sleep)
