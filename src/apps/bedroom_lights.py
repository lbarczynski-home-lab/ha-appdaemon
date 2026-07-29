import hassapi as hass
from components.lights import HassLight

class BedroomLightsAutomation(hass.Hass):

    LOG_TAG = "[Bedroom lights automation]"
    BRIGHTNESS_LOW = 76
    BRIGHTNESS_HIGH = 254

    def initialize(self):
        self.log(f"{self.LOG_TAG} Start")
        home = self.get_app("home_model").home
        self.lamp = HassLight(self, "light.bedroom_rgb_lamp")
        self.hall_main_light = home.hall.main_light
        self._brightness_high = True
        
        home.bedroom.bedside_table_left_button.add_click_listener(self.on_button_click)
        home.bedroom.bedside_table_right_button.add_click_listener(self.on_button_click)

    def on_button_click(self, topic, action):
        self.log(f"{self.LOG_TAG} Button click '{action}' on {topic}")
        
        if action == "single":
            brightness = self.BRIGHTNESS_HIGH if self._brightness_high else self.BRIGHTNESS_LOW
            self.lamp.toggle(brightness=brightness)
                
        elif action == "double":
            self._brightness_high = not self._brightness_high
            brightness = self.BRIGHTNESS_HIGH if self._brightness_high else self.BRIGHTNESS_LOW
            self.lamp.turn_on(brightness=brightness)
            self.log(f"{self.LOG_TAG} Toggled brightness to {'HIGH' if self._brightness_high else 'LOW'}")
            
        elif action == "hold":
            self.log(f"{self.LOG_TAG} Toggling hall main light")
            self.hall_main_light.toggle()
