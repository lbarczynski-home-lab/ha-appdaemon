import mqttapi as mqtt
from models.home import Home

class StorageLightsAutomation(mqtt.Mqtt):

    LOG_TAG = "[Storage lights automation]"

    def initialize(self):
        self.log(f"{self.LOG_TAG} Start")
        self.home = Home(self.log, self)
        
        self.home.storage.doors.add_state_change_listener(self.on_doors_state_changed)

    def on_doors_state_changed(self, topic, is_open):
        if is_open:
            self.log(f"{self.LOG_TAG} Doors opened, turning on lights")
            self.home.storage.main_light.turn_on()
        else:
            self.log(f"{self.LOG_TAG} Doors closed, turning off lights")
            self.home.storage.main_light.turn_off()
