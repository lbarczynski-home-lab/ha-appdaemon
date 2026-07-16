import pytest
from unittest.mock import MagicMock, call
import sys
import os
import json

# Add apps directory to sys.path so that absolute imports from within apps (like 'components') work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../apps'))

# Mock hassapi before importing the app
class MockHass:
    def __init__(self, *args, **kwargs):
        pass

mock_hassapi = MagicMock()
mock_hassapi.Hass = MockHass
sys.modules["hassapi"] = mock_hassapi

from apps.ambient_lights import AmbientLightsAutomation

@pytest.fixture
def app():
    """Fixture that initializes the app and mocks mqtt."""
    app = AmbientLightsAutomation()
    
    app.get_plugin_api = MagicMock()
    app.mqtt = MagicMock()
    app.get_plugin_api.return_value = app.mqtt
    app.log = MagicMock()
    
    app.initialize()
    
    # After initialize, app.lights and app.buttons are populated.
    return app

def setup_light_state(app, is_on):
    """Helper method to mock entity state responses by directly calling on_mqtt_message on each light."""
    for light in app.lights:
        payload = json.dumps({"state": "ON" if is_on else "OFF", "brightness": 100 if is_on else 0})
        light.on_mqtt_message("MQTT_MESSAGE", {"payload": payload}, {})

def test_GIVEN_all_lights_off_WHEN_single_button_click_THEN_should_turn_on_all_lights(app):
    # GIVEN
    setup_light_state(app, is_on=False)
    app.mqtt.mqtt_publish.reset_mock()
        
    # WHEN
    button = app.buttons[0]
    button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "single"}'}, {})
    
    # THEN
    # We expect mqtt_publish to be called with "ON" for all command topics
    assert app.mqtt.mqtt_publish.call_count == 4
    # Let's verify that "ON" is in the published payload
    for call_args in app.mqtt.mqtt_publish.call_args_list:
        topic, payload = call_args[0]
        assert "ON" in payload

def test_GIVEN_some_lights_on_WHEN_single_button_click_THEN_should_turn_off_all_lights(app):
    # GIVEN
    setup_light_state(app, is_on=False)
    
    # Turn ON just one light (e.g. the first one)
    on_payload = json.dumps({"state": "ON", "brightness": 100})
    app.lights[0].on_mqtt_message("MQTT_MESSAGE", {"payload": on_payload}, {})
    
    app.mqtt.mqtt_publish.reset_mock()
        
    # WHEN
    button = app.buttons[0]
    button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "single"}'}, {})
    
    # THEN
    # We expect mqtt_publish to be called with "OFF" for all command topics
    assert app.mqtt.mqtt_publish.call_count == 4
    for call_args in app.mqtt.mqtt_publish.call_args_list:
        topic, payload = call_args[0]
        assert "OFF" in payload

def test_GIVEN_all_lights_on_WHEN_single_button_click_THEN_should_turn_off_all_lights(app):
    # GIVEN
    setup_light_state(app, is_on=True)
    app.mqtt.mqtt_publish.reset_mock()
        
    # WHEN
    button = app.buttons[0]
    button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "single"}'}, {})
    
    # THEN
    assert app.mqtt.mqtt_publish.call_count == 4
    for call_args in app.mqtt.mqtt_publish.call_args_list:
        topic, payload = call_args[0]
        assert "OFF" in payload

def test_GIVEN_all_lights_off_WHEN_unsupported_action_click_THEN_should_not_change_state(app):
    # GIVEN
    setup_light_state(app, is_on=False)
    app.mqtt.mqtt_publish.reset_mock()
        
    # WHEN
    button = app.buttons[0]
    button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "double"}'}, {})
    
    # THEN
    app.mqtt.mqtt_publish.assert_not_called()

def test_GIVEN_no_initial_state_retained_WHEN_single_button_click_THEN_should_turn_on_all_lights(app):
    # GIVEN no setup_light_state called (simulating no retained MQTT messages)
    app.mqtt.mqtt_publish.reset_mock()
        
    # WHEN
    button = app.buttons[0]
    button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "single"}'}, {})
    
    # THEN
    assert app.mqtt.mqtt_publish.call_count == 4
    for call_args in app.mqtt.mqtt_publish.call_args_list:
        topic, payload = call_args[0]
        assert "ON" in payload
