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

from apps.bedroom_lights import BedroomLightsAutomation
from apps.models.home import Home

@pytest.fixture
def app():
    app = BedroomLightsAutomation()
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
    
    # Expose the mocked home model to the tests so we can simulate button clicks
    app.mock_home = mock_home_app.home
    return app

def test_GIVEN_lamp_off_WHEN_single_click_THEN_should_turn_on_with_high_brightness(app):
    app.get_state.return_value = "off"
    app.mock_home.bedroom.bedside_table_left_button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "single"}'}, {})
    app.turn_on.assert_called_with("light.bedroom_rgb_lamp", brightness=254)

def test_GIVEN_lamp_on_WHEN_single_click_THEN_should_turn_off(app):
    app.get_state.return_value = "on"
    app.mock_home.bedroom.bedside_table_right_button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "single"}'}, {})
    app.turn_off.assert_called_with("light.bedroom_rgb_lamp")

def test_GIVEN_any_state_WHEN_double_click_THEN_should_toggle_brightness(app):
    # Initially high, so first double click makes it low (76)
    app.mock_home.bedroom.bedside_table_left_button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "double"}'}, {})
    app.turn_on.assert_called_with("light.bedroom_rgb_lamp", brightness=76)
    
    app.turn_on.reset_mock()
    
    # Second double click makes it high (254)
    app.mock_home.bedroom.bedside_table_left_button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "double"}'}, {})
    app.turn_on.assert_called_with("light.bedroom_rgb_lamp", brightness=254)

def test_GIVEN_hall_light_off_WHEN_hold_THEN_should_turn_on(app):
    app.mock_home.mqtt.mqtt_publish.reset_mock()
    # Mock that the light is off by overriding the is_on method
    app.mock_home.hall.main_light.is_on = MagicMock(return_value=False)
    app.mock_home.bedroom.bedside_table_left_button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "hold"}'}, {})
    app.mock_home.mqtt.mqtt_publish.assert_called_with("shellies/hall_main_light/relay/0/command", "on")

def test_GIVEN_hall_light_on_WHEN_hold_THEN_should_turn_off(app):
    app.mock_home.mqtt.mqtt_publish.reset_mock()
    app.mock_home.hall.main_light.is_on = MagicMock(return_value=True)
    app.mock_home.bedroom.bedside_table_left_button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "hold"}'}, {})
    app.mock_home.mqtt.mqtt_publish.assert_called_with("shellies/hall_main_light/relay/0/command", "off")
