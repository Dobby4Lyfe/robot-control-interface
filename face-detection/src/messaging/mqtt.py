import json
import time

from paho.mqtt import client as mqtt_client

from config import Config
from messaging.contracts import gestureRequestMessage, servoMovementMessage, mqttMessage

topic_bounding_box = "FaceCoords/BoundingBox"
topic_bounding_box_centre = "FaceCoords/BoundingBoxCentre"
topic_bounding_box_centre_x = "FaceCoords/BoundingBoxCentre_x"
topic_bounding_box_centre_y = "FaceCoords/BoundingBoxCentre_y"



class MqttClient(mqtt_client.Client):

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker as", self.client_id)
        else:
            print(f"Failed to connect as {self.client_id}, return code {rc}")

    def __init__(self, client_id, config: Config) -> None:

        # Settings for client
        self.debugTopic = '/debug'
        self.client_id = client_id + '-' + config.MQTT_CLIENT_NAME
        self.callbacks = {}

        # Create Client
        self.client = mqtt_client.Client(client_id)

        if config.MQTT_USERNAME is not None:
            self.client.username_pw_set(
                config.MQTT_USERNAME, config.MQTT_PASSWORD)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(config.MQTT_HOST, config.MQTT_PORT)
        self.client.loop_start()
        self.client.max_inflight_messages_set = 1

        super().__init__()

    def publishLastFrame(self, lastFrame):
        if (type(lastFrame) == bytes):
            self.client.publish('FaceCoords/lastImage', lastFrame)

    # publish messages over the mqtt broker
    def publishMessages(self, left_rcvd, top_rcvd, right_rcvd, bottom_rcvd, midpoint_x, midpoint_y):
        msg = "x1 (top left) = " + str(left_rcvd) + " | " + "y1 (top left) = " + str(top_rcvd) + " | " + \
            "x2 (bottom right) = " + str(right_rcvd) + " | " + \
            "y2 (bottom right) = " + str(bottom_rcvd)
        msg_centre = "midpoint_x = " + \
            str(midpoint_x) + " | " + "midpoint_y = " + str(midpoint_y)
        msg_centre_x = midpoint_x
        msg_centre_y = midpoint_y
        result = self.client.publish(topic_bounding_box, msg)
        result = self.client.publish(topic_bounding_box_centre, msg_centre)
        result = self.client.publish(topic_bounding_box_centre_x, msg_centre_x)
        result = self.client.publish(topic_bounding_box_centre_y, msg_centre_y)
        status = result[0]
        if status == 0:
            status = status
        else:
            print("Failed to send messages via MQTT!!!")

    def publish_message(self, topic: str, message: mqttMessage):
        self.client.publish(topic, json.dumps(message.__dict__))

    def publish_debug(self, message, component, category, level):
        payload = {
            "title": message,  # backward compatability for now
            "message": message,
            "component": component,
            "category": category,
            "level": level
        }
        self.client.publish(self.debugTopic, payload=json.dumps(payload))

    def subscribe(self, topic, callback):
        print('subscribing to' + topic)
        self.callbacks[topic] = callback
        self.client.subscribe(topic)
        

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload)
        except Exception as ex:
            print(ex)
            payload = {
                "topic": msg.topic,
                "payload": msg.payload.decode()
            }
        
        

        if msg.topic == '/servo-control':
            payload = servoMovementMessage(**json.loads(msg.payload))
            if ((time.time() - payload.ts) > .2):
                return

        if msg.topic == '/dobby/gesture' or msg.topic == '/servo-gesture':
            payload = gestureRequestMessage(**json.loads(msg.payload))
            if ((time.time() - payload.ts) > 2):
                return

        if msg.topic in self.callbacks:
            self.callbacks[msg.topic](payload)
