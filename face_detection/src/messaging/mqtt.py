import json

from paho.mqtt import client as mqtt_client

from config import Config

topic_bounding_box = "FaceCoords/BoundingBox"
topic_bounding_box_centre = "FaceCoords/BoundingBoxCentre"
topic_bounding_box_centre_x = "FaceCoords/BoundingBoxCentre_x"
topic_bounding_box_centre_y = "FaceCoords/BoundingBoxCentre_y"


class MqttClient(mqtt_client.Client):

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker as", self.client_id)
        else:
            print("Failed to connect, return code %d\n", rc)

    def __init__(self, client_id, config: Config) -> None:
        # Settings for client
        self.debugTopic = '/debug'
        self.client_id = client_id + '-' + config.MQTT_CLIENT_NAME

        # Create Client
        self.client = mqtt_client.Client(client_id)
        if config.MQTT_USERNAME is not None:
            self.client.username_pw_set(
                config.MQTT_USERNAME, config.MQTT_PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.connect(config.MQTT_HOST, config.MQTT_PORT)
        self.client.loop_start()
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

    def publish_debug(self, message, component, category):
        payload = {
            "title": message,  # backward compatability for now
            "message": message,
            "component": component,
            "category": category
        }
        self.client.publish(self.debugTopic, payload=json.dumps(payload))
