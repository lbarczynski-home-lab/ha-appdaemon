import mqttapi as mqtt
from models.home import Home

class OfficeLightsAutomation(mqtt.Mqtt):

    LOG_TAG = "[Office lights automation]"

    def initialize(self):
        self.log(f"{self.LOG_TAG} Start")
        self.home = Home(self.log, self)
        
        self.home.office.light_switch_additional_button.add_state_change_listener(self.on_switch_state_changed)

    def on_switch_state_changed(self, name, is_on):
        if is_on:
            self.log(f"{self.LOG_TAG} Wall button turned on, turning on vertical RGB lamp")
            self.home.office.vertical_rgb_lamp.turn_on()
        else:
            self.log(f"{self.LOG_TAG} Wall button turned off, turning off vertical RGB lamp")
            self.home.office.vertical_rgb_lamp.turn_off()
