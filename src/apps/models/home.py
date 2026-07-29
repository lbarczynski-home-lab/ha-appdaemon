from components.lights import Zigbee2MqttLight, GoveeMqttLight
from components.buttons import MqttButton
from components.switch import TasmotaSwitch
from components.sensors import MqttContactSensor

class Room:
    def __init__(self, log, mqtt):
        self.log = log
        self.mqtt = mqtt

class LivingRoom(Room):
    def __init__(self, log, mqtt):
        super().__init__(log, mqtt)
        self.rtv_led_strip = Zigbee2MqttLight(log, mqtt, "RTV", "zigbee2mqtt/living_room_rtv_shelf_led_strip", "zigbee2mqtt/living_room_rtv_shelf_led_strip/set")
        self.bookshelf_led_strip = Zigbee2MqttLight(log, mqtt, "Bookshelf", "zigbee2mqtt/living_room_bookshelf_led_strip", "zigbee2mqtt/living_room_bookshelf_led_strip/set")

class Office(Room):
    def __init__(self, log, mqtt):
        super().__init__(log, mqtt)
        self.vertical_rgb_lamp = GoveeMqttLight(log, mqtt, "Office Vertical RGB Lamp", "gv2mqtt/light/27D0EEE3EEDAD052/state", "gv2mqtt/light/27D0EEE3EEDAD052/command")
        self.light_switch_additional_button = TasmotaSwitch(log, mqtt, "Office Right Button", "iot/tasmota/office_light/stat/POWER2", "iot/tasmota/office_light/cmnd/POWER2")

class Bedroom(Room):
    def __init__(self, log, mqtt):
        super().__init__(log, mqtt)
        self.lamp = Zigbee2MqttLight(log, mqtt, "Bedroom Lamp", "zigbee2mqtt/bedroom_ambient_lamp", "zigbee2mqtt/bedroom_ambient_lamp/set")
        self.bedside_table_left_button = MqttButton(log, mqtt, "zigbee2mqtt/bedroom_bedside_table_left_button")
        self.bedside_table_right_button = MqttButton(log, mqtt, "zigbee2mqtt/bedroom_bedside_table_right_button")

class Hall(Room):
    def __init__(self, log, mqtt):
        super().__init__(log, mqtt)
        self.console_button = MqttButton(log, mqtt, "zigbee2mqtt/hall_console_button")
        self.exit_button = MqttButton(log, mqtt, "zigbee2mqtt/hall_exit_button")

class Storage(Room):
    def __init__(self, log, mqtt):
        super().__init__(log, mqtt)
        self.doors = MqttContactSensor(log, mqtt, "zigbee2mqtt/storage_doors")
        self.main_light = TasmotaSwitch(log, mqtt, "Storage Light", "iot/tasmota/bathroom_light/stat/POWER", "iot/tasmota/bathroom_light/cmnd/POWER")

class Home:
    def __init__(self, log, mqtt):
        self.living_room = LivingRoom(log, mqtt)
        self.office = Office(log, mqtt)
        self.bedroom = Bedroom(log, mqtt)
        self.hall = Hall(log, mqtt)
        self.storage = Storage(log, mqtt)
