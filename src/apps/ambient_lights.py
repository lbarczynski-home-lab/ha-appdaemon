import hassapi as hass

class AmbientLightsAutomation(hass.Hass):

    def initialize(self):
        self.home = self.get_app("home_model").home
        
        self.all_lights = [
            self.home.living_room.rtv_led_strip,
            self.home.living_room.bookshelf_led_strip,
            self.home.bedroom.lamp,
            self.home.office.vertical_rgb_lamp,
        ]
        
        self.home.hall.console_button.add_click_listener(self.on_button_click)
        self.home.hall.exit_button.add_click_listener(self.on_button_click)
        self.home.bedroom.bedside_table_left_button.add_click_listener(self.on_button_click)
        self.home.bedroom.bedside_table_right_button.add_click_listener(self.on_button_click)

        self.log("[AmbientLightsAutomation] Initialized")

    def _toggle_lights(self, lights):
        if any(light.is_on() for light in lights):
            self.log("[AmbientLightsAutomation] Turning off active lights")
            for light in lights:
                if light.is_on():
                    light.turn_off()
        else:
            self.log("[AmbientLightsAutomation] Turning on inactive lights")
            for light in lights:
                if not light.is_on():
                    light.turn_on()

    def on_button_click(self, topic):
        self.log(f"[AmbientLightsAutomation] Single button click: {topic}")
        self._toggle_lights(self.all_lights)
