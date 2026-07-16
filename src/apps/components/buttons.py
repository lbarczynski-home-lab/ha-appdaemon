import json
from contextlib import suppress

class MqttButton:
    def __init__(self, mqtt_plugin, topic, on_single_click):
        self.mqtt = mqtt_plugin
        self.topic = topic
        self.on_single_click = on_single_click
        
        self.mqtt.listen_event(self.on_mqtt_message, "MQTT_MESSAGE", topic=self.topic)

    def on_mqtt_message(self, event_name, data, kwargs):
        with suppress(json.JSONDecodeError, AttributeError):
            if json.loads(data.get("payload", "")).get("action") == "single":
                self.on_single_click(self.topic)
