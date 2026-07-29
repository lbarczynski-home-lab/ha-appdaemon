import json
from contextlib import suppress
from typing import Callable, List

ButtonClickListener = Callable[[str, str], None]

class MqttButton:
    def __init__(self, log, mqtt_plugin, topic):
        self.log = log
        self.mqtt = mqtt_plugin
        self.topic = topic
        self._listeners: List[ButtonClickListener] = []
        self.mqtt.listen_event(self.on_mqtt_message, "MQTT_MESSAGE", topic=self.topic)
        self.log(f"[{self.__class__.__name__}] Initialized for topic {self.topic}", level="INFO")

    def add_click_listener(self, listener: ButtonClickListener):
        self._listeners.append(listener)

    def remove_click_listener(self, listener: ButtonClickListener):
        if listener in self._listeners:
            self._listeners.remove(listener)

    def on_mqtt_message(self, event_name, data, kwargs):
        with suppress(json.JSONDecodeError, AttributeError):
            action = json.loads(data.get("payload", "")).get("action")
            if action:
                self.log(f"[MqttButton] Action '{action}' detected on {self.topic}", level="INFO")
                for listener in self._listeners:
                    listener(self.topic, action)
