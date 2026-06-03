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
    ha_module.const.ATTR_DEVICE_ID = 'device_id'
    ha_module.const.ATTR_ENTITY_ID = 'entity_id'
    ha_module.const.__version__ = '2026.5.0'

    # Mock UnitOfTemperature
    class UnitOfTemperature:
        CELSIUS = '°C'
        FAHRENHEIT = '°F'

    # Mock UnitOfPower
    class UnitOfPower:
        WATT = 'W'
        KILOWATT = 'kW'

    ha_module.const.UnitOfTemperature = UnitOfTemperature
    ha_module.const.UnitOfPower = UnitOfPower

    # Mock Platform enum
    class Platform:
        SENSOR = 'sensor'
        BINARY_SENSOR = 'binary_sensor'
        SWITCH = 'switch'
        CLIMATE = 'climate'
        COVER = 'cover'
        NUMBER = 'number'
        SELECT = 'select'

    ha_module.const.Platform = Platform
    sys.modules['homeassistant.const'] = ha_module.const

    # Mock data_entry_flow
    data_entry_flow_module = types.ModuleType('data_entry_flow')

    class FlowHandler:
        pass

    class FlowResultType:
        FORM = 'form'
        CREATE_ENTRY = 'create_entry'
        ABORT = 'abort'

    data_entry_flow_module.FlowHandler = FlowHandler
    data_entry_flow_module.FlowResultType = FlowResultType
    sys.modules['homeassistant.data_entry_flow'] = data_entry_flow_module

    # Mock config_entries
    ha_module.config_entries = types.ModuleType('config_entries')

    class MockConfigEntry:
        def __init__(self, domain=None, data=None, options=None, entry_id=None, title=None):
            self.domain = domain
            self.data = data or {}
            self.options = options or {}
            self.entry_id = entry_id or 'test_entry_id'
            self.title = title or 'Test'

        def add_to_hass(self, hass):
            """Add entry to hass."""
            if not hasattr(hass, 'config_entries'):
                hass.config_entries = []
            if not isinstance(hass.config_entries, list):
                hass.config_entries = []
            hass.config_entries.append(self)

    ha_module.config_entries.ConfigEntry = MockConfigEntry
    sys.modules['homeassistant.config_entries'] = ha_module.config_entries

    # Mock core
    ha_module.core = types.ModuleType('core')

    class HomeAssistant:
        def __init__(self):
            self.data = {}

    def callback(func):
        """Mock callback decorator."""
        return func

    class SupportsResponse:
        ONLY = 'only'

    class ServiceCall:
        def __init__(self, domain=None, service=None, data=None, context=None):
            self.domain = domain
            self.service = service
            self.data = data or {}
            self.context = context

    ha_module.core.HomeAssistant = HomeAssistant
    ha_module.core.callback = callback
    ha_module.core.SupportsResponse = SupportsResponse
    ha_module.core.ServiceCall = ServiceCall
    sys.modules['homeassistant.core'] = ha_module.core

    # Mock exceptions
    ha_module.exceptions = types.ModuleType('exceptions')

    class HomeAssistantError(Exception):
        pass

    class ConfigEntryNotReady(Exception):
        pass

    ha_module.exceptions.HomeAssistantError = HomeAssistantError
    ha_module.exceptions.ConfigEntryNotReady = ConfigEntryNotReady
    sys.modules['homeassistant.exceptions'] = ha_module.exceptions

    # Mock helpers - make it a proper package
    helpers_module = types.ModuleType('helpers')
    sys.modules['homeassistant.helpers'] = helpers_module

    # helpers.config_validation
    config_validation_module = types.ModuleType('config_validation')

    def config_entry_only_config_schema(domain):
        """Mock config_entry_only_config_schema."""
        def schema(config):
            return {}
        return schema

    def string(value):
        """Mock string validator."""
        return str(value)

    config_validation_module.config_entry_only_config_schema = config_entry_only_config_schema
    config_validation_module.string = string
    helpers_module.config_validation = config_validation_module
    sys.modules['homeassistant.helpers.config_validation'] = config_validation_module

    # helpers.aiohttp_client
    aiohttp_client_module = types.ModuleType('aiohttp_client')

    async def async_get_clientsession(hass, verify_ssl=True):
        """Mock async_get_clientsession."""
        pass

    aiohttp_client_module.async_get_clientsession = async_get_clientsession
    helpers_module.aiohttp_client = aiohttp_client_module
    sys.modules['homeassistant.helpers.aiohttp_client'] = aiohttp_client_module

    # helpers.entity
    entity_module = types.ModuleType('entity')

    class EntityCategory:
        DIAGNOSTIC = 'diagnostic'
        CONFIG = 'config'

    entity_module.EntityCategory = EntityCategory
    helpers_module.entity = entity_module
    sys.modules['homeassistant.helpers.entity'] = entity_module

    # helpers.entity_registry
    entity_registry_module = types.ModuleType('entity_registry')
    helpers_module.entity_registry = entity_registry_module
    sys.modules['homeassistant.helpers.entity_registry'] = entity_registry_module

    # helpers.issue_registry
    issue_registry_module = types.ModuleType('issue_registry')

    class IssueSeverity:
        CRITICAL = 'critical'
        ERROR = 'error'
        WARNING = 'warning'
        INFO = 'info'

    def create_issue(hass, domain, issue_id, **kwargs):
        """Mock create_issue."""
        pass

    async def async_create_issue(hass, domain, issue_id, **kwargs):
        """Mock async_create_issue."""
        pass

    async def async_delete_issue(hass, domain, issue_id):
        """Mock async_delete_issue."""
        pass

    issue_registry_module.IssueSeverity = IssueSeverity
    issue_registry_module.create_issue = create_issue
    issue_registry_module.async_create_issue = async_create_issue
    issue_registry_module.async_delete_issue = async_delete_issue
    helpers_module.issue_registry = issue_registry_module
    sys.modules['homeassistant.helpers.issue_registry'] = issue_registry_module

    # helpers.device_registry
    device_registry_module = types.ModuleType('device_registry')

    class DeviceInfo(dict):
        pass

    class DeviceRegistry:
        pass

    device_registry_module.DeviceInfo = DeviceInfo
    device_registry_module.DeviceRegistry = DeviceRegistry
    helpers_module.device_registry = device_registry_module
    sys.modules['homeassistant.helpers.device_registry'] = device_registry_module

    # helpers.update_coordinator
    update_coordinator_module = types.ModuleType('update_coordinator')

    class UpdateFailed(Exception):
        pass

    class DataUpdateCoordinator:
        def __init__(self, hass, logger, name, update_interval=None):
            self.hass = hass
            self.logger = logger
            self.name = name
            self.update_interval = update_interval

    class CoordinatorEntity:
        def __init__(self, coordinator):
            self.coordinator = coordinator

    update_coordinator_module.UpdateFailed = UpdateFailed
    update_coordinator_module.DataUpdateCoordinator = DataUpdateCoordinator
    update_coordinator_module.CoordinatorEntity = CoordinatorEntity
    helpers_module.update_coordinator = update_coordinator_module
    sys.modules['homeassistant.helpers.update_coordinator'] = update_coordinator_module

    # helpers.entity_platform
    entity_platform_module = types.ModuleType('entity_platform')
    entity_platform_module.AddEntitiesCallback = type('AddEntitiesCallback', (), {})
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

    # components.binary_sensor
    binary_sensor_module = types.ModuleType('binary_sensor')

    class BinarySensorDeviceClass:
        MOTION = 'motion'
        DOOR = 'door'
        PROBLEM = 'problem'
        SAFETY = 'safety'
        SOUND = 'sound'
        RUNNING = 'running'

    binary_sensor_module.BinarySensorDeviceClass = BinarySensorDeviceClass
    components_module.binary_sensor = binary_sensor_module
    sys.modules['homeassistant.components.binary_sensor'] = binary_sensor_module

    # components.climate
    climate_module = types.ModuleType('climate')

    class HVACMode:
        OFF = 'off'
        HEAT = 'heat'
        AUTO = 'auto'

    class HVACAction:
        OFF = 'off'
        HEATING = 'heating'
        IDLE = 'idle'

    class ClimateEntityFeature:
        TARGET_TEMPERATURE = 1
        TARGET_TEMPERATURE_RANGE = 2

    class ClimateEntity:
        pass

    class ClimateEntityDescription:
        def __init__(self, key, name=None, **kwargs):
            self.key = key
            self.name = name

    climate_module.HVACMode = HVACMode
    climate_module.HVACAction = HVACAction
    climate_module.ClimateEntityFeature = ClimateEntityFeature
    climate_module.ClimateEntity = ClimateEntity
    climate_module.ClimateEntityDescription = ClimateEntityDescription
    components_module.climate = climate_module
    sys.modules['homeassistant.components.climate'] = climate_module

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

    class SwitchEntity:
        pass

    class SwitchEntityDescription:
        def __init__(self, key, name=None, **kwargs):
            self.key = key
            self.name = name

    switch_module.SwitchEntity = SwitchEntity
    switch_module.SwitchEntityDescription = SwitchEntityDescription
    components_module.switch = switch_module
    sys.modules['homeassistant.components.switch'] = switch_module

    # components.number
    number_module = types.ModuleType('number')

    class NumberDeviceClass:
        TEMPERATURE = 'temperature'
        HUMIDITY = 'humidity'
        POWER = 'power'
        PH = 'ph'

    class NumberEntity:
        pass

    class NumberEntityDescription:
        def __init__(self, key, name=None, **kwargs):
            self.key = key
            self.name = name

    number_module.NumberDeviceClass = NumberDeviceClass
    number_module.NumberEntity = NumberEntity
    number_module.NumberEntityDescription = NumberEntityDescription
    components_module.number = number_module
    sys.modules['homeassistant.components.number'] = number_module

    # components.select
    select_module = types.ModuleType('select')

    class SelectEntity:
        pass

    class SelectEntityDescription:
        def __init__(self, key, name=None, **kwargs):
            self.key = key
            self.name = name

    select_module.SelectEntity = SelectEntity
    select_module.SelectEntityDescription = SelectEntityDescription
    components_module.select = select_module
    sys.modules['homeassistant.components.select'] = select_module

    # components.sensor
    sensor_module = types.ModuleType('sensor')

    class SensorDeviceClass:
        TEMPERATURE = 'temperature'
        HUMIDITY = 'humidity'
        POWER = 'power'

    class SensorStateClass:
        MEASUREMENT = 'measurement'

    class SensorEntity:
        pass

    class SensorEntityDescription:
        def __init__(self, key, name=None, **kwargs):
            self.key = key
            self.name = name

    sensor_module.SensorDeviceClass = SensorDeviceClass
    sensor_module.SensorStateClass = SensorStateClass
    sensor_module.SensorEntity = SensorEntity
    sensor_module.SensorEntityDescription = SensorEntityDescription
    components_module.sensor = sensor_module
    sys.modules['homeassistant.components.sensor'] = sensor_module

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

        def __eq__(self, other):
            if not isinstance(other, MockConfigEntry):
                return False
            return (self.domain == other.domain and
                    self.data == other.data and
                    self.options == other.options and
                    self.entry_id == other.entry_id and
                    self.title == other.title)

    common_submodule.MockConfigEntry = MockConfigEntry
    common_module.common = common_submodule

    sys.modules['pytest_homeassistant_custom_component'] = common_module
    sys.modules['pytest_homeassistant_custom_component.common'] = common_submodule
