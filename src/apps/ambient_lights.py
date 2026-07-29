import hassapi as hass
from components.lights import HassLight

class AmbientLightsAutomation(hass.Hass):

    def initialize(self):
        self.home = self.get_app("home_model").home
        
        self.all_lights = [
            HassLight(self, "light.living_room_rtv_led_strip"),
            HassLight(self, "light.living_room_bookshelf_led_strip"),
            HassLight(self, "light.bedroom_rgb_lamp"),
            HassLight(self, "light.office_floor_rgb_lamp"),
        ]
        
        self.home.hall.console_button.add_click_listener(self.on_button_click)
        self.home.hall.exit_button.add_click_listener(self.on_button_click)

        self.log("[AmbientLightsAutomation] Initialized")

    def _toggle_lights(self, lights):
        is_any_on = any(light.is_on() for light in lights)
        self.log(f"[AmbientLightsAutomation] Turning {'off active' if is_any_on else 'on inactive'} lights")
        for light in lights:
            if light.is_on() == is_any_on:
                light.toggle()

    def on_button_click(self, topic, action):
        if action != "single":
            return
        self.log(f"[AmbientLightsAutomation] Single button click: {topic}")
        self._toggle_lights(self.all_lights)
