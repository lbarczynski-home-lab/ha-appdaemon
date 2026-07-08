import mqttapi as mqtt
import json

class StorageLightsAutomation(mqtt.Mqtt):

    LOG_TAG = "[Storage lights automation]"

    STORAGE_DOORS_STATE_TOPIC = "zigbee2mqtt/storage_doors"
    STORAGE_LIGHTS_CMND_TOPIC = "iot/tasmota/bathroom_light/cmnd/POWER"

    def initialize(self):
        self.log(f"{self.LOG_TAG} Start")
        self.listen_event(self.on_doors_message, "MQTT_MESSAGE", topic=self.STORAGE_DOORS_STATE_TOPIC)

    def on_doors_message(self, event_name, data, kwargs):
        payload_str = data.get("payload", "")
        if not payload_str:
            return

        try:
            payload = json.loads(payload_str)
        except json.JSONDecodeError as e:
            self.log(f"{self.LOG_TAG} Error parsing message: {payload_str}. Error: {e}")
            return

        if "contact" in payload:
            contact = payload["contact"]
            if contact is False:
                self.log(f"{self.LOG_TAG} Doors opened, turning on lights")
                self.mqtt_publish(self.STORAGE_LIGHTS_CMND_TOPIC, "ON")
            elif contact is True:
                self.log(f"{self.LOG_TAG} Doors closed, turning off lights")
                self.mqtt_publish(self.STORAGE_LIGHTS_CMND_TOPIC, "OFF")

