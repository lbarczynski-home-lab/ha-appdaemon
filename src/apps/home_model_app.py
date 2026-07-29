import hassapi as hass
from models.home import Home

class HomeModelApp(hass.Hass):
    def initialize(self):
        self.mqtt = self.get_plugin_api("MQTT")
        self.home = Home(self.log, self.mqtt)
        self.log("[HomeModelApp] Digital Twin initialized.")
