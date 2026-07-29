from components.lights import Zigbee2MqttLight, GoveeMqttLight
from components.buttons import MqttButton
from components.switch import TasmotaSwitch, ShellySwitch
from components.sensors import MqttContactSensor

class Room:
    def __init__(self, log, mqtt):
        self.log = log
        self.mqtt = mqtt

class LivingRoom(Room):
    def __init__(self, log, mqtt):
        super().__init__(log, mqtt)
        self.rtv_led_strip = Zigbee2MqttLight(
            app_logger=log, 
            mqtt_plugin=mqtt, 
            name="RTV", 
            state_topic="zigbee2mqtt/living_room_rtv_shelf_led_strip", 
            command_topic="zigbee2mqtt/living_room_rtv_shelf_led_strip/set"
        )
        self.bookshelf_led_strip = Zigbee2MqttLight(
            app_logger=log, 
            mqtt_plugin=mqtt, 
            name="Bookshelf", 
            state_topic="zigbee2mqtt/living_room_bookshelf_led_strip", 
            command_topic="zigbee2mqtt/living_room_bookshelf_led_strip/set"
        )

class Office(Room):
    def __init__(self, log, mqtt):
        super().__init__(log, mqtt)
        self.vertical_rgb_lamp = GoveeMqttLight(
            app_logger=log, 
            mqtt_plugin=mqtt, 
            name="Office Vertical RGB Lamp", 
            state_topic="gv2mqtt/light/27D0EEE3EEDAD052/state", 
            command_topic="gv2mqtt/light/27D0EEE3EEDAD052/command"
        )
        self.light_switch_additional_button = TasmotaSwitch(
            app_logger=log, 
            mqtt_plugin=mqtt, 
            name="Office Right Button", 
            state_topic="iot/tasmota/office_light/stat/POWER2", 
            command_topic="iot/tasmota/office_light/cmnd/POWER2"
        )

class Bedroom(Room):
    def __init__(self, log, mqtt):
        super().__init__(log, mqtt)
        self.lamp = Zigbee2MqttLight(
            app_logger=log, 
            mqtt_plugin=mqtt, 
            name="Bedroom Lamp", 
            state_topic="zigbee2mqtt/bedroom_ambient_lamp", 
            command_topic="zigbee2mqtt/bedroom_ambient_lamp/set"
        )
        self.bedside_table_left_button = MqttButton(
            log=log, 
            mqtt_plugin=mqtt, 
            topic="zigbee2mqtt/bedroom_bedside_table_left_button"
        )
        self.bedside_table_right_button = MqttButton(
            log=log, 
            mqtt_plugin=mqtt, 
            topic="zigbee2mqtt/bedroom_bedside_table_right_button"
        )

class Hall(Room):
    def __init__(self, log, mqtt):
        super().__init__(log, mqtt)
        self.console_button = MqttButton(
            log=log, 
            mqtt_plugin=mqtt, 
            topic="zigbee2mqtt/hall_console_button"
        )
        self.exit_button = MqttButton(
            log=log, 
            mqtt_plugin=mqtt, 
            topic="zigbee2mqtt/hall_exit_button"
        )
        self.main_light = ShellySwitch(
            app_logger=log,
            mqtt_plugin=mqtt,
            name="Hall Main Light",
            state_topic="shellies/hall_main_light/relay/0",
            command_topic="shellies/hall_main_light/relay/0/command"
        )

class Storage(Room):
    def __init__(self, log, mqtt):
        super().__init__(log, mqtt)
        self.doors = MqttContactSensor(
            log=log, 
            mqtt_plugin=mqtt, 
            topic="zigbee2mqtt/storage_doors"
        )
        self.main_light = TasmotaSwitch(
            app_logger=log, 
            mqtt_plugin=mqtt, 
            name="Storage Light", 
            state_topic="iot/tasmota/bathroom_light/stat/POWER", 
            command_topic="iot/tasmota/bathroom_light/cmnd/POWER"
        )

class Home:
    def __init__(self, log, mqtt):
        self.log = log
        self.mqtt = mqtt
        self.living_room = LivingRoom(log, mqtt)
        self.office = Office(log, mqtt)
        self.bedroom = Bedroom(log, mqtt)
        self.hall = Hall(log, mqtt)
        self.storage = Storage(log, mqtt)
