"""Unit tests for the Violet Pool Controller integration."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from custom_components.violet_pool_controller import (
    PLATFORMS,
    async_migrate_entry,
    async_setup,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.violet_pool_controller import api as api_module
from custom_components.violet_pool_controller import device as device_module
from custom_components.violet_pool_controller.const import (
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
from custom_components.violet_pool_controller.services import (
    async_register_services,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def config_entry(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
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
        entry_id="test-entry",
        title="Test Pool Controller",
    )
    entry.add_to_hass(hass)
    return entry


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


async def test_async_setup_initialises_domain(hass: HomeAssistant) -> None:
    # Ensure domain is clean
    if DOMAIN in hass.data:
        del hass.data[DOMAIN]

    result = await async_setup(hass, {})
    assert result is True
    assert DOMAIN in hass.data


async def test_async_setup_entry_success(hass: HomeAssistant, config_entry: MockConfigEntry, coordinator: MagicMock) -> None:
    # Ensure domain data exists (simulating async_setup)
    hass.data.setdefault(DOMAIN, {})

    # Mock hass.config_entries.async_forward_entry_setups
    # In some HA versions/test setups this might be needed or it's an async method
    hass.config_entries.async_forward_entry_setups = AsyncMock()

    with patch.object(
        device_module,
        "async_setup_device",
        new=AsyncMock(return_value=coordinator),
    ), patch.object(
        api_module,
        "VioletPoolAPI",
        autospec=True,
    ) as api_cls:
        result = await async_setup_entry(hass, config_entry)

    assert result is True
    hass.config_entries.async_forward_entry_setups.assert_awaited_once_with(config_entry, PLATFORMS)
    api_cls.assert_called_once()
    assert hass.data[DOMAIN][config_entry.entry_id] is coordinator


async def test_async_setup_entry_missing_host(hass: HomeAssistant) -> None:
    # Create entry with missing host
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            # CONF_API_URL missing
            CONF_USE_SSL: False,
            CONF_DEVICE_ID: 1,
            CONF_DEVICE_NAME: "Test Pool Controller",
            CONF_POLLING_INTERVAL: 15,
            CONF_TIMEOUT_DURATION: 10,
            CONF_RETRY_ATTEMPTS: 3,
            CONF_ACTIVE_FEATURES: ["heating"],
        },
        entry_id="test-entry-missing-host",
        title="Test Pool Controller",
    )
    entry.add_to_hass(hass)

    # Ensure domain data exists
    hass.data.setdefault(DOMAIN, {})

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
             await async_setup_entry(hass, entry)


async def test_async_setup_entry_device_error(hass: HomeAssistant, config_entry: MockConfigEntry) -> None:
    # Ensure domain data exists
    hass.data.setdefault(DOMAIN, {})

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
            await async_setup_entry(hass, config_entry)


async def test_async_unload_entry_success(hass: HomeAssistant, config_entry: MockConfigEntry, coordinator: MagicMock) -> None:
    # Setup coordinator mock with api mock
    coordinator.device.api._session.close = AsyncMock()

    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = coordinator

    # Mock async_unload_platforms on the instance
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    result = await async_unload_entry(hass, config_entry)

    assert result is True
    hass.config_entries.async_unload_platforms.assert_awaited_once()
    # async_unload_entry pops the entry from hass.data if successful
    assert config_entry.entry_id not in hass.data[DOMAIN]


async def test_async_unload_entry_failure(hass: HomeAssistant, config_entry: MockConfigEntry) -> None:
    # We need to make sure the entry is in hass.data
    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = MagicMock()

    hass.config_entries.async_unload_platforms = AsyncMock(return_value=False)

    result = await async_unload_entry(hass, config_entry)

    assert result is False


async def test_async_migrate_entry_versions(hass: HomeAssistant) -> None:
    entry_v1 = MockConfigEntry(domain=DOMAIN, data={}, version=1)
    entry_v1.add_to_hass(hass)
    assert await async_migrate_entry(hass, entry_v1) is True

    entry_v99 = MockConfigEntry(domain=DOMAIN, data={}, version=99)
    entry_v99.add_to_hass(hass)
    assert await async_migrate_entry(hass, entry_v99) is False


async def test_service_registration_registers_expected_services(hass: HomeAssistant) -> None:
    # Use real registration
    await async_register_services(hass)

    expected_services = {
        "control_pump",
        "smart_dosing",
        "manage_pv_surplus",
        "control_dmx_scenes",
        "set_light_color_pulse",
        "manage_digital_rules",
        "test_output",
    }

    for service in expected_services:
        assert hass.services.has_service(DOMAIN, service), f"Service {service} not registered"


async def test_service_registration_is_idempotent(hass: HomeAssistant) -> None:
    # Register once
    await async_register_services(hass)

    # Register twice - should not raise and log debug message
    # We can't easily assert on logs or "not called" without complex patching
    # so we assume if it doesn't crash, it's fine.
    await async_register_services(hass)

    # Ensure services are still there
    assert hass.services.has_service(DOMAIN, "control_pump")
