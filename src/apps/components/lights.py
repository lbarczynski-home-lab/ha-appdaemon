import json

class MqttLight:
    def __init__(self, app_logger, mqtt_plugin, name, state_topic, command_topic):
        self.log = app_logger
        self.mqtt = mqtt_plugin
        self.name = name
        self.state_topic = state_topic
        self.command_topic = command_topic
        self._is_on = False
        self._brightness = 0
        
        self.mqtt.mqtt_subscribe(self.state_topic)
        self.mqtt.listen_event(self.on_mqtt_message, "MQTT_MESSAGE", topic=self.state_topic)

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
            self._is_on = state_data.get("state", current_state_str).upper() == "ON"
            self._brightness = state_data.get("brightness", self._brightness)
        except json.JSONDecodeError:
            pass

    def turn_on(self):
        payload = json.dumps({"state": "ON", "brightness": 254})
        self.mqtt.mqtt_publish(self.command_topic, payload)

    def turn_off(self):
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
            self._is_on = state_data.get("state", current_state_str).upper() == "ON"
            self._brightness = state_data.get("brightness", self._brightness)
        except json.JSONDecodeError:
            pass

    def turn_on(self):
        payload = json.dumps({"state": "ON", "brightness": 100})
        self.mqtt.mqtt_publish(self.command_topic, payload)

    def turn_off(self):
        payload = json.dumps({"state": "OFF"})
        self.mqtt.mqtt_publish(self.command_topic, payload)
