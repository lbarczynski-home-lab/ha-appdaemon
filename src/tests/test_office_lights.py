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
    app.log = MagicMock()
    app.listen_state = MagicMock()
    app.turn_on = MagicMock()
    app.turn_off = MagicMock()
    app.get_state = MagicMock()
    
    mock_home_app = MagicMock()
    mock_mqtt = MagicMock()
    mock_home_app.home = Home(MagicMock(), mock_mqtt)
    
    app.get_app = MagicMock(return_value=mock_home_app)
    app.initialize()
    return app

def test_GIVEN_wall_button_turns_on_WHEN_state_changed_THEN_should_turn_on_vertical_rgb_lamp(app):
    payload = "ON"
    app.home.office.light_switch_additional_button.on_mqtt_message("MQTT_MESSAGE", {"payload": payload}, {})
    app.turn_on.assert_called_with("light.office_floor_rgb_lamp", brightness=254)

def test_GIVEN_wall_button_turns_off_WHEN_state_changed_THEN_should_turn_off_vertical_rgb_lamp(app):
    app.home.office.light_switch_additional_button.on_mqtt_message("MQTT_MESSAGE", {"payload": "ON"}, {})
    app.turn_off.reset_mock()
    
    payload = "OFF"
    app.home.office.light_switch_additional_button.on_mqtt_message("MQTT_MESSAGE", {"payload": payload}, {})
    app.turn_off.assert_called_with("light.office_floor_rgb_lamp")

def test_GIVEN_lamp_turns_on_WHEN_state_changed_THEN_should_turn_on_wall_button(app):
    app.home.mqtt.mqtt_publish.reset_mock()
    app.lamp._on_hass_state_change("light.office_floor_rgb_lamp", "state", "off", "on", {})
    app.home.mqtt.mqtt_publish.assert_called_with("iot/tasmota/office_light/cmnd/POWER2", "ON")

def test_GIVEN_lamp_turns_off_WHEN_state_changed_THEN_should_turn_off_wall_button(app):
    app.lamp._on_hass_state_change("light.office_floor_rgb_lamp", "state", "off", "on", {})
    app.home.mqtt.mqtt_publish.reset_mock()
    
    app.lamp._on_hass_state_change("light.office_floor_rgb_lamp", "state", "on", "off", {})
    app.home.mqtt.mqtt_publish.assert_called_with("iot/tasmota/office_light/cmnd/POWER2", "OFF")
