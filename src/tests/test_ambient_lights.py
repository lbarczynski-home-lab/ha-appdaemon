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
from apps.models.home import Home

@pytest.fixture
def app():
    app = AmbientLightsAutomation()
    app.get_app = MagicMock()
    app.log = MagicMock()
    
    # Mock Home model
    mock_home_app = MagicMock()
    mock_mqtt = MagicMock()
    mock_home_app.home = Home(MagicMock(), mock_mqtt)
    
    app.get_app.return_value = mock_home_app
    app.initialize()
    return app

def setup_light_state(app, lights, is_on):
    for light in lights:
        payload = json.dumps({"state": "ON" if is_on else "OFF", "brightness": 100 if is_on else 0})
        light.on_mqtt_message("MQTT_MESSAGE", {"payload": payload}, {})

def test_GIVEN_all_lights_off_WHEN_button_click_THEN_should_turn_on_all_lights(app):
    setup_light_state(app, app.all_lights, is_on=False)
    app.home.mqtt.mqtt_publish.reset_mock()
    
    app.home.hall.console_button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "single"}'}, {})
    
    assert app.home.mqtt.mqtt_publish.call_count == 4
    for call_args in app.home.mqtt.mqtt_publish.call_args_list:
        topic, payload = call_args[0]
        assert "ON" in payload

def test_GIVEN_some_lights_on_WHEN_button_click_THEN_should_turn_off_active_lights(app):
    setup_light_state(app, app.all_lights, is_on=False)
    
    # Only turn on first light
    on_payload = json.dumps({"state": "ON", "brightness": 100})
    app.all_lights[0].on_mqtt_message("MQTT_MESSAGE", {"payload": on_payload}, {})
    
    app.home.mqtt.mqtt_publish.reset_mock()
        
    app.home.bedroom.bedside_table_left_button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "single"}'}, {})
    
    # It should only publish OFF to the ONE light that was ON
    assert app.home.mqtt.mqtt_publish.call_count == 1
    topic, payload = app.home.mqtt.mqtt_publish.call_args_list[0][0]
    assert "OFF" in payload
