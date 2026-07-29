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

from apps.office_lights import OfficeLightsAutomation

@pytest.fixture
def app():
    app = OfficeLightsAutomation()
    app.log = MagicMock()
    
    # For mqttapi plugins, `self` is often passed as the mqtt instance or we have self.mqtt_publish etc.
    # In office_lights we did: self.home = Home(self.log, self)
    # So we need to mock mqtt_publish, listen_event on app itself.
    app.mqtt_publish = MagicMock()
    app.listen_event = MagicMock()
    
    app.initialize()
    return app

def test_GIVEN_wall_button_turns_on_WHEN_state_changed_THEN_should_turn_on_vertical_rgb_lamp(app):
    # GIVEN
    # clear initial publish calls if any
    app.mqtt_publish.reset_mock()
    
    # WHEN
    # Simulate wall button ON (right button in office is a TasmotaSwitch)
    payload = "ON"
    app.home.office.light_switch_additional_button.on_mqtt_message("MQTT_MESSAGE", {"payload": payload}, {})
    
    # THEN
    app.mqtt_publish.assert_called_with("gv2mqtt/light/27D0EEE3EEDAD052/command", json.dumps({"state": "ON", "brightness": 100}))

def test_GIVEN_wall_button_turns_off_WHEN_state_changed_THEN_should_turn_off_vertical_rgb_lamp(app):
    # GIVEN
    app.mqtt_publish.reset_mock()
    # First turn it on to ensure state change registers correctly in TasmotaSwitch
    app.home.office.light_switch_additional_button.on_mqtt_message("MQTT_MESSAGE", {"payload": "ON"}, {})
    app.mqtt_publish.reset_mock()
    
    # WHEN
    # Simulate wall button OFF
    payload = "OFF"
    app.home.office.light_switch_additional_button.on_mqtt_message("MQTT_MESSAGE", {"payload": payload}, {})
    
    # THEN
    app.mqtt_publish.assert_called_with("gv2mqtt/light/27D0EEE3EEDAD052/command", json.dumps({"state": "OFF"}))
