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
        self.set_state(True)

    def turn_off(self):
        self.set_state(False)

    def set_state(self, is_on: bool):
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

    def set_state(self, is_on: bool):
        state_str = "ON" if is_on else "OFF"
        self.log(f"[{self.__class__.__name__}] Sending turn {state_str} command to {self.command_topic}", level="INFO")
        self._expected_state_changes += 1
        
        payload_dict = {"state": state_str}
        if is_on:
            payload_dict["brightness"] = 254
            
        self.mqtt.mqtt_publish(self.command_topic, json.dumps(payload_dict))


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

    def set_state(self, is_on: bool):
        state_str = "ON" if is_on else "OFF"
        self.log(f"[{self.__class__.__name__}] Sending turn {state_str} command to {self.command_topic}", level="INFO")
        self._expected_state_changes += 1
        
        payload_dict = {"state": state_str}
        if is_on:
            payload_dict["brightness"] = 100
            
        self.mqtt.mqtt_publish(self.command_topic, json.dumps(payload_dict))

class HassLight:
    def __init__(self, hass_app, entity_id):
        self.app = hass_app
        self.entity_id = entity_id
        self.log = hass_app.log
        self._listeners = []
        self.log(f"[{self.__class__.__name__}] Initialized for entity {self.entity_id}", level="INFO")
        
        self.app.listen_state(self._on_hass_state_change, self.entity_id)

    def _on_hass_state_change(self, entity, attribute, old, new, kwargs):
        is_on = (new == "on")
        self.log(f"[{self.__class__.__name__}] State changed to {new} for {self.entity_id}", level="INFO")
        for callback in self._listeners:
            callback(self.entity_id, is_on)

    def add_state_change_listener(self, callback) -> None:
        self._listeners.append(callback)

    def remove_state_change_listener(self, callback) -> None:
        if callback in self._listeners:
            self._listeners.remove(callback)

    def is_on(self) -> bool:
        return self.app.get_state(self.entity_id) == "on"

    def set_state(self, is_on: bool, brightness: int = 254):
        if is_on:
            self.log(f"[{self.__class__.__name__}] Sending turn ON command to {self.entity_id} with brightness {brightness}", level="INFO")
            self.app.turn_on(self.entity_id, brightness=brightness)
        else:
            self.log(f"[{self.__class__.__name__}] Sending turn OFF command to {self.entity_id}", level="INFO")
            self.app.turn_off(self.entity_id)

    def turn_on(self, brightness: int = 254):
        self.set_state(True, brightness=brightness)

    def turn_off(self):
        self.set_state(False)
