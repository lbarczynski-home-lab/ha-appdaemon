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

from apps.office_lights import OfficeLightsAutomation
from apps.models.home import Home

@pytest.fixture
def app():
    app = OfficeLightsAutomation()
    app.get_app = MagicMock()
    app.log = MagicMock()
    
    mock_home_app = MagicMock()
    mock_mqtt = MagicMock()
    mock_home_app.home = Home(MagicMock(), mock_mqtt)
    
    app.get_app.return_value = mock_home_app
    app.initialize()
    return app

def test_GIVEN_wall_button_turns_on_WHEN_state_changed_THEN_should_turn_on_vertical_rgb_lamp(app):
    app.home.mqtt.mqtt_publish.reset_mock()
    payload = "ON"
    app.home.office.light_switch_additional_button.on_mqtt_message("MQTT_MESSAGE", {"payload": payload}, {})
    app.home.mqtt.mqtt_publish.assert_called_with("gv2mqtt/light/27D0EEE3EEDAD052/command", json.dumps({"state": "ON", "brightness": 100}))

def test_GIVEN_wall_button_turns_off_WHEN_state_changed_THEN_should_turn_off_vertical_rgb_lamp(app):
    app.home.office.light_switch_additional_button.on_mqtt_message("MQTT_MESSAGE", {"payload": "ON"}, {})
    app.home.mqtt.mqtt_publish.reset_mock()
    payload = "OFF"
    app.home.office.light_switch_additional_button.on_mqtt_message("MQTT_MESSAGE", {"payload": payload}, {})
    app.home.mqtt.mqtt_publish.assert_called_with("gv2mqtt/light/27D0EEE3EEDAD052/command", json.dumps({"state": "OFF"}))
