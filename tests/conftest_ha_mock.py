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

    # Mock helpers - make it a proper package
    helpers_module = types.ModuleType('helpers')
    sys.modules['homeassistant.helpers'] = helpers_module

    # helpers.config_validation
    config_validation_module = types.ModuleType('config_validation')
    helpers_module.config_validation = config_validation_module
    sys.modules['homeassistant.helpers.config_validation'] = config_validation_module

    # helpers.device_registry
    device_registry_module = types.ModuleType('device_registry')
    class DeviceInfo(dict):
        pass
    device_registry_module.DeviceInfo = DeviceInfo
    helpers_module.device_registry = device_registry_module
    sys.modules['homeassistant.helpers.device_registry'] = device_registry_module

    # helpers.update_coordinator
    update_coordinator_module = types.ModuleType('update_coordinator')
    class CoordinatorEntity:
        def __init__(self, coordinator):
            self.coordinator = coordinator
    update_coordinator_module.CoordinatorEntity = CoordinatorEntity
    helpers_module.update_coordinator = update_coordinator_module
    sys.modules['homeassistant.helpers.update_coordinator'] = update_coordinator_module

    # helpers.entity_platform
    entity_platform_module = types.ModuleType('entity_platform')
    helpers_module.entity_platform = entity_platform_module
    sys.modules['homeassistant.helpers.entity_platform'] = entity_platform_module

    # helpers.service_info (for ZeroConf)
    service_info_module = types.ModuleType('service_info')
    zeroconf_module = types.ModuleType('zeroconf')
    class ZeroconfServiceInfo:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    zeroconf_module.ZeroconfServiceInfo = ZeroconfServiceInfo
    service_info_module.zeroconf = zeroconf_module
    helpers_module.service_info = service_info_module
    sys.modules['homeassistant.helpers.service_info'] = service_info_module
    sys.modules['homeassistant.helpers.service_info.zeroconf'] = zeroconf_module

    ha_module.helpers = helpers_module

    # Mock components
    components_module = types.ModuleType('components')
    sys.modules['homeassistant.components'] = components_module

    # components.cover
    cover_module = types.ModuleType('cover')
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

    cover_module.CoverDeviceClass = CoverDeviceClass
    cover_module.CoverEntity = CoverEntity
    cover_module.CoverEntityDescription = CoverEntityDescription
    cover_module.CoverEntityFeature = CoverEntityFeature
    components_module.cover = cover_module
    sys.modules['homeassistant.components.cover'] = cover_module

    # components.switch
    switch_module = types.ModuleType('switch')
    class SwitchEntityDescription:
        def __init__(self, key, name=None, **kwargs):
            self.key = key
            self.name = name
    switch_module.SwitchEntityDescription = SwitchEntityDescription
    components_module.switch = switch_module
    sys.modules['homeassistant.components.switch'] = switch_module

    # components.number
    number_module = types.ModuleType('number')
    class NumberEntityDescription:
        def __init__(self, key, name=None, **kwargs):
            self.key = key
            self.name = name
    number_module.NumberEntityDescription = NumberEntityDescription
    components_module.number = number_module
    sys.modules['homeassistant.components.number'] = number_module

    # components.select
    select_module = types.ModuleType('select')
    class SelectEntityDescription:
        def __init__(self, key, name=None, **kwargs):
            self.key = key
            self.name = name
    select_module.SelectEntityDescription = SelectEntityDescription
    components_module.select = select_module
    sys.modules['homeassistant.components.select'] = select_module
    sys.modules['homeassistant.helpers'] = ha_module.helpers


# Setup mocks
setup_homeassistant_mocks()


# Setup pytest_homeassistant_custom_component mocks
if 'pytest_homeassistant_custom_component' not in sys.modules:
    common_module = types.ModuleType('pytest_homeassistant_custom_component')
    common_submodule = types.ModuleType('common')

    # Mock MockConfigEntry
    class MockConfigEntry(dict):
        def __init__(self, domain=None, data=None, options=None, entry_id=None, title=None):
            super().__init__()
            self.domain = domain
            self.data = data or {}
            self.options = options or {}
            self.entry_id = entry_id or 'test_entry_id'
            self.title = title or 'Test'

    common_submodule.MockConfigEntry = MockConfigEntry
    common_module.common = common_submodule

    sys.modules['pytest_homeassistant_custom_component'] = common_module
    sys.modules['pytest_homeassistant_custom_component.common'] = common_submodule
