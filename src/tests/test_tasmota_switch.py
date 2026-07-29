import pytest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../apps'))

from components.switch import TasmotaSwitch

@pytest.fixture
def mock_mqtt():
    return MagicMock()

@pytest.fixture
def mock_logger():
    return MagicMock()

@pytest.fixture
def switch(mock_logger, mock_mqtt):
    return TasmotaSwitch(mock_logger, mock_mqtt, "test_switch", "stat/switch", "cmnd/switch")

class TestTasmotaSwitch:
    def test_turn_on_increments_counter_and_delays_update(self, switch, mock_mqtt):
        # Given
        assert switch.is_on() is False
        
        # When
        switch.turn_on()
        
        # Then
        assert switch.is_on() is False # State not updated yet
        assert switch._expected_state_changes == 1
        mock_mqtt.mqtt_publish.assert_called_once_with("cmnd/switch", "ON")

    def test_turn_off_increments_counter_and_delays_update(self, switch, mock_mqtt):
        # Given
        switch._is_on = True
        
        # When
        switch.turn_off()
        
        # Then
        assert switch.is_on() is True # State not updated yet
        assert switch._expected_state_changes == 1
        mock_mqtt.mqtt_publish.assert_called_once_with("cmnd/switch", "OFF")

    def test_mqtt_message_updates_state_and_calls_listener(self, switch):
        # Given
        listener_mock = MagicMock()
        switch.add_state_change_listener(listener_mock)
        
        # When
        switch.on_mqtt_message("MQTT_MESSAGE", {"payload": "ON"}, {})
        
        # Then
        assert switch.is_on() is True
        listener_mock.assert_called_once_with("test_switch", True)

    def test_expected_mqtt_message_decrements_counter_and_suppresses_listener(self, switch):
        # Given
        switch.turn_on() # counter = 1
        listener_mock = MagicMock()
        switch.add_state_change_listener(listener_mock)
        
        # When
        switch.on_mqtt_message("MQTT_MESSAGE", {"payload": "ON"}, {})
        
        # Then
        assert switch.is_on() is True
        assert switch._expected_state_changes == 0
        listener_mock.assert_not_called()

    def test_redundant_mqtt_message_decrements_counter_and_suppresses_listener(self, switch):
        # Given
        switch._is_on = True
        switch.turn_on() # Sending ON while already ON, counter = 1
        listener_mock = MagicMock()
        switch.add_state_change_listener(listener_mock)
        
        # When
        switch.on_mqtt_message("MQTT_MESSAGE", {"payload": "ON"}, {})
        
        # Then
        assert switch.is_on() is True
        assert switch._expected_state_changes == 0
        listener_mock.assert_not_called()

    def test_remove_listener_prevents_callback(self, switch):
        # Given
        listener_mock = MagicMock()
        switch.add_state_change_listener(listener_mock)
        switch.remove_state_change_listener(listener_mock)
        
        # When
        switch.on_mqtt_message("MQTT_MESSAGE", {"payload": "ON"}, {})
        
        # Then
        listener_mock.assert_not_called()

    def test_multiple_turn_on_commands_are_handled_correctly(self, switch, mock_mqtt):
        # Given
        assert switch.is_on() is False
        listener_mock = MagicMock()
        switch.add_state_change_listener(listener_mock)
        
        # When: We call turn_on() 5 times in a row
        for _ in range(5):
            switch.turn_on()
            
        assert switch._expected_state_changes == 5
        
        # Zgodnie ze sprawdzeniem w MQTT Explorer, urządzenie wysyła 5 callbacków
        for _ in range(5):
            switch.on_mqtt_message("MQTT_MESSAGE", {"payload": "ON"}, {})
        
        # Then: Counter wraca do zera bez wywoływania listenera
        assert switch._expected_state_changes == 0
        listener_mock.assert_not_called()
        
        # Prawdziwe kliknięcie guzika w inny stan poprawnie triggeruje listenera
        switch.on_mqtt_message("MQTT_MESSAGE", {"payload": "OFF"}, {})
        
        assert switch.is_on() is False
        assert switch._expected_state_changes == 0
        listener_mock.assert_called_once_with("test_switch", False)
