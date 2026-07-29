import json
from typing import Callable

StateChangeCallback = Callable[[str, bool], None]

class MqttLight:
    def __init__(self, app_logger, mqtt_plugin, name, state_topic, command_topic):
        self.log = app_logger
        self.mqtt = mqtt_plugin
        self.name = name
        self.state_topic = state_topic
        self.command_topic = command_topic
        self._is_on = False
        self._brightness = 0
        self._expected_state_changes = 0
        self._listeners: list[StateChangeCallback] = []
        
        self.mqtt.listen_event(self.on_mqtt_message, "MQTT_MESSAGE", topic=self.state_topic)
        self.log(f"[{self.__class__.__name__}] Initialized for topic {self.state_topic}", level="INFO")

    def add_state_change_listener(self, callback: StateChangeCallback) -> None:
        self._listeners.append(callback)

    def remove_state_change_listener(self, callback: StateChangeCallback) -> None:
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_state_change(self):
        self.log(f"[{self.__class__.__name__}] State changed to {'ON' if self._is_on else 'OFF'}, brightness: {self._brightness} on {self.state_topic}", level="INFO")
        for callback in self._listeners:
            callback(self.name, self.is_on())

    def on_mqtt_message(self, event_name, data, kwargs):
        raise NotImplementedError()

    def is_on(self) -> bool:
        return self._is_on and self._brightness > 0

    def turn_on(self):
        raise NotImplementedError()

    def turn_off(self):
        raise NotImplementedError()


class Zigbee2MqttLight(MqttLight):
    def on_mqtt_message(self, event_name, data, kwargs):
        payload = data.get("payload", "")
        if not payload:
            return
        try:
            state_data = json.loads(payload)
            current_state_str = "ON" if self._is_on else "OFF"
            new_is_on = state_data.get("state", current_state_str).upper() == "ON"
            new_brightness = state_data.get("brightness", self._brightness)
            
            state_changed = self._is_on != new_is_on or self._brightness != new_brightness
            self._is_on = new_is_on
            self._brightness = new_brightness
            
            if self._expected_state_changes > 0:
                self._expected_state_changes -= 1
            elif state_changed:
                self._notify_state_change()
        except json.JSONDecodeError:
            pass

    def turn_on(self):
        self.log(f"[{self.__class__.__name__}] Sending turn ON command to {self.command_topic}", level="INFO")
        self._expected_state_changes += 1
        payload = json.dumps({"state": "ON", "brightness": 254})
        self.mqtt.mqtt_publish(self.command_topic, payload)

    def turn_off(self):
        self.log(f"[{self.__class__.__name__}] Sending turn OFF command to {self.command_topic}", level="INFO")
        self._expected_state_changes += 1
        payload = json.dumps({"state": "OFF"})
        self.mqtt.mqtt_publish(self.command_topic, payload)


class GoveeMqttLight(MqttLight):
    def on_mqtt_message(self, event_name, data, kwargs):
        payload = data.get("payload", "")
        if not payload:
            return
        try:
            state_data = json.loads(payload)
            current_state_str = "ON" if self._is_on else "OFF"
            new_is_on = state_data.get("state", current_state_str).upper() == "ON"
            new_brightness = state_data.get("brightness", self._brightness)
            
            state_changed = self._is_on != new_is_on or self._brightness != new_brightness
            self._is_on = new_is_on
            self._brightness = new_brightness
            
            if self._expected_state_changes > 0:
                self._expected_state_changes -= 1
            elif state_changed:
                self._notify_state_change()
        except json.JSONDecodeError:
            pass

    def turn_on(self):
        self.log(f"[{self.__class__.__name__}] Sending turn ON command to {self.command_topic}", level="INFO")
        self._expected_state_changes += 1
        payload = json.dumps({"state": "ON", "brightness": 100})
        self.mqtt.mqtt_publish(self.command_topic, payload)

    def turn_off(self):
        self.log(f"[{self.__class__.__name__}] Sending turn OFF command to {self.command_topic}", level="INFO")
        self._expected_state_changes += 1
        payload = json.dumps({"state": "OFF"})
        self.mqtt.mqtt_publish(self.command_topic, payload)
