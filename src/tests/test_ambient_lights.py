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

from apps.ambient_lights import AmbientLightsAutomation

@pytest.fixture
def app():
    app = AmbientLightsAutomation()
    app.get_plugin_api = MagicMock()
    app.mqtt = MagicMock()
    app.get_plugin_api.return_value = app.mqtt
    app.log = MagicMock()
    
    app.initialize()
    return app

def setup_light_state(app, is_on):
    for light in app.lights:
        payload = json.dumps({"state": "ON" if is_on else "OFF", "brightness": 100 if is_on else 0})
        light.on_mqtt_message("MQTT_MESSAGE", {"payload": payload}, {})

def test_GIVEN_all_lights_off_WHEN_single_button_click_THEN_should_turn_on_all_lights(app):
    setup_light_state(app, is_on=False)
    app.mqtt.mqtt_publish.reset_mock()
    
    app.home.hall.console_button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "single"}'}, {})
    
    assert app.mqtt.mqtt_publish.call_count == 4
    for call_args in app.mqtt.mqtt_publish.call_args_list:
        topic, payload = call_args[0]
        assert "ON" in payload

def test_GIVEN_some_lights_on_WHEN_single_button_click_THEN_should_turn_off_all_lights(app):
    setup_light_state(app, is_on=False)
    
    on_payload = json.dumps({"state": "ON", "brightness": 100})
    app.lights[0].on_mqtt_message("MQTT_MESSAGE", {"payload": on_payload}, {})
    
    app.mqtt.mqtt_publish.reset_mock()
        
    app.home.hall.console_button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "single"}'}, {})
    
    assert app.mqtt.mqtt_publish.call_count == 4
    for call_args in app.mqtt.mqtt_publish.call_args_list:
        topic, payload = call_args[0]
        assert "OFF" in payload

def test_GIVEN_all_lights_on_WHEN_single_button_click_THEN_should_turn_off_all_lights(app):
    setup_light_state(app, is_on=True)
    app.mqtt.mqtt_publish.reset_mock()
        
    app.home.hall.console_button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "single"}'}, {})
    
    assert app.mqtt.mqtt_publish.call_count == 4
    for call_args in app.mqtt.mqtt_publish.call_args_list:
        topic, payload = call_args[0]
        assert "OFF" in payload

def test_GIVEN_all_lights_off_WHEN_unsupported_action_click_THEN_should_not_change_state(app):
    setup_light_state(app, is_on=False)
    app.mqtt.mqtt_publish.reset_mock()
        
    app.home.hall.console_button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "double"}'}, {})
    
    app.mqtt.mqtt_publish.assert_not_called()
