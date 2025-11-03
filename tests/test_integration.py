"""Unit tests for the Violet Pool Controller integration.

The real Home Assistant framework is not available in the execution
environment that powers these exercises.  To make the integration
testable we install a set of lightweight stubs that emulate the minimal
behaviour exercised by the unit tests.  The production code continues to
import the canonical modules which keeps the implementation compatible
with Home Assistant while ensuring the tests can run without the heavy
dependency tree.
"""

from __future__ import annotations

import asyncio
import sys
import types
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from pathlib import Path


# Ensure the repository root is on ``sys.path`` so the custom component can be
# imported just like it would inside Home Assistant.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Home Assistant test stubs
# ---------------------------------------------------------------------------


def _install_voluptuous_stub() -> None:
    if "voluptuous" in sys.modules:  # pragma: no cover - defensive guard
        return

    vol_mod = types.ModuleType("voluptuous")

    class Schema:
        def __init__(self, schema: Any) -> None:
            self.schema = schema

        def __call__(self, value: Any) -> Any:  # pragma: no cover - trivial
            return value

    def Required(key: Any, default: Any | None = None) -> Any:
        return key

    def Optional(key: Any, default: Any | None = None) -> Any:
        return key

    def All(*validators: Any) -> Callable[[Any], Any]:  # pragma: no cover - trivial
        def _validator(value: Any) -> Any:
            for validator in validators:
                value = validator(value)
            return value

        return _validator

    def Coerce(type_: Callable[[Any], Any]) -> Callable[[Any], Any]:
        def _validator(value: Any) -> Any:
            return type_(value)

        return _validator

    def Range(*args: Any, **kwargs: Any) -> Callable[[Any], Any]:
        def _validator(value: Any) -> Any:
            return value

        return _validator

    def In(container: Any) -> Callable[[Any], Any]:
        def _validator(value: Any) -> Any:
            if value not in container:
                raise ValueError(f"{value!r} not in {container!r}")
            return value

        return _validator

    vol_mod.Schema = Schema
    vol_mod.Required = Required
    vol_mod.Optional = Optional
    vol_mod.All = All
    vol_mod.Coerce = Coerce
    vol_mod.Range = Range
    vol_mod.In = In
    vol_mod.boolean = lambda value: bool(value)  # pragma: no cover - trivial

    sys.modules["voluptuous"] = vol_mod


def _install_aiohttp_stub() -> None:
    if "aiohttp" in sys.modules:  # pragma: no cover - defensive guard
        return

    aiohttp_mod = types.ModuleType("aiohttp")

    class ClientSession:  # pragma: no cover - simple stub
        async def request(self, *args: Any, **kwargs: Any) -> Any:
            raise RuntimeError("aiohttp stub does not support real requests")

    class ClientTimeout:  # pragma: no cover - simple stub
        def __init__(self, total: float | None = None) -> None:
            self.total = total

    class BasicAuth:  # pragma: no cover - simple stub
        def __init__(self, login: str, password: str = "") -> None:
            self.login = login
            self.password = password

    class ClientError(Exception):
        pass

    class ContentTypeError(Exception):
        pass

    aiohttp_mod.ClientSession = ClientSession
    aiohttp_mod.ClientTimeout = ClientTimeout
    aiohttp_mod.BasicAuth = BasicAuth
    aiohttp_mod.ClientError = ClientError
    aiohttp_mod.ContentTypeError = ContentTypeError

    sys.modules["aiohttp"] = aiohttp_mod


def _install_homeassistant_stubs() -> None:
    """Install minimal Home Assistant stubs if the real package is absent."""

    if "homeassistant" in sys.modules:  # pragma: no cover - defensive guard
        return

    # ``homeassistant`` package root -------------------------------------------------
    ha_pkg = types.ModuleType("homeassistant")
    ha_pkg.__path__ = []  # Mark the module as a package
    sys.modules["homeassistant"] = ha_pkg

    # ``homeassistant.const`` --------------------------------------------------------
    const_mod = types.ModuleType("homeassistant.const")

    class Platform(str, Enum):
        SENSOR = "sensor"
        BINARY_SENSOR = "binary_sensor"
        SWITCH = "switch"
        CLIMATE = "climate"
        COVER = "cover"
        NUMBER = "number"

    const_mod.Platform = Platform
    const_mod.ATTR_DEVICE_ID = "device_id"
    const_mod.ATTR_ENTITY_ID = "entity_id"
    const_mod.CONF_USERNAME = "username"
    const_mod.CONF_PASSWORD = "password"
    sys.modules["homeassistant.const"] = const_mod
    ha_pkg.const = const_mod

    # ``homeassistant.exceptions`` ---------------------------------------------------
    exceptions_mod = types.ModuleType("homeassistant.exceptions")

    class HomeAssistantError(Exception):
        """Base error type matching Home Assistant's behaviour."""

    class ConfigEntryNotReady(HomeAssistantError):
        """Raised when a config entry cannot be prepared."""

    exceptions_mod.HomeAssistantError = HomeAssistantError
    exceptions_mod.ConfigEntryNotReady = ConfigEntryNotReady
    sys.modules["homeassistant.exceptions"] = exceptions_mod
    ha_pkg.exceptions = exceptions_mod

    # ``homeassistant.config_entries`` -----------------------------------------------
    config_entries_mod = types.ModuleType("homeassistant.config_entries")

    @dataclass
    class ConfigEntry:
        data: dict[str, Any]
        options: dict[str, Any] = field(default_factory=dict)
        entry_id: str = "entry"
        version: int = 1
        title: str = "Test Entry"

    config_entries_mod.ConfigEntry = ConfigEntry
    sys.modules["homeassistant.config_entries"] = config_entries_mod
    ha_pkg.config_entries = config_entries_mod

    # ``homeassistant.core`` ---------------------------------------------------------
    core_mod = types.ModuleType("homeassistant.core")

    class HomeAssistant:
        """Tiny Home Assistant stub used by the tests."""

        def __init__(self) -> None:
            self.data: dict[str, Any] = {}
            self.config_entries = MagicMock()
            self.services = MagicMock()

    @dataclass
    class ServiceCall:
        data: dict[str, Any]

    core_mod.HomeAssistant = HomeAssistant
    core_mod.ServiceCall = ServiceCall
    sys.modules["homeassistant.core"] = core_mod
    ha_pkg.core = core_mod

    # ``homeassistant.components`` package -----------------------------------------
    components_pkg = types.ModuleType("homeassistant.components")
    components_pkg.__path__ = []
    sys.modules["homeassistant.components"] = components_pkg
    ha_pkg.components = components_pkg

    number_mod = types.ModuleType("homeassistant.components.number")

    class _NumberDeviceClass:
        def __getattr__(self, name: str) -> str:  # pragma: no cover - simple stub
            return name.lower()

    number_mod.NumberDeviceClass = _NumberDeviceClass()
    sys.modules["homeassistant.components.number"] = number_mod
    components_pkg.number = number_mod

    binary_sensor_mod = types.ModuleType("homeassistant.components.binary_sensor")

    class _BinarySensorDeviceClass:
        def __getattr__(self, name: str) -> str:  # pragma: no cover - simple stub
            return name.lower()

    binary_sensor_mod.BinarySensorDeviceClass = _BinarySensorDeviceClass()
    sys.modules["homeassistant.components.binary_sensor"] = binary_sensor_mod
    components_pkg.binary_sensor = binary_sensor_mod

    # ``homeassistant.helpers`` package ---------------------------------------------
    helpers_pkg = types.ModuleType("homeassistant.helpers")
    helpers_pkg.__path__ = []
    sys.modules["homeassistant.helpers"] = helpers_pkg
    ha_pkg.helpers = helpers_pkg

    # ``homeassistant.helpers.entity`` ---------------------------------------------
    entity_helper_mod = types.ModuleType("homeassistant.helpers.entity")

    class _EntityCategory:
        def __getattr__(self, name: str) -> str:  # pragma: no cover - simple stub
            return name.lower()

    entity_helper_mod.EntityCategory = _EntityCategory()
    sys.modules["homeassistant.helpers.entity"] = entity_helper_mod
    helpers_pkg.entity = entity_helper_mod

    # ``homeassistant.helpers.config_validation`` -----------------------------------
    cv_mod = types.ModuleType("homeassistant.helpers.config_validation")

    def config_entry_only_config_schema(domain: str) -> Callable[[Any], Any]:
        return lambda value=None: value

    def entity_ids(value: Any) -> list[str]:
        if isinstance(value, list):
            return value
        return [str(value)]

    def string(value: Any) -> str:
        return str(value)

    def boolean(value: Any) -> bool:
        return bool(value)

    cv_mod.config_entry_only_config_schema = config_entry_only_config_schema
    cv_mod.entity_ids = entity_ids
    cv_mod.string = string
    cv_mod.boolean = boolean
    sys.modules["homeassistant.helpers.config_validation"] = cv_mod
    helpers_pkg.config_validation = cv_mod

    # ``homeassistant.helpers.aiohttp_client`` --------------------------------------
    aiohttp_client_mod = types.ModuleType("homeassistant.helpers.aiohttp_client")

    def async_get_clientsession(hass: Any) -> object:  # pragma: no cover - stub
        return object()

    aiohttp_client_mod.async_get_clientsession = async_get_clientsession
    sys.modules["homeassistant.helpers.aiohttp_client"] = aiohttp_client_mod
    helpers_pkg.aiohttp_client = aiohttp_client_mod

    # ``homeassistant.helpers.entity_registry`` -------------------------------------
    entity_registry_mod = types.ModuleType("homeassistant.helpers.entity_registry")

    class _DummyEntityRegistry:
        def async_get(self, entity_id: str) -> Any:  # pragma: no cover - stub
            return None

    def async_get(hass: Any) -> _DummyEntityRegistry:  # pragma: no cover - stub
        return _DummyEntityRegistry()

    entity_registry_mod.async_get = async_get
    sys.modules["homeassistant.helpers.entity_registry"] = entity_registry_mod
    helpers_pkg.entity_registry = entity_registry_mod

    # ``homeassistant.helpers.update_coordinator`` -----------------------------------
    coordinator_mod = types.ModuleType("homeassistant.helpers.update_coordinator")

    class DataUpdateCoordinator:  # pragma: no cover - simple stub
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.data = {}

        async def async_config_entry_first_refresh(self) -> None:  # pragma: no cover - stub
            return None

        async def async_request_refresh(self) -> None:  # pragma: no cover - stub
            return None

    class UpdateFailed(Exception):
        pass

    coordinator_mod.DataUpdateCoordinator = DataUpdateCoordinator
    coordinator_mod.UpdateFailed = UpdateFailed
    sys.modules["homeassistant.helpers.update_coordinator"] = coordinator_mod
    helpers_pkg.update_coordinator = coordinator_mod


_install_voluptuous_stub()
_install_aiohttp_stub()
_install_homeassistant_stubs()


# Now we can import the integration using the stubbed modules
from homeassistant.exceptions import HomeAssistantError  # type: ignore  # noqa: E402

import custom_components.violet_pool_controller.api as api_module  # noqa: E402
import custom_components.violet_pool_controller.device as device_module  # noqa: E402

from custom_components.violet_pool_controller import (  # noqa: E402
    PLATFORMS,
    async_migrate_entry,
    async_setup,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.violet_pool_controller.const import (  # noqa: E402
    CONF_ACTIVE_FEATURES,
    CONF_API_URL,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_POLLING_INTERVAL,
    CONF_RETRY_ATTEMPTS,
    CONF_TIMEOUT_DURATION,
    CONF_USE_SSL,
    DOMAIN,
)
from custom_components.violet_pool_controller.services import (  # noqa: E402
    async_register_services,
)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def hass() -> Any:
    instance = sys.modules["homeassistant.core"].HomeAssistant()
    instance.data.setdefault(DOMAIN, {})
    instance.config_entries.async_forward_entry_setups = AsyncMock()
    instance.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    instance.services.has_service = MagicMock(return_value=False)
    instance.services.async_register = MagicMock()
    return instance


@pytest.fixture
def config_entry() -> Any:
    entry_cls = sys.modules["homeassistant.config_entries"].ConfigEntry
    return entry_cls(
        data={
            CONF_API_URL: "192.168.1.100",
            CONF_USE_SSL: False,
            CONF_DEVICE_ID: 1,
            CONF_DEVICE_NAME: "Test Pool Controller",
            CONF_POLLING_INTERVAL: 15,
            CONF_TIMEOUT_DURATION: 10,
            CONF_RETRY_ATTEMPTS: 3,
            CONF_ACTIVE_FEATURES: ["heating"],
        },
        options={},
        entry_id="test-entry",
        title="Test Pool Controller",
    )


@pytest.fixture
def coordinator() -> MagicMock:
    mock = MagicMock()
    mock.device = MagicMock()
    mock.device.available = True
    mock.device.api = MagicMock()
    mock.config_entry = MagicMock(entry_id="test-entry")
    return mock


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_async_setup_initialises_domain(hass: Any) -> None:
    hass.data.pop(DOMAIN, None)
    result = asyncio.run(async_setup(hass, {}))
    assert result is True
    assert DOMAIN in hass.data


def test_async_setup_entry_success(hass: Any, config_entry: Any, coordinator: MagicMock) -> None:
    with patch.object(
        device_module,
        "async_setup_device",
        new=AsyncMock(return_value=coordinator),
    ), patch.object(
        api_module,
        "VioletPoolAPI",
        autospec=True,
    ) as api_cls:
        result = asyncio.run(async_setup_entry(hass, config_entry))

    assert result is True
    hass.config_entries.async_forward_entry_setups.assert_awaited_once_with(
        config_entry, PLATFORMS
    )
    api_cls.assert_called_once()
    assert hass.data[DOMAIN][config_entry.entry_id] is coordinator


def test_async_setup_entry_missing_host(hass: Any, config_entry: Any) -> None:
    config_entry.data.pop(CONF_API_URL)

    with patch.object(
        api_module,
        "VioletPoolAPI",
        autospec=True,
    ), patch.object(
        device_module,
        "async_setup_device",
        new=AsyncMock(),
    ):
        with pytest.raises(HomeAssistantError):
            asyncio.run(async_setup_entry(hass, config_entry))


def test_async_setup_entry_device_error(hass: Any, config_entry: Any) -> None:
    with patch.object(
        device_module,
        "async_setup_device",
        new=AsyncMock(side_effect=HomeAssistantError("boom")),
    ), patch.object(
        api_module,
        "VioletPoolAPI",
        autospec=True,
    ):
        with pytest.raises(HomeAssistantError):
            asyncio.run(async_setup_entry(hass, config_entry))


def test_async_unload_entry_success(hass: Any, config_entry: Any, coordinator: MagicMock) -> None:
    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = coordinator

    result = asyncio.run(async_unload_entry(hass, config_entry))

    assert result is True
    hass.config_entries.async_unload_platforms.assert_awaited_once()
    assert hass.data[DOMAIN] == {}


def test_async_unload_entry_failure(hass: Any, config_entry: Any) -> None:
    hass.config_entries.async_unload_platforms.side_effect = HomeAssistantError("fail")

    result = asyncio.run(async_unload_entry(hass, config_entry))

    assert result is False


def test_async_migrate_entry_versions(hass: Any, config_entry: Any) -> None:
    config_entry.version = 1
    assert asyncio.run(async_migrate_entry(hass, config_entry)) is True

    config_entry.version = 99
    assert asyncio.run(async_migrate_entry(hass, config_entry)) is False


def test_service_registration_registers_expected_services(hass: Any) -> None:
    hass.services.has_service.return_value = False

    asyncio.run(async_register_services(hass))

    registered = {
        call.args[1] for call in hass.services.async_register.call_args_list
    }
    assert registered == {
        "control_pump",
        "smart_dosing",
        "manage_pv_surplus",
        "control_dmx_scenes",
        "set_light_color_pulse",
        "manage_digital_rules",
    }


def test_service_registration_is_idempotent(hass: Any) -> None:
    hass.services.has_service.return_value = True

    asyncio.run(async_register_services(hass))

    hass.services.async_register.assert_not_called()

