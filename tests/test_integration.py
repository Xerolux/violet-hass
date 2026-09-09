"""Unit tests for the Violet Pool Controller integration."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from pytest_homeassistant_custom_component.common import MockConfigEntry

import custom_components.violet_pool_controller as integration
from custom_components.violet_pool_controller import (
    PLATFORMS,
    async_migrate_entry,
    async_setup_entry,
    async_unload_entry,
)
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
from custom_components.violet_pool_controller.runtime_data import VioletRuntimeData
from custom_components.violet_pool_controller.services import (
    async_register_services,
)

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


async def test_async_setup_entry_success(
    hass: HomeAssistant, config_entry: MockConfigEntry, coordinator: MagicMock
) -> None:
    # Mock hass.config_entries.async_forward_entry_setups
    # In some HA versions/test setups this might be needed or it's an async method
    hass.config_entries.async_forward_entry_setups = AsyncMock()

    # Both names are bound in the integration package at import time, so the
    # patches have to target that module, not their source modules.
    with (
        patch.object(
            integration,
            "async_setup_device",
            new=AsyncMock(return_value=coordinator),
        ),
        patch.object(
            integration,
            "VioletPoolAPI",
            autospec=True,
        ) as api_cls,
    ):
        result = await async_setup_entry(hass, config_entry)

    assert result is True
    hass.config_entries.async_forward_entry_setups.assert_awaited_once_with(config_entry, PLATFORMS)
    api_cls.assert_called_once()
    assert config_entry.runtime_data.coordinator is coordinator


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

    with (
        patch.object(
            integration,
            "VioletPoolAPI",
            autospec=True,
        ),
        patch.object(
            integration,
            "async_setup_device",
            new=AsyncMock(),
        ),
        pytest.raises(HomeAssistantError),
    ):
        await async_setup_entry(hass, entry)


async def test_async_setup_entry_device_error(
    hass: HomeAssistant, config_entry: MockConfigEntry
) -> None:
    with (
        patch.object(
            integration,
            "async_setup_device",
            new=AsyncMock(side_effect=HomeAssistantError("boom")),
        ),
        patch.object(
            integration,
            "VioletPoolAPI",
            autospec=True,
        ),
        pytest.raises(HomeAssistantError),
    ):
        await async_setup_entry(hass, config_entry)


async def test_async_unload_entry_success(
    hass: HomeAssistant, config_entry: MockConfigEntry, coordinator: MagicMock
) -> None:
    # Setup coordinator mock with api mock
    coordinator.device.api._session.close = AsyncMock()

    config_entry.runtime_data = VioletRuntimeData(coordinator=coordinator)

    # Mock async_unload_platforms on the instance
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    result = await async_unload_entry(hass, config_entry)

    assert result is True
    hass.config_entries.async_unload_platforms.assert_awaited_once()


async def test_async_unload_entry_failure(
    hass: HomeAssistant, config_entry: MockConfigEntry
) -> None:
    config_entry.runtime_data = VioletRuntimeData(coordinator=MagicMock())

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


# ---------------------------------------------------------------------------
# Update listener: a changed connection can only be applied by a reload
# ---------------------------------------------------------------------------


def _listener_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Return a loaded-looking entry whose runtime data records its setup state."""
    from custom_components.violet_pool_controller import _structural_options

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Pool",
        data={
            CONF_API_URL: "192.168.178.55",
            CONF_USE_SSL: False,
            CONF_DEVICE_ID: 1,
            CONF_DEVICE_NAME: "Test Pool Controller",
            "username": "admin",
            "password": "s3cret",
            CONF_POLLING_INTERVAL: 10,
        },
    )
    entry.add_to_hass(hass)

    coordinator = MagicMock()
    coordinator.async_request_refresh = AsyncMock()
    coordinator.apply_polling_options = MagicMock(return_value=False)
    entry.runtime_data = VioletRuntimeData(
        coordinator=coordinator,
        structural_options=_structural_options(entry),
    )
    return entry


async def test_changed_password_reloads_the_entry(hass: HomeAssistant) -> None:
    """The API client is built once, so new credentials need a new client.

    Regression: ``update_api_config`` compared the credentials in the options
    while reading them from the data, so a changed password was applied to
    nothing at all.
    """
    from custom_components.violet_pool_controller import async_update_listener

    entry = _listener_entry(hass)
    hass.config_entries.async_update_entry(
        entry, data={**entry.data, "password": "a-new-secret"}
    )

    with patch.object(hass.config_entries, "async_schedule_reload") as reload_mock:
        await async_update_listener(hass, entry)

    reload_mock.assert_called_once_with(entry.entry_id)


async def test_changed_host_reloads_the_entry(hass: HomeAssistant) -> None:
    """A reconfigured host needs a new API client too."""
    from custom_components.violet_pool_controller import async_update_listener

    entry = _listener_entry(hass)
    hass.config_entries.async_update_entry(
        entry, data={**entry.data, CONF_API_URL: "10.0.0.9"}
    )

    with patch.object(hass.config_entries, "async_schedule_reload") as reload_mock:
        await async_update_listener(hass, entry)

    reload_mock.assert_called_once_with(entry.entry_id)


async def test_polling_change_is_applied_without_a_reload(hass: HomeAssistant) -> None:
    """Polling settings stay hot-applied on the running coordinator."""
    from custom_components.violet_pool_controller import async_update_listener

    entry = _listener_entry(hass)
    entry.runtime_data.coordinator.apply_polling_options = MagicMock(return_value=True)
    hass.config_entries.async_update_entry(entry, options={CONF_POLLING_INTERVAL: 60})

    with patch.object(hass.config_entries, "async_schedule_reload") as reload_mock:
        await async_update_listener(hass, entry)

    reload_mock.assert_not_called()
    entry.runtime_data.coordinator.apply_polling_options.assert_called_once()


# ---------------------------------------------------------------------------
# Migration to config entry version 4
# ---------------------------------------------------------------------------


async def test_migration_strips_the_connection_copy_from_the_options(
    hass: HomeAssistant,
) -> None:
    """Regression: the options flow copied data - password included - into options.

    Because ``get_entry_value`` reads the options first, that stale copy then
    shadowed every later reconfigure of the connection.
    """
    from custom_components.violet_pool_controller.const import (
        CONF_PASSWORD,
        CONF_PORT,
        CONF_USERNAME,
        CONF_VERIFY_SSL,
        CONFIG_ENTRY_VERSION,
    )

    entry = MockConfigEntry(
        domain=DOMAIN,
        version=3,
        data={CONF_API_URL: "192.168.178.55", CONF_PASSWORD: "s3cret"},
        options={
            CONF_API_URL: "192.168.178.55",
            CONF_PORT: 80,
            CONF_USERNAME: "admin",
            CONF_PASSWORD: "s3cret",
            CONF_USE_SSL: False,
            CONF_VERIFY_SSL: False,
            CONF_DEVICE_ID: 1,
            CONF_POLLING_INTERVAL: 30,
        },
    )
    entry.add_to_hass(hass)

    assert await async_migrate_entry(hass, entry) is True

    assert entry.version == CONFIG_ENTRY_VERSION
    for key in (
        CONF_API_URL,
        CONF_PORT,
        CONF_USERNAME,
        CONF_PASSWORD,
        CONF_USE_SSL,
        CONF_VERIFY_SSL,
        CONF_DEVICE_ID,
    ):
        assert key not in entry.options, f"{key} must not survive in the options"
    # A genuine option is untouched.
    assert entry.options[CONF_POLLING_INTERVAL] == 30
    # The authoritative values stay in the entry data.
    assert entry.data[CONF_PASSWORD] == "s3cret"


async def test_migration_moves_the_device_to_the_entry_identifier(
    hass: HomeAssistant,
) -> None:
    """The controller device must survive an IP change.

    Regression: the identifier was ``{host}_{device_id}``, so a reconfigure
    created a second device and orphaned the one the user had named.
    """
    from homeassistant.helpers import device_registry as dr

    entry = MockConfigEntry(
        domain=DOMAIN,
        version=3,
        data={CONF_API_URL: "192.168.178.55", CONF_DEVICE_ID: 1},
    )
    entry.add_to_hass(hass)

    registry = dr.async_get(hass)
    device = registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, "192.168.178.55_1")},
        name="Poolhaus",
    )

    assert await async_migrate_entry(hass, entry) is True

    migrated = registry.async_get(device.id)
    assert migrated is not None
    assert migrated.identifiers == {(DOMAIN, entry.entry_id)}
    assert migrated.name == "Poolhaus"


async def test_migration_without_a_matching_device_is_a_noop(hass: HomeAssistant) -> None:
    """An entry whose device was never created still migrates cleanly."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=3,
        data={CONF_API_URL: "192.168.178.55", CONF_DEVICE_ID: 1},
    )
    entry.add_to_hass(hass)

    assert await async_migrate_entry(hass, entry) is True


# ---------------------------------------------------------------------------
# Device removal
# ---------------------------------------------------------------------------


async def test_main_device_cannot_be_removed_while_loaded(hass: HomeAssistant) -> None:
    """Removing the controller device of a loaded entry only recreates it."""
    from homeassistant.config_entries import ConfigEntryState
    from homeassistant.helpers import device_registry as dr

    from custom_components.violet_pool_controller import async_remove_config_entry_device

    entry = MockConfigEntry(domain=DOMAIN, data={CONF_API_URL: "192.168.178.55"})
    entry.add_to_hass(hass)
    entry.mock_state(hass, ConfigEntryState.LOADED)

    registry = dr.async_get(hass)
    device = registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
    )

    assert await async_remove_config_entry_device(hass, entry, device) is False


async def test_sub_devices_can_always_be_removed(hass: HomeAssistant) -> None:
    """Sub-devices stay removable; they are rebuilt from the next poll."""
    from homeassistant.config_entries import ConfigEntryState
    from homeassistant.helpers import device_registry as dr

    from custom_components.violet_pool_controller import async_remove_config_entry_device

    entry = MockConfigEntry(domain=DOMAIN, data={CONF_API_URL: "192.168.178.55"})
    entry.add_to_hass(hass)
    entry.mock_state(hass, ConfigEntryState.LOADED)

    registry = dr.async_get(hass)
    device = registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, f"{entry.entry_id}_group_heating")},
    )

    assert await async_remove_config_entry_device(hass, entry, device) is True


# ---------------------------------------------------------------------------
# Unsafe switches: one-off pass, not a per-start enforcement
# ---------------------------------------------------------------------------


def _register_unsafe_switch(hass: HomeAssistant, entry: MockConfigEntry):
    """Register an enabled REFILL switch for the entry and return its entry."""
    from homeassistant.helpers import entity_registry as er

    registry = er.async_get(hass)
    return registry.async_get_or_create(
        "switch",
        DOMAIN,
        f"{entry.entry_id}_REFILL",
        config_entry=entry,
    )


async def test_unsafe_switch_pass_runs_once_and_records_it(hass: HomeAssistant) -> None:
    """The one-off pass disables the pre-existing unsafe switch exactly once."""
    from homeassistant.helpers import entity_registry as er

    from custom_components.violet_pool_controller import _disable_unsafe_switches
    from custom_components.violet_pool_controller.const import (
        CONF_UNSAFE_SWITCHES_MIGRATED,
    )

    entry = MockConfigEntry(domain=DOMAIN, data={CONF_API_URL: "192.168.178.55"})
    entry.add_to_hass(hass)
    entity = _register_unsafe_switch(hass, entry)

    registry = er.async_get(hass)
    _disable_unsafe_switches(hass, registry, entry.entry_id)

    assert registry.async_get(entity.entity_id).disabled_by is (
        er.RegistryEntryDisabler.INTEGRATION
    )
    assert entry.options[CONF_UNSAFE_SWITCHES_MIGRATED] is True


async def test_user_reenabled_unsafe_switch_survives_a_restart(hass: HomeAssistant) -> None:
    """Regression: the pass ran on every start and undid the user's decision.

    switch.py already creates every unsafe switch with
    ``entity_registry_enabled_default`` derived from the same option, so the
    per-start pass had nothing left to do except fight the user.
    """
    from homeassistant.helpers import entity_registry as er

    from custom_components.violet_pool_controller import _disable_unsafe_switches

    entry = MockConfigEntry(domain=DOMAIN, data={CONF_API_URL: "192.168.178.55"})
    entry.add_to_hass(hass)
    entity = _register_unsafe_switch(hass, entry)

    registry = er.async_get(hass)
    _disable_unsafe_switches(hass, registry, entry.entry_id)

    # The user deliberately re-enables the switch in the UI.
    registry.async_update_entity(entity.entity_id, disabled_by=None)

    # Next Home Assistant start.
    _disable_unsafe_switches(hass, registry, entry.entry_id)

    assert registry.async_get(entity.entity_id).disabled_by is None
