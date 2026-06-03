"""Minimal Home Assistant mocks for tests without full HA installation."""

import sys
import types


def setup_homeassistant_mocks():
    """Setup minimal Home Assistant mocks."""
    import sys

    # Mock homeassistant package
    ha_module = types.ModuleType('homeassistant')
    sys.modules['homeassistant'] = ha_module

    # Mock submodules
    ha_module.const = types.ModuleType('const')
    ha_module.const.CONF_DEVICE_ID = 'device_id'
    ha_module.const.CONF_HOST = 'host'
    ha_module.const.CONF_PASSWORD = 'password'
    ha_module.const.CONF_PORT = 'port'
    ha_module.const.CONF_USERNAME = 'username'
    ha_module.const.CONF_VERIFY_SSL = 'verify_ssl'
    sys.modules['homeassistant.const'] = ha_module.const

    # Mock config_entries
    ha_module.config_entries = types.ModuleType('config_entries')
    class MockConfigEntry:
        def __init__(self, domain=None, data=None, options=None, entry_id=None, title=None):
            self.domain = domain
            self.data = data or {}
            self.options = options or {}
            self.entry_id = entry_id or 'test_entry_id'
            self.title = title or 'Test'

    ha_module.config_entries.ConfigEntry = MockConfigEntry
    sys.modules['homeassistant.config_entries'] = ha_module.config_entries

    # Mock core
    ha_module.core = types.ModuleType('core')
    sys.modules['homeassistant.core'] = ha_module.core

    # Mock exceptions
    ha_module.exceptions = types.ModuleType('exceptions')
    class HomeAssistantError(Exception):
        pass
    ha_module.exceptions.HomeAssistantError = HomeAssistantError
    sys.modules['homeassistant.exceptions'] = ha_module.exceptions

    # Mock helpers
    ha_module.helpers = types.ModuleType('helpers')

    # helpers.config_validation
    ha_module.helpers.config_validation = types.ModuleType('config_validation')
    sys.modules['homeassistant.helpers.config_validation'] = ha_module.helpers.config_validation

    # helpers.device_registry
    ha_module.helpers.device_registry = types.ModuleType('device_registry')
    class DeviceInfo(dict):
        pass
    ha_module.helpers.device_registry.DeviceInfo = DeviceInfo
    sys.modules['homeassistant.helpers.device_registry'] = ha_module.helpers.device_registry

    # helpers.update_coordinator
    ha_module.helpers.update_coordinator = types.ModuleType('update_coordinator')
    class CoordinatorEntity:
        def __init__(self, coordinator):
            self.coordinator = coordinator
    ha_module.helpers.update_coordinator.CoordinatorEntity = CoordinatorEntity
    sys.modules['homeassistant.helpers.update_coordinator'] = ha_module.helpers.update_coordinator

    # helpers.entity_platform
    ha_module.helpers.entity_platform = types.ModuleType('entity_platform')
    sys.modules['homeassistant.helpers.entity_platform'] = ha_module.helpers.entity_platform

    # Mock components
    ha_module.components = types.ModuleType('components')

    # components.cover
    ha_module.components.cover = types.ModuleType('cover')
    class CoverDeviceClass:
        SHUTTER = 'shutter'
    class CoverEntity:
        pass
    class CoverEntityDescription:
        def __init__(self, key, name=None, translation_key=None, icon=None):
            self.key = key
            self.name = name
            self.translation_key = translation_key
            self.icon = icon
    class CoverEntityFeature:
        OPEN = 1
        CLOSE = 2
        STOP = 4

    ha_module.components.cover.CoverDeviceClass = CoverDeviceClass
    ha_module.components.cover.CoverEntity = CoverEntity
    ha_module.components.cover.CoverEntityDescription = CoverEntityDescription
    ha_module.components.cover.CoverEntityFeature = CoverEntityFeature
    sys.modules['homeassistant.components.cover'] = ha_module.components.cover

    sys.modules['homeassistant.components'] = ha_module.components
    sys.modules['homeassistant.helpers'] = ha_module.helpers


# Setup mocks
setup_homeassistant_mocks()
