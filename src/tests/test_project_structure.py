import os
import pytest
import importlib
import sys
from unittest.mock import MagicMock

APPS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../apps'))

# Add apps directory to path so we can test imports
if APPS_DIR not in sys.path:
    sys.path.insert(0, APPS_DIR)

# Mock base classes to avoid errors when importing
class MockHass:
    def __init__(self, *args, **kwargs): pass
class MockMqtt:
    def __init__(self, *args, **kwargs): pass

mock_hassapi = MagicMock()
mock_hassapi.Hass = MockHass
sys.modules["hassapi"] = mock_hassapi

mock_mqttapi = MagicMock()
mock_mqttapi.Mqtt = MockMqtt
sys.modules["mqttapi"] = mock_mqttapi


def test_all_subdirectories_are_packages():
    """
    AppDaemon (and standard Python packaging in older contexts) requires 
    subdirectories to have __init__.py to be imported as packages.
    """
    for root, dirs, files in os.walk(APPS_DIR):
        # Ignore __pycache__ and hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('__') and not d.startswith('.')]
        
        for d in dirs:
            dir_path = os.path.join(root, d)
            init_file = os.path.join(dir_path, '__init__.py')
            assert os.path.isfile(init_file), f"CRITICAL: Directory {dir_path} is missing __init__.py! This will cause ModuleNotFoundError in AppDaemon."

def test_apps_yaml_is_valid_and_classes_exist():
    """
    Validates apps.yaml syntax and ensures every referenced module and class exists.
    """
    apps_yaml_path = os.path.join(APPS_DIR, 'apps.yaml')
    
    apps_config = {}
    current_app = None
    with open(apps_yaml_path, 'r') as f:
        for line in f:
            line = line.split('#')[0].rstrip()
            if not line.strip():
                continue
            if not line.startswith(' '):
                current_app = line.replace(':', '').strip()
                apps_config[current_app] = {}
            elif current_app:
                if ':' in line:
                    key, val = line.split(':', 1)
                    apps_config[current_app][key.strip()] = val.strip()
        
    if not apps_config:
        return # Empty file

    for app_name, app_config in apps_config.items():
        module_name = app_config.get('module')
        class_name = app_config.get('class')
        
        assert module_name is not None, f"App '{app_name}' is missing 'module' in apps.yaml"
        assert class_name is not None, f"App '{app_name}' is missing 'class' in apps.yaml"
        
        # 1. Test if module exists and imports without syntax errors
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            pytest.fail(f"Failed to import module '{module_name}' for app '{app_name}'. Error: {e}")
            
        # 2. Test if class exists in the module
        assert hasattr(module, class_name), f"Class '{class_name}' not found in module '{module_name}' (App: '{app_name}')"
