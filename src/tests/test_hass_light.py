import pytest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../apps'))

from components.lights import HassLight

@pytest.fixture
def mock_app():
    app = MagicMock()
    return app

def test_GIVEN_hass_light_WHEN_initialized_THEN_should_log(mock_app):
    light = HassLight(mock_app, "light.test_lamp")
    mock_app.log.assert_called_with("[HassLight] Initialized for entity light.test_lamp", level="INFO")

def test_GIVEN_hass_light_WHEN_is_on_called_THEN_returns_true_if_state_is_on(mock_app):
    light = HassLight(mock_app, "light.test_lamp")
    mock_app.get_state.return_value = "on"
    assert light.is_on() is True

def test_GIVEN_hass_light_WHEN_is_on_called_THEN_returns_false_if_state_is_off(mock_app):
    light = HassLight(mock_app, "light.test_lamp")
    mock_app.get_state.return_value = "off"
    assert light.is_on() is False

def test_GIVEN_hass_light_WHEN_turn_on_called_THEN_should_call_app_turn_on(mock_app):
    light = HassLight(mock_app, "light.test_lamp")
    light.turn_on()
    mock_app.turn_on.assert_called_with("light.test_lamp")
    mock_app.log.assert_any_call("[HassLight] Sending turn ON command to light.test_lamp", level="INFO")

def test_GIVEN_hass_light_WHEN_turn_off_called_THEN_should_call_app_turn_off(mock_app):
    light = HassLight(mock_app, "light.test_lamp")
    light.turn_off()
    mock_app.turn_off.assert_called_with("light.test_lamp")
    mock_app.log.assert_any_call("[HassLight] Sending turn OFF command to light.test_lamp", level="INFO")
