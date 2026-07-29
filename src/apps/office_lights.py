import hassapi as hass

class OfficeLightsAutomation(hass.Hass):

    LOG_TAG = "[Office lights automation]"

    def initialize(self):
        self.log(f"{self.LOG_TAG} Start")
        self.home = self.get_app("home_model").home
        
        self.home.office.light_switch_additional_button.add_state_change_listener(self.on_switch_state_changed)
        self.home.office.vertical_rgb_lamp.add_state_change_listener(self.on_lamp_state_changed)

    def on_switch_state_changed(self, name, is_on):
        self.log(f"{self.LOG_TAG} Wall button changed to {is_on}, syncing vertical RGB lamp")
        self.home.office.vertical_rgb_lamp.set_state(is_on)

    def on_lamp_state_changed(self, name, is_on):
        self.log(f"{self.LOG_TAG} Lamp changed to {is_on}, syncing wall button")
        self.home.office.light_switch_additional_button.set_state(is_on)
