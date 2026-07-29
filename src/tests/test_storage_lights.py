import pytest
from unittest.mock import MagicMock
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../apps'))

class MockHass:
    def __init__(self, *args, **kwargs):
        pass

mock_hassapi = MagicMock()
mock_hassapi.Hass = MockHass
sys.modules["hassapi"] = mock_hassapi

from apps.storage_lights import StorageLightsAutomation
from apps.models.home import Home

@pytest.fixture
def configured_app():
    app = StorageLightsAutomation()
    app.get_app = MagicMock()
    app.log = MagicMock()
    
    mock_home_app = MagicMock()
    mock_mqtt = MagicMock()
    mock_home_app.home = Home(MagicMock(), mock_mqtt)
    
    app.get_app.return_value = mock_home_app
    app.initialize()
    return app

def test_GIVEN_doors_open_WHEN_mqtt_message_received_THEN_should_turn_on_lights(configured_app):
    app = configured_app
    payload = json.dumps({"contact": False})
    app.home.storage.doors.on_mqtt_message("MQTT_MESSAGE", {"payload": payload}, {})
    app.home.mqtt.mqtt_publish.assert_called_once_with("iot/tasmota/bathroom_light/cmnd/POWER", "ON")

def test_GIVEN_doors_closed_WHEN_mqtt_message_received_THEN_should_turn_off_lights(configured_app):
    app = configured_app
    app.home.storage.doors.on_mqtt_message("MQTT_MESSAGE", {"payload": json.dumps({"contact": False})}, {})
    app.home.mqtt.mqtt_publish.reset_mock()
    
    payload = json.dumps({"contact": True})
    app.home.storage.doors.on_mqtt_message("MQTT_MESSAGE", {"payload": payload}, {})
    app.home.mqtt.mqtt_publish.assert_called_once_with("iot/tasmota/bathroom_light/cmnd/POWER", "OFF")

def test_GIVEN_invalid_json_WHEN_mqtt_message_received_THEN_should_do_nothing(configured_app):
    app = configured_app
    payload = "invalid json"
    app.home.storage.doors.on_mqtt_message("MQTT_MESSAGE", {"payload": payload}, {})
    app.home.mqtt.mqtt_publish.assert_not_called()

def test_GIVEN_no_contact_key_WHEN_mqtt_message_received_THEN_should_do_nothing(configured_app):
    app = configured_app
    payload = json.dumps({"battery": 100})
    app.home.storage.doors.on_mqtt_message("MQTT_MESSAGE", {"payload": payload}, {})
    app.home.mqtt.mqtt_publish.assert_not_called()
