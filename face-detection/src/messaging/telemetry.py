from .mqtt import MqttClient

class TelemetryClient():
    def __init__(self, mqtt: MqttClient, component_name: str) -> None:
        self.mqtt = mqtt
        self.component = component_name
    
    def debug(self, message: str, category = "Unknown"):
        self.mqtt.publish_debug(message, self.component, category)
        print(message)