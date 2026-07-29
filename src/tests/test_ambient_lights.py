import pytest
from unittest.mock import MagicMock, call
import sys
import os

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
    app.log = MagicMock()
    app.get_state = MagicMock()
    app.turn_on = MagicMock()
    app.turn_off = MagicMock()
    
    # Mock Home model
    mock_home_app = MagicMock()
    mock_mqtt = MagicMock()
    mock_home_app.home = Home(MagicMock(), mock_mqtt)
    
    app.get_app = MagicMock(return_value=mock_home_app)
    
    app.initialize()
    app.home = mock_home_app.home
    return app

def test_GIVEN_all_lights_off_WHEN_button_click_THEN_should_turn_on_all_lights(app):
    app.get_state.return_value = "off"
    
    app.home.hall.console_button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "single"}'}, {})
    
    assert app.turn_on.call_count == 4
    app.turn_on.assert_has_calls([
        call("light.living_room_rtv_shelf_led_strip"),
        call("light.living_room_bookshelf_led_strip"),
        call("light.bedroom_ambient_lamp"),
        call("light.office_vertical_rgb_lamp"),
    ])

def test_GIVEN_some_lights_on_WHEN_button_click_THEN_should_turn_off_active_lights(app):
    def mock_get_state(entity_id):
        if entity_id == "light.living_room_rtv_shelf_led_strip":
            return "on"
        return "off"
        
    app.get_state.side_effect = mock_get_state
    
    app.home.bedroom.bedside_table_left_button.on_mqtt_message("MQTT_MESSAGE", {"payload": '{"action": "single"}'}, {})
    
    assert app.turn_off.call_count == 1
    app.turn_off.assert_called_with("light.living_room_rtv_shelf_led_strip")
