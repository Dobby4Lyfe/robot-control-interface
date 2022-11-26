from tkinter import E
from typing import Tuple
import face_recognition
import imutils
import cv2
import time
import queue
import numpy as np

from imutils.video import VideoStream
from imutils.video import FPS
from imutils import opencv2matplotlib
from PIL import Image


from config import Config

from .imageHelper import pil_image_to_byte_array
from messaging.mqtt import MqttClient
from messaging.telemetry import TelemetryClient


def face_seek(imageQueue: queue.Queue, config: Config, usePiCamera=True):
    mqtt = None
    video_stream = None
    telemetry = None
    try:
        fps = FPS()
        # Initializing the video stream

        time.sleep(2.0)
        mqtt = MqttClient('dobby-face-processing', config)
        telemetry = TelemetryClient(mqtt, "Face Detection")

        telemetry.debug('Opening camera', "Control")
        video_stream = VideoStream(usePiCamera=False).start()

        telemetry.debug('Starting face detection loop', "Control")
        fps.start()
        frame_count = 0
        last_face = [None, None]
        while True:
            try:
                # grab the frame from the threaded video stream and resize it
                # to 500px (to speedup processing)
                start = time.monotonic()
                frame = video_stream.read()
                frame_count = frame_count + 1
                #frame = imutils.resize(frame, width=800, height=200)
                # frame = imutils.resize(frame, width=500)
                # Detect the fce boxes
                boxes = face_recognition.face_locations(
                    frame, number_of_times_to_upsample=0)

                if len(boxes) > 0:
                    telemetry.debug(f'Found {len(boxes)} faces', "Loop")

                ordered_faces = list()
                if (len(boxes) > 1):
                    for (top, right, bottom, left) in (boxes):
                        new_face = [int((left + right)/2),
                                    int((top + bottom)/2)]
                        distance = np.sqrt(
                            np.sum(np.square(np.array(last_face) - np.array(new_face))))
                        ordered_faces.append(
                            (top, right, bottom, left, distance))
                    ordered_faces.sort(key=lambda box: box[4])
                    telemetry.debug(f'Ordered faces {ordered_faces}', "Loop")
                elif (len(boxes) == 1):
                    ordered_faces.append(
                        (boxes[0][0], boxes[0][1], boxes[0][2], boxes[0][3], 0))

                # names = []
                # loop over the recognized faces
                # left = x1, top = y1, right = x2, bottom = y2
                closest_face = True
                for (top, right, bottom, left, distance) in ordered_faces:
                    # print('face detected')
                    # draw the predicted face name on the image - color is in BGR
                    midpoint_x = int((left + right)/2)
                    midpoint_y = int((top + bottom)/2)
                    outline_color = (
                        0, 255, 0) if closest_face else (0, 255, 225)

                    cv2.rectangle(frame, (left, top),
                                  (right, bottom), outline_color, 2)

                    # y = top - 15 if top - 15 > 15 else top + 15
                    # cv2.putText(frame, '', (left, y),
                    #             cv2.FONT_HERSHEY_SIMPLEX, .8, (0, 255, 255), 2)
                    cv2.circle(frame, (midpoint_x, midpoint_y),
                               5, (0, 0, 255), -1)

                    # Enable printing of co-ordinates to help with debugging
                    # print("Left top co-ordinates - ", left,", ",top)
                    # print("Bottom right co-ordinates - ", bottom,", ",right)
                    # push messages out over MQTT

                    if closest_face:
                        if (imageQueue.full()):
                            try:
                                imageQueue.get(True)
                                imageQueue.task_done()
                            except queue.Empty:
                                pass
                        try:
                            imageQueue.put(tuple([midpoint_x, midpoint_y]))
                            mqtt.publishMessages(left, top, right, bottom,
                                                 midpoint_x, midpoint_y)
                            last_face = [midpoint_x, midpoint_y]
                            telemetry.debug(
                                f'Sent new target at x:{midpoint_x} y:{midpoint_y}', "Loop")
                        except queue.Full as ex:
                            telemetry.error(
                                f'Could not send new face to queue {ex}', "Loop")
                        closest_face = False

                if (config.SEND_FRAME_FREQUENCY > 0 and frame_count % config.SEND_FRAME_FREQUENCY == 0):
                    np_array_RGB = opencv2matplotlib(frame)
                    image = Image.fromarray(np_array_RGB)  # PIL image
                    last_frame = pil_image_to_byte_array(image)
                    mqtt.publishLastFrame(last_frame)

                # update the FPS counter
                fps.update()

                if (frame_count % 10 == 0):
                    fps.stop()
                    telemetry.debug(f'Approx. FPS: {fps.fps():.2f}', "Loop")
                    fps = FPS().start()

                updateSpeed = 1 / config.MAX_FPS
                delta = (time.monotonic() - start)
                sleep = .001 if delta >= updateSpeed else updateSpeed - delta
                time.sleep(sleep)
            except Exception as ex:
                telemetry.error(ex, "Loop")
    except Exception as ex:
        try:
            video_stream.stop()
            time.sleep(5)
        finally:
            pass
        try:
            telemetry.error("Face detection process failed", "Control")
        finally:
            try:
                mqtt.disconnect()
            finally:
                pass
        raise ex
