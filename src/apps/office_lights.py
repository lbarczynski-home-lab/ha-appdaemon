import hassapi as hass
from components.lights import HassLight

class OfficeLightsAutomation(hass.Hass):

    LOG_TAG = "[Office lights automation]"

    def initialize(self):
        self.log(f"{self.LOG_TAG} Start")
        self.home = self.get_app("home_model").home
        self.lamp = HassLight(self, "light.office_floor_rgb_lamp")
        
        self.home.office.light_switch_additional_button.add_state_change_listener(self.on_switch_state_changed)
        self.lamp.add_state_change_listener(self.on_lamp_state_changed)

    def on_switch_state_changed(self, name, is_on):
        self.log(f"{self.LOG_TAG} Wall button changed to {is_on}, syncing vertical RGB lamp")
        self.lamp.set_state(is_on)

    def on_lamp_state_changed(self, name, is_on):
        self.log(f"{self.LOG_TAG} Lamp changed to {is_on}, syncing wall button")
        self.home.office.light_switch_additional_button.set_state(is_on)
