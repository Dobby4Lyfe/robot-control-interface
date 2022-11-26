from ast import Dict
import json
from .mqtt import MqttClient
from colorama import Fore, Style


class TelemetryClient():
    def __init__(self, mqtt: MqttClient, component_name: str) -> None:
        self.mqtt = mqtt
        self.component = component_name

    def debug(self, message: str, category="Unknown"):
        self.mqtt.publish_debug(message, self.component, category, "Debug")
        print(f'{Fore.BLUE + Style.DIM}[Debug] {category}: {message} {Style.RESET_ALL}')

    def error(self, message: str, category="Unknown"):
        if isinstance(message, Exception): message = str(message)
        self.mqtt.publish_debug(message, self.component, category, "Error")
        print(f'{Fore.RED}[Error] {category}: {message} {Style.RESET_ALL}')

    def publish(self, payload: Dict):
        self.mqtt.publish(f'/debug/{self.component}',
                          payload=json.dumps(payload))
