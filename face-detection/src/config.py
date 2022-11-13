import os
from typing import Any, TypeVar
# from dotenv import load_dotenv

# load_dotenv()
# T = TypeVar('T')


class Config():
    def __init__(self) -> None:
        self.MQTT_CLIENT_NAME = self.get_required('MQTT_CLIENT_NAME')
        self.MQTT_HOST = self.get_required('MQTT_HOST')
        self.MQTT_PORT = self.get_required('MQTT_PORT', int, 1883)
        self.MQTT_USERNAME = self.get('MQTT_USERNAME')
        self.MQTT_PASSWORD = self.get('MQTT_PASSWORD')
        self.USE_PI_CAMERA = self.get_required('USE_PI_CAMERA', bool, False)
        self.MAX_FPS = self.get('MAX_FPS', int, 4)
        self.SEND_FRAME_FREQUENCY = self.get('SEND_FRAME_FREQUENCY', int, 2)

    def get(self, env_name, T: TypeVar = str, default_value: Any = None):
        var = os.getenv(env_name, default_value)
        try:
            if var is None:
                return None
            return T(var)
        except:
            return None

    def get_required(self, env_name: str, T: TypeVar = str, default_value: Any = None):
        var = self.get(env_name, T, default_value)
        if not isinstance(var, T):
            raise ValueError(
                env_name, 'Could not parse required argument. make sure it is set correctly in your environment variables')
        return var


config = Config()
