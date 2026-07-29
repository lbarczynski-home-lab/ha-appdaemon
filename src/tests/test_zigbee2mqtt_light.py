import pytest
from unittest.mock import MagicMock
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../apps'))

from components.lights import Zigbee2MqttLight

@pytest.fixture
def mock_mqtt():
    return MagicMock()

@pytest.fixture
def mock_logger():
    return MagicMock()

@pytest.fixture
def light(mock_logger, mock_mqtt):
    return Zigbee2MqttLight(mock_logger, mock_mqtt, "test_light", "zigbee2mqtt/light", "zigbee2mqtt/light/set")

class TestZigbee2MqttLight:
    def test_turn_on_increments_counter_and_delays_update(self, light, mock_mqtt):
        # Given
        assert light.is_on() is False
        
        # When
        light.turn_on()
        
        # Then
        assert light.is_on() is False # State not updated yet
        assert light._expected_state_changes == 1
        expected_payload = json.dumps({"state": "ON", "brightness": 254})
        mock_mqtt.mqtt_publish.assert_called_once_with("zigbee2mqtt/light/set", expected_payload)

    def test_turn_off_increments_counter_and_delays_update(self, light, mock_mqtt):
        # Given
        light._is_on = True
        light._brightness = 254
        
        # When
        light.turn_off()
        
        # Then
        assert light.is_on() is True # State not updated yet
        assert light._expected_state_changes == 1
        expected_payload = json.dumps({"state": "OFF"})
        mock_mqtt.mqtt_publish.assert_called_once_with("zigbee2mqtt/light/set", expected_payload)

    def test_mqtt_message_updates_state_and_calls_listener(self, light):
        # Given
        listener_mock = MagicMock()
        light.add_state_change_listener(listener_mock)
        
        # When
        payload_on = json.dumps({"state": "ON", "brightness": 254})
        light.on_mqtt_message("MQTT_MESSAGE", {"payload": payload_on}, {})
        
        # Then
        assert light.is_on() is True
        listener_mock.assert_called_once_with("test_light", True)

    def test_expected_mqtt_message_decrements_counter_and_suppresses_listener(self, light):
        # Given
        light.turn_on() # counter = 1
        listener_mock = MagicMock()
        light.add_state_change_listener(listener_mock)
        
        # When
        payload_on = json.dumps({"state": "ON", "brightness": 254})
        light.on_mqtt_message("MQTT_MESSAGE", {"payload": payload_on}, {})
        
        # Then
        assert light.is_on() is True
        assert light._expected_state_changes == 0
        listener_mock.assert_not_called()

    def test_redundant_mqtt_message_decrements_counter_and_suppresses_listener(self, light):
        # Given
        light._is_on = True
        light._brightness = 254
        light.turn_on() # Sending ON while already ON, counter = 1
        listener_mock = MagicMock()
        light.add_state_change_listener(listener_mock)
        
        # When
        payload_on = json.dumps({"state": "ON", "brightness": 254})
        light.on_mqtt_message("MQTT_MESSAGE", {"payload": payload_on}, {})
        
        # Then
        assert light.is_on() is True
        assert light._expected_state_changes == 0
        listener_mock.assert_not_called()

    def test_remove_listener_prevents_callback(self, light):
        # Given
        listener_mock = MagicMock()
        light.add_state_change_listener(listener_mock)
        light.remove_state_change_listener(listener_mock)
        
        # When
        payload_on = json.dumps({"state": "ON", "brightness": 254})
        light.on_mqtt_message("MQTT_MESSAGE", {"payload": payload_on}, {})
        
        # Then
        listener_mock.assert_not_called()
