import json
from contextlib import suppress
from typing import Callable, List

ContactChangeListener = Callable[[str, bool], None]

class MqttContactSensor:
    def __init__(self, log, mqtt_plugin, topic):
        self.log = log
        self.mqtt = mqtt_plugin
        self.topic = topic
        self._is_open = False
        self._listeners: List[ContactChangeListener] = []
        self.mqtt.listen_event(self.on_mqtt_message, "MQTT_MESSAGE", topic=self.topic)
        self.log(f"[{self.__class__.__name__}] Initialized for topic {self.topic}", level="INFO")

    def add_state_change_listener(self, listener: ContactChangeListener):
        self._listeners.append(listener)

    def remove_state_change_listener(self, listener: ContactChangeListener):
        if listener in self._listeners:
            self._listeners.remove(listener)

    def is_open(self) -> bool:
        return self._is_open

    def on_mqtt_message(self, event_name, data, kwargs):
        with suppress(json.JSONDecodeError, AttributeError, ValueError):
            payload = json.loads(data.get("payload", ""))
            if "contact" in payload:
                new_is_open = not payload["contact"]
                
                if self._is_open != new_is_open:
                    self.log(f"[MqttContactSensor] State changed on {self.topic}: {'Open' if new_is_open else 'Closed'}", level="INFO")
                    self._is_open = new_is_open
                    for listener in self._listeners:
                        listener(self.topic, self._is_open)
