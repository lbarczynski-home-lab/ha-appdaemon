import hassapi as hass
import json

class AmbientLightsAutomation(hass.Hass):

    BEDROOM_RGB_LAMP = "light.bedroom_rgb_lamp"
    OFFICE_FLOOR_RGB_LAMP = "light.office_floor_rgb_lamp"
    TV_RTV_LED_STRIP = "light.living_room_rtv_led_strip"
    BOOKSHELF_LED_STRIP = "light.living_room_bookshelf_led_strip"

    def initialize(self):
        self.mqtt = self.get_plugin_api("MQTT")

        self.rtv_led_strip = self.get_entity(self.TV_RTV_LED_STRIP)
        self.bookshelf_led_strip = self.get_entity(self.BOOKSHELF_LED_STRIP)
        self.bedroom_rgb_lamp = self.get_entity(self.BEDROOM_RGB_LAMP)
        self.office_floor_rgb_lamp = self.get_entity(self.OFFICE_FLOOR_RGB_LAMP)

        self.buttons = [
            "zigbee2mqtt/hall_console_button",
            "zigbee2mqtt/bedroom_bedside_table_left_button",
            "zigbee2mqtt/bedroom_bedside_table_right_button",
            "zigbee2mqtt/hall_exit_button",
        ]

        for topic in set(self.buttons):
            self.mqtt.listen_event(self.on_button_click, "MQTT_MESSAGE", topic=topic)

        self.log("[AmbientLightsAutomation] Initialized")

    def on_button_click(self, event_name, data, kwargs):
        payload = data.get("payload", "")

        action = payload
        if payload.startswith("{"):
            try:
                action = json.loads(payload).get("action", "")
            except json.JSONDecodeError:
                pass

        if action == "single":
            self.log(
                f"[AmbientLightsAutomation] Single button click: {data.get('topic')}"
            )
            self.process_lights_logic()

    def process_lights_logic(self):
        if self.are_lights_on():
            self.log("[AmbientLightsAutomation] Turning off all lights")
            for light in self.ambient_ligts():
                light.turn_off()
        else:
            self.log("[AmbientLightsAutomation] Turning on all lights")
            for light in self.ambient_ligts():
                light.turn_on(brightness=255)

    def are_lights_on(self):
        for light in self.ambient_ligts():
            if self.is_light_active(light):
                return True
        return False

    def is_light_active(self, entity) -> bool:
        if entity.get_state().lower() != "on":
            return False

        brightness = entity.get_state(attribute="brightness") or 0
        return brightness > 0

    def ambient_ligts(self):
        return [
            self.rtv_led_strip,
            self.bookshelf_led_strip,
            self.bedroom_rgb_lamp,
            self.office_floor_rgb_lamp,
        ]
