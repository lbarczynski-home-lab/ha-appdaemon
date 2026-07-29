import pytest
from unittest.mock import MagicMock
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../apps'))

class MockMqtt:
    def __init__(self, *args, **kwargs):
        pass

mock_mqttapi = MagicMock()
mock_mqttapi.Mqtt = MockMqtt
sys.modules["mqttapi"] = mock_mqttapi

from apps.storage_lights import StorageLightsAutomation

@pytest.fixture
def configured_app():
    app = StorageLightsAutomation()
    
    app.mqtt_publish = MagicMock()
    app.listen_event = MagicMock()
    app.log = MagicMock()
    
    app.initialize()
    return app

def test_GIVEN_doors_open_WHEN_mqtt_message_received_THEN_should_turn_on_lights(configured_app):
    app = configured_app
    payload = json.dumps({"contact": False})
    
    app.home.storage.doors.on_mqtt_message("MQTT_MESSAGE", {"payload": payload}, {})
    
    app.mqtt_publish.assert_called_once_with("iot/tasmota/bathroom_light/cmnd/POWER", "ON")

def test_GIVEN_doors_closed_WHEN_mqtt_message_received_THEN_should_turn_off_lights(configured_app):
    app = configured_app
    
    # Open doors first to ensure state change
    app.home.storage.doors.on_mqtt_message("MQTT_MESSAGE", {"payload": json.dumps({"contact": False})}, {})
    app.mqtt_publish.reset_mock()
    
    payload = json.dumps({"contact": True})
    app.home.storage.doors.on_mqtt_message("MQTT_MESSAGE", {"payload": payload}, {})
    
    app.mqtt_publish.assert_called_once_with("iot/tasmota/bathroom_light/cmnd/POWER", "OFF")

def test_GIVEN_invalid_json_WHEN_mqtt_message_received_THEN_should_do_nothing(configured_app):
    app = configured_app
    payload = "invalid json"
    
    app.home.storage.doors.on_mqtt_message("MQTT_MESSAGE", {"payload": payload}, {})
    
    app.mqtt_publish.assert_not_called()

def test_GIVEN_no_contact_key_WHEN_mqtt_message_received_THEN_should_do_nothing(configured_app):
    app = configured_app
    payload = json.dumps({"battery": 100})
    
    app.home.storage.doors.on_mqtt_message("MQTT_MESSAGE", {"payload": payload}, {})
    
    app.mqtt_publish.assert_not_called()
