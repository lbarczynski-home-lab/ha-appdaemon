import pytest
from unittest.mock import MagicMock
import sys

# Mock hassapi before importing the app
class MockHass:
    def __init__(self, *args, **kwargs):
        pass

mock_hassapi = MagicMock()
mock_hassapi.Hass = MockHass
sys.modules["hassapi"] = mock_hassapi

from apps.ambient_lights import AmbientLightsAutomation

@pytest.fixture
def configured_app():
    """Fixture that initializes the app and mocks the lights."""
    app = AmbientLightsAutomation()
    
    app.get_plugin_api = MagicMock()
    app.mqtt = MagicMock()
    app.get_plugin_api.return_value = app.mqtt
    
    app.log = MagicMock()
    
    mock_lights = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    app.get_entity = MagicMock(side_effect=mock_lights)
    
    app.initialize()
    
    return app, mock_lights

def setup_light_state(light_mock, is_on):
    """Helper method to mock entity state responses for get_state()."""
    if is_on:
        def mock_get_state(attribute=None):
            if attribute is None:
                return "on"
            elif attribute == "brightness":
                return 100
        light_mock.get_state.side_effect = mock_get_state
    else:
        def mock_get_state(attribute=None):
            if attribute is None:
                return "off"
            elif attribute == "brightness":
                return 0
        light_mock.get_state.side_effect = mock_get_state

def test_GIVEN_all_lights_off_WHEN_single_button_click_THEN_should_turn_on_all_lights(configured_app):
    app, lights = configured_app
    
    # GIVEN
    for light in lights:
        setup_light_state(light, is_on=False)
        
    # WHEN
    app.on_button_click("event_name", {"topic": "some/topic", "payload": "single"}, {})
    
    # THEN
    for light in lights:
        light.turn_on.assert_called_once_with(brightness=255)
        light.turn_off.assert_not_called()

def test_GIVEN_some_lights_on_WHEN_single_button_click_THEN_should_turn_off_all_lights(configured_app):
    app, lights = configured_app
    
    # GIVEN
    setup_light_state(lights[0], is_on=False)
    setup_light_state(lights[1], is_on=True)
    setup_light_state(lights[2], is_on=False)
    setup_light_state(lights[3], is_on=False)
        
    # WHEN
    app.on_button_click("event_name", {"topic": "some/topic", "payload": "single"}, {})
    
    # THEN
    for light in lights:
        light.turn_off.assert_called_once()
        light.turn_on.assert_not_called()

def test_GIVEN_all_lights_on_WHEN_single_button_click_THEN_should_turn_off_all_lights(configured_app):
    app, lights = configured_app
    
    # GIVEN
    for light in lights:
        setup_light_state(light, is_on=True)
        
    # WHEN
    app.on_button_click("event_name", {"topic": "some/topic", "payload": "single"}, {})
    
    # THEN
    for light in lights:
        light.turn_off.assert_called_once()
        light.turn_on.assert_not_called()

def test_GIVEN_all_lights_off_WHEN_unsupported_action_click_THEN_should_not_change_state(configured_app):
    app, lights = configured_app
    
    # GIVEN
    for light in lights:
        setup_light_state(light, is_on=False)
        
    # WHEN
    app.on_button_click("event_name", {"topic": "some/topic", "payload": "double"}, {})
    
    # THEN
    for light in lights:
        light.turn_off.assert_not_called()
        light.turn_on.assert_not_called()

def test_GIVEN_all_lights_off_WHEN_single_button_click_json_payload_THEN_should_turn_on_all_lights(configured_app):
    app, lights = configured_app
    
    # GIVEN
    for light in lights:
        setup_light_state(light, is_on=False)
        
    # WHEN
    app.on_button_click("event_name", {"topic": "some/topic", "payload": '{"action": "single"}'}, {})
    
    # THEN
    for light in lights:
        light.turn_on.assert_called_once_with(brightness=255)
        light.turn_off.assert_not_called()
