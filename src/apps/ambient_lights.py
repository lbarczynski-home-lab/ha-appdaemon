import hassapi as hass
from components.lights import Zigbee2MqttLight, GoveeMqttLight
from components.buttons import MqttButton

class AmbientLightsAutomation(hass.Hass):

    def initialize(self):
        self.mqtt = self.get_plugin_api("MQTT")
        self.lights = [
            Zigbee2MqttLight(self.log, self.mqtt, "RTV", "zigbee2mqtt/living_room_rtv_shelf_led_strip", "zigbee2mqtt/living_room_rtv_shelf_led_strip/set"),
            Zigbee2MqttLight(self.log, self.mqtt, "Bookshelf", "zigbee2mqtt/living_room_bookshelf_led_strip", "zigbee2mqtt/living_room_bookshelf_led_strip/set"),
            Zigbee2MqttLight(self.log, self.mqtt, "Bedroom Lamp", "zigbee2mqtt/bedroom_ambient_lamp", "zigbee2mqtt/bedroom_ambient_lamp/set"),
            GoveeMqttLight(self.log, self.mqtt, "Office Lamp", "gv2mqtt/light/27D0EEE3EEDAD052/state", "gv2mqtt/light/27D0EEE3EEDAD052/command"),
        ]
        self.buttons = [
            MqttButton(self.mqtt, "zigbee2mqtt/hall_console_button", self.on_button_click),
            MqttButton(self.mqtt, "zigbee2mqtt/bedroom_bedside_table_left_button", self.on_button_click),
            MqttButton(self.mqtt, "zigbee2mqtt/bedroom_bedside_table_right_button", self.on_button_click),
            MqttButton(self.mqtt, "zigbee2mqtt/hall_exit_button", self.on_button_click),
        ]

        self.log("[AmbientLightsAutomation] Initialized")

    def on_button_click(self, topic):
        self.log(f"[AmbientLightsAutomation] Single button click: {topic}")
        if any(light.is_on() for light in self.lights):
            self.log("[AmbientLightsAutomation] Turning off all lights")
            for light in self.lights:
                light.turn_off()
        else:
            self.log("[AmbientLightsAutomation] Turning on all lights")
            for light in self.lights:
                light.turn_on()
