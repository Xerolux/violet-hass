"""Tests für interpret_state_as_bool Utility."""

from pathlib import Path
import sys
import types

import pytest


# Ensure repository root is on the import path (mirrors other tests)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _install_homeassistant_stubs() -> None:
    """Install lightweight Home Assistant stubs for unit testing."""

    ha_module = types.ModuleType("homeassistant")

    helpers_module = types.ModuleType("homeassistant.helpers")
    helpers_update = types.ModuleType("homeassistant.helpers.update_coordinator")
    helpers_entity = types.ModuleType("homeassistant.helpers.entity")
    helpers_config_validation = types.ModuleType("homeassistant.helpers.config_validation")

    def _dummy_config_entry_only_config_schema(*_, **__):  # pragma: no cover - stub
        return None

    helpers_config_validation.config_entry_only_config_schema = _dummy_config_entry_only_config_schema
    helpers_aiohttp = types.ModuleType("homeassistant.helpers.aiohttp_client")

    async def _dummy_get_clientsession(*_, **__):  # pragma: no cover - stub
        return None

    helpers_aiohttp.async_get_clientsession = _dummy_get_clientsession

    class CoordinatorEntity:  # pragma: no cover - structure stub
        pass

    class DataUpdateCoordinator:  # pragma: no cover - structure stub
        pass

    class UpdateFailed(Exception):  # pragma: no cover - structure stub
        pass

    class EntityDescription:  # pragma: no cover - structure stub
        def __init__(self, *_, **__):
            pass

    class EntityCategory:  # pragma: no cover - structure stub
        DIAGNOSTIC = "diagnostic"
        CONFIG = "config"

    helpers_update.CoordinatorEntity = CoordinatorEntity
    helpers_update.DataUpdateCoordinator = DataUpdateCoordinator
    helpers_update.UpdateFailed = UpdateFailed
    helpers_entity.EntityDescription = EntityDescription
    helpers_entity.EntityCategory = EntityCategory

    config_entries_module = types.ModuleType("homeassistant.config_entries")

    class ConfigEntry:  # pragma: no cover - structure stub
        def __init__(self, *_, **__):
            pass

    config_entries_module.ConfigEntry = ConfigEntry

    # Register modules
    core_module = types.ModuleType("homeassistant.core")

    class HomeAssistant:  # pragma: no cover - structure stub
        def __init__(self, *_, **__):
            pass

    core_module.HomeAssistant = HomeAssistant

    const_module = types.ModuleType("homeassistant.const")

    class Platform:  # pragma: no cover - structure stub
        SENSOR = "sensor"
        BINARY_SENSOR = "binary_sensor"
        SWITCH = "switch"
        CLIMATE = "climate"
        COVER = "cover"
        NUMBER = "number"
        SELECT = "select"

    const_module.Platform = Platform

    exceptions_module = types.ModuleType("homeassistant.exceptions")

    class ConfigEntryNotReady(Exception):  # pragma: no cover - structure stub
        pass

    class HomeAssistantError(Exception):  # pragma: no cover - structure stub
        pass

    exceptions_module.ConfigEntryNotReady = ConfigEntryNotReady
    exceptions_module.HomeAssistantError = HomeAssistantError

    components_module = types.ModuleType("homeassistant.components")

    number_module = types.ModuleType("homeassistant.components.number")

    class NumberDeviceClass:  # pragma: no cover - structure stub
        SPEED = "speed"
        PH = "ph"

    number_module.NumberDeviceClass = NumberDeviceClass

    binary_sensor_module = types.ModuleType("homeassistant.components.binary_sensor")

    class BinarySensorDeviceClass:  # pragma: no cover - structure stub
        RUNNING = "running"
        PROBLEM = "problem"
        DOOR = "door"

    binary_sensor_module.BinarySensorDeviceClass = BinarySensorDeviceClass

    aiohttp_module = types.ModuleType("aiohttp")

    class ClientError(Exception):  # pragma: no cover - structure stub
        pass

    class ClientResponseError(ClientError):  # pragma: no cover - structure stub
        pass

    class ClientTimeout:  # pragma: no cover - structure stub
        def __init__(self, *_, **__):
            pass

    class TCPConnector:  # pragma: no cover - structure stub
        def __init__(self, *_, **__):
            pass

    class ClientSession:  # pragma: no cover - structure stub
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_, **__):
            return False

        async def get(self, *_, **__):
            return None

        async def post(self, *_, **__):
            return None

    aiohttp_module.ClientError = ClientError
    aiohttp_module.ClientResponseError = ClientResponseError
    aiohttp_module.ClientTimeout = ClientTimeout
    aiohttp_module.TCPConnector = TCPConnector
    aiohttp_module.ClientSession = ClientSession

    sys.modules.setdefault("homeassistant", ha_module)
    sys.modules.setdefault("homeassistant.helpers", helpers_module)
    sys.modules.setdefault("homeassistant.helpers.update_coordinator", helpers_update)
    sys.modules.setdefault("homeassistant.helpers.entity", helpers_entity)
    sys.modules.setdefault("homeassistant.helpers.config_validation", helpers_config_validation)
    sys.modules.setdefault("homeassistant.helpers.aiohttp_client", helpers_aiohttp)
    sys.modules.setdefault("homeassistant.config_entries", config_entries_module)
    sys.modules.setdefault("homeassistant.core", core_module)
    sys.modules.setdefault("homeassistant.const", const_module)
    sys.modules.setdefault("homeassistant.exceptions", exceptions_module)
    sys.modules.setdefault("homeassistant.components", components_module)
    sys.modules.setdefault("homeassistant.components.number", number_module)
    sys.modules.setdefault("homeassistant.components.binary_sensor", binary_sensor_module)
    sys.modules.setdefault("aiohttp", aiohttp_module)

    # Link submodules for dotted access
    ha_module.helpers = helpers_module
    helpers_module.update_coordinator = helpers_update
    helpers_module.entity = helpers_entity
    helpers_module.config_validation = helpers_config_validation
    helpers_module.aiohttp_client = helpers_aiohttp
    components_module.number = number_module
    components_module.binary_sensor = binary_sensor_module


_install_homeassistant_stubs()

from custom_components.violet_pool_controller.entity import interpret_state_as_bool  # noqa: E402


@pytest.mark.parametrize(
    "raw_state,expected",
    [
        ("3|PUMP_ANTI_FREEZE", True),
        ("5|AUTO_WAIT", False),
        (" 2 |AUTO", True),
        ("0|OFF", False),
    ],
)
def test_interpret_state_with_numeric_prefix(raw_state, expected):
    """Composite string states should use their numeric prefix for evaluation."""

    assert interpret_state_as_bool(raw_state, "PUMPSTATE") is expected
