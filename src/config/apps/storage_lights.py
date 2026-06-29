import hassapi as hass

class StorageLightsAutomation(hass.Hass):

    STORAGE_DOORS = "binary_sensor.storage_doors"
    STORAGE_LIGHTS = "light.storage_main_light"

    def initialize(self):
        self.log("[Storage lights automation] Start")
        self.listen_state(self.on_doors_open, self.STORAGE_DOORS, new = "on")
        self.listen_state(self.on_doors_closed, self.STORAGE_DOORS, new = "off")

    def on_doors_open(self, entity, attribute, old, new, cb_args):
        self.log("[Storage lights automation] Doors opened, turning on lights")
        self.call_service("light/turn_on", entity_id = self.STORAGE_LIGHTS)

    def on_doors_closed(self, entity, attribute, old, new, cb_args):
        self.log("[Storage lights automation] Doors cloased, turning off lights")
        self.call_service("light/turn_off", entity_id = self.STORAGE_LIGHTS)
