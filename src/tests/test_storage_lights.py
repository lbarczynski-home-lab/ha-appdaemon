import pytest
from unittest.mock import MagicMock
import sys
import json

class MockMqtt:
    def __init__(self, *args, **kwargs):
        pass

mock_mqttapi = MagicMock()
mock_mqttapi.Mqtt = MockMqtt
sys.modules["mqttapi"] = mock_mqttapi

from apps.storage_lights import StorageLightsAutomation

@pytest.fixture
def configured_app():
    """Fixture that initializes the app and mocks the mqtt methods."""
    app = StorageLightsAutomation()
    
    app.mqtt_publish = MagicMock()
    app.listen_event = MagicMock()
    app.log = MagicMock()
    
    app.initialize()
    
    return app

def test_GIVEN_doors_open_WHEN_mqtt_message_received_THEN_should_turn_on_lights(configured_app):
    app = configured_app
    
    # GIVEN
    payload = json.dumps({"contact": False})
    
    # WHEN
    app.on_doors_message("MQTT_MESSAGE", {"topic": "zigbee2mqtt/storage_doors", "payload": payload}, {})
    
    # THEN
    app.mqtt_publish.assert_called_once_with("iot/tasmota/bathroom_light/cmnd/POWER", "ON")

def test_GIVEN_doors_closed_WHEN_mqtt_message_received_THEN_should_turn_off_lights(configured_app):
    app = configured_app
    
    # GIVEN
    payload = json.dumps({"contact": True})
    
    # WHEN
    app.on_doors_message("MQTT_MESSAGE", {"topic": "zigbee2mqtt/storage_doors", "payload": payload}, {})
    
    # THEN
    app.mqtt_publish.assert_called_once_with("iot/tasmota/bathroom_light/cmnd/POWER", "OFF")

def test_GIVEN_invalid_json_WHEN_mqtt_message_received_THEN_should_do_nothing(configured_app):
    app = configured_app
    
    # GIVEN
    payload = "invalid json"
    
    # WHEN
    app.on_doors_message("MQTT_MESSAGE", {"topic": "zigbee2mqtt/storage_doors", "payload": payload}, {})
    
    # THEN
    app.mqtt_publish.assert_not_called()

def test_GIVEN_no_contact_key_WHEN_mqtt_message_received_THEN_should_do_nothing(configured_app):
    app = configured_app
    
    # GIVEN
    payload = json.dumps({"battery": 100})
    
    # WHEN
    app.on_doors_message("MQTT_MESSAGE", {"topic": "zigbee2mqtt/storage_doors", "payload": payload}, {})
    
    # THEN
    app.mqtt_publish.assert_not_called()

