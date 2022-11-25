from ast import Dict
import json
from .mqtt import MqttClient

class TelemetryClient():
    def __init__(self, mqtt: MqttClient, component_name: str) -> None:
        self.mqtt = mqtt
        self.component = component_name
    
    def debug(self, message: str, category = "Unknown"):
        self.mqtt.publish_debug('[Debug] ' + message, self.component, category)
        print(message)

    def publish(self, payload: Dict):
        self.mqtt.publish(f'/debug/{self.component}', payload=json.dumps(payload))