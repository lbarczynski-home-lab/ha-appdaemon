from typing import Callable

StateChangeCallback = Callable[[str, bool], None]

class MqttSwitch:
    def __init__(self, app_logger, mqtt_plugin, name, state_topic, command_topic):
        self.log = app_logger
        self.mqtt = mqtt_plugin
        self.name = name
        self.state_topic = state_topic
        self.command_topic = command_topic
        self._is_on = False
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
        self.log(f"[{self.__class__.__name__}] State changed to {'ON' if self._is_on else 'OFF'} on {self.state_topic}", level="INFO")
        for callback in self._listeners:
            callback(self.name, self._is_on)

    def on_mqtt_message(self, event_name, data, kwargs):
        raise NotImplementedError()

    def is_on(self) -> bool:
        return self._is_on

    def turn_on(self):
        self.set_state(True)

    def turn_off(self):
        self.set_state(False)

    def set_state(self, is_on: bool):
        raise NotImplementedError()

class TasmotaSwitch(MqttSwitch):
    TURN_ON_PAYLOAD = "ON"
    TURN_OFF_PAYLOAD = "OFF"
    
    def on_mqtt_message(self, event_name, data, kwargs):
        payload = data.get("payload", "").upper()
        new_state = payload == self.TURN_ON_PAYLOAD
        state_changed = self._is_on != new_state
        self._is_on = new_state
        
        if self._expected_state_changes > 0:
            self._expected_state_changes -= 1
        elif state_changed:
            self._notify_state_change()
    
    def set_state(self, is_on: bool):
        state_str = self.TURN_ON_PAYLOAD if is_on else self.TURN_OFF_PAYLOAD
        self.log(f"[{self.__class__.__name__}] Sending turn {state_str} command to {self.command_topic}", level="INFO")
        self._expected_state_changes += 1
        self.mqtt.mqtt_publish(self.command_topic, state_str)
