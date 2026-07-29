import hassapi as hass
from models.home import Home

class AmbientLightsAutomation(hass.Hass):

    def initialize(self):
        self.mqtt = self.get_plugin_api("MQTT")
        self.home = Home(self.log, self.mqtt)
        
        self.lights = [
            self.home.living_room.rtv_led_strip,
            self.home.living_room.bookshelf_led_strip,
            self.home.bedroom.lamp,
            self.home.office.vertical_rgb_lamp,
        ]
        
        self.home.hall.console_button.add_click_listener(self.on_button_click)
        self.home.bedroom.bedside_table_left_button.add_click_listener(self.on_button_click)
        self.home.bedroom.bedside_table_right_button.add_click_listener(self.on_button_click)
        self.home.hall.exit_button.add_click_listener(self.on_button_click)

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
