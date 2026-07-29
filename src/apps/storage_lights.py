import hassapi as hass

class StorageLightsAutomation(hass.Hass):

    LOG_TAG = "[Storage lights automation]"

    def initialize(self):
        self.log(f"{self.LOG_TAG} Start")
        self.home = self.get_app("home_model").home
        
        self.home.storage.doors.add_state_change_listener(self.on_doors_state_changed)

    def on_doors_state_changed(self, topic, is_open):
        self.log(f"{self.LOG_TAG} Doors changed to {'open' if is_open else 'closed'}, syncing lights")
        self.home.storage.main_light.set_state(is_open)
