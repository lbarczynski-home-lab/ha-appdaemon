import hassapi as hass

class LivingRoomLedStripsAutomation(hass.Hass):

    TV                  = "media_player.tv_salon"
    APPLE_TV            = "media_player.apple_tv_living_room"
    PLAYSTATION_5       = "media_player.playstation_5"

    TV_RTV_LED_STRIP    = "light.living_room_rtv_led_strip"
    BOOKSHELF_LED_STRIP = "light.living_room_bookshelf_led_strip"

    HOME_THEATRE_POWER  = "sensor.living_room_home_theatre_power"

    def initialize(self):
        # entites
        self.tv                  = self.get_entity(self.TV)
        self.apple_tv            = self.get_entity(self.APPLE_TV)
        self.ps5                 = self.get_entity(self.PLAYSTATION_5)

        # led strips
        self.rtv_led_strip       = self.get_entity(self.TV_RTV_LED_STRIP)
        self.bookshelf_led_strip = self.get_entity(self.BOOKSHELF_LED_STRIP)

        # power methers
        self.home_theatre_power  = self.get_entity(self.HOME_THEATRE_POWER)

        # setup listeners
        self.listen_state(self.update_state, self.TV)
        self.listen_state(self.update_state, self.APPLE_TV)
        self.listen_state(self.update_state, self.PLAYSTATION_5)

    def update_state(self, entity, attribute, old, new, cb_args):
        if old == new:
            return

        self.log(f"Entity '{entity}' state changed from '{old}' to '{new}'")

        if self.is_on():
            self.rtv_led_strip.turn_on(brightness = 254)
            self.bookshelf_led_strip.turn_on(brightness = 254)
        else:
            self.rtv_led_strip.turn_off()
            self.bookshelf_led_strip.turn_off()

    def is_on(self):
        power_str = self.home_theatre_power.get_state()

        try:
            power = int(float(power_str))
            if power < 100:
                return False
        except (ValueError, TypeError):
            self.log(f"Error! Unable to parse power meter value \"'{power_str}'\"")
            return False

        tv_state = self.tv.get_state().lower()
        apple_tv_state = self.apple_tv.get_state().lower()
        ps5_state = self.ps5.get_state().lower()

        inactive_states = ["off", "unknown", "unavailable", None, "standby"]

        tv_on = tv_state not in inactive_states
        apple_tv_on = apple_tv_state not in inactive_states
        ps5_on = ps5_state not in inactive_states

        return tv_on or apple_tv_on or ps5_on
