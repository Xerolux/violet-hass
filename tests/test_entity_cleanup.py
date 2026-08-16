"""Tests for the feature selection actually taking effect.

Covers the two halves of the fix:

* :mod:`custom_components.violet_pool_controller.entity_cleanup` removes
  registry entries that the platforms no longer provide.
* ``async_update_listener`` reloads the config entry when the feature or
  sensor selection changed.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import Platform
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller import (
    _structural_options,
    _structural_options_key,
    async_update_listener,
)
from custom_components.violet_pool_controller.const import (
    CONF_ACTIVE_FEATURES,
    CONF_API_URL,
    CONF_DEVICE_NAME,
    CONF_POLLING_INTERVAL,
    CONF_SELECTED_SENSORS,
    DOMAIN,
)
from custom_components.violet_pool_controller.entity_cleanup import (
    async_remove_orphaned_entities,
    discard_provided_entities,
    track_provided_entities,
)

ALL_PLATFORMS = [Platform.SENSOR, Platform.LIGHT]


def _entity(unique_id):
    """Return a stub entity exposing only the unique_id."""
    entity = MagicMock()
    entity.unique_id = unique_id
    return entity


@pytest.fixture
def config_entry(hass):
    """Add a config entry to hass."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Pool",
        data={
            CONF_API_URL: "192.168.178.55",
            CONF_DEVICE_NAME: "Test Pool Controller",
            CONF_ACTIVE_FEATURES: ["filter_control", "led_lighting"],
        },
    )
    entry.add_to_hass(hass)
    return entry


def _register(hass, config_entry, domain, unique_id):
    """Create an entity registry entry for the config entry."""
    return er.async_get(hass).async_get_or_create(
        domain,
        DOMAIN,
        unique_id,
        config_entry=config_entry,
    )


class TestOrphanedEntityRemoval:
    """Test that entities of disabled features disappear from the registry."""

    async def test_removes_entities_no_longer_provided(self, hass, config_entry):
        """A DMX light that is no longer provided must be removed."""
        kept = _register(hass, config_entry, "sensor", f"{config_entry.entry_id}_pH_value")
        stale = _register(hass, config_entry, "light", f"{config_entry.entry_id}_DMX_SCENE1")

        track_provided_entities(hass, config_entry, Platform.SENSOR, [_entity(kept.unique_id)])
        # led_lighting disabled -> the light platform provides nothing
        track_provided_entities(hass, config_entry, Platform.LIGHT, [])

        removed = async_remove_orphaned_entities(hass, config_entry, ALL_PLATFORMS)

        registry = er.async_get(hass)
        assert removed == 1
        assert registry.async_get(kept.entity_id) is not None
        assert registry.async_get(stale.entity_id) is None

    async def test_keeps_registry_disabled_entities(self, hass, config_entry):
        """Entities that are disabled in the registry are still provided."""
        disabled = _register(hass, config_entry, "light", f"{config_entry.entry_id}_DMX_SCENE1")
        er.async_get(hass).async_update_entity(
            disabled.entity_id, disabled_by=er.RegistryEntryDisabler.USER
        )

        # The platform still reports it even though HA never instantiates it.
        track_provided_entities(hass, config_entry, Platform.SENSOR, [])
        track_provided_entities(hass, config_entry, Platform.LIGHT, [_entity(disabled.unique_id)])

        assert async_remove_orphaned_entities(hass, config_entry, ALL_PLATFORMS) == 0
        assert er.async_get(hass).async_get(disabled.entity_id) is not None

    async def test_skips_cleanup_when_a_platform_did_not_report(self, hass, config_entry):
        """A platform that failed to set up must not cause entity removal."""
        existing = _register(hass, config_entry, "light", f"{config_entry.entry_id}_DMX_SCENE1")

        track_provided_entities(
            hass, config_entry, Platform.SENSOR, [_entity(f"{config_entry.entry_id}_pH_value")]
        )
        # No report from the light platform.

        assert async_remove_orphaned_entities(hass, config_entry, ALL_PLATFORMS) == 0
        assert er.async_get(hass).async_get(existing.entity_id) is not None

    async def test_skips_cleanup_when_nothing_was_provided(self, hass, config_entry):
        """An empty result set is treated as a failed setup, not as a wipe."""
        existing = _register(hass, config_entry, "sensor", f"{config_entry.entry_id}_pH_value")

        for platform in ALL_PLATFORMS:
            track_provided_entities(hass, config_entry, platform, [])

        assert async_remove_orphaned_entities(hass, config_entry, ALL_PLATFORMS) == 0
        assert er.async_get(hass).async_get(existing.entity_id) is not None

    async def test_discard_clears_the_reported_ids(self, hass, config_entry):
        """Unloading drops the bookkeeping so the next setup starts clean."""
        track_provided_entities(hass, config_entry, Platform.SENSOR, [_entity("x")])
        discard_provided_entities(hass, config_entry)

        assert async_remove_orphaned_entities(hass, config_entry, ALL_PLATFORMS) == 0


class TestStructuralOptionReload:
    """Test that changing the selection reloads the entry."""

    @pytest.fixture
    def hass_with_coordinator(self, hass, config_entry):
        """Register a coordinator plus the applied structural options."""
        coordinator = MagicMock()
        coordinator.async_request_refresh = AsyncMock()
        coordinator.device.update_api_config = AsyncMock(return_value=False)
        hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = coordinator
        hass.data[DOMAIN][_structural_options_key(config_entry)] = _structural_options(config_entry)
        return hass

    async def test_feature_change_triggers_reload(self, hass_with_coordinator, config_entry):
        """Disabling a feature must re-run the platform setups."""
        hass = hass_with_coordinator
        hass.config_entries.async_update_entry(
            config_entry, options={CONF_ACTIVE_FEATURES: ["filter_control"]}
        )

        with patch.object(hass.config_entries, "async_schedule_reload") as reload_mock:
            await async_update_listener(hass, config_entry)

        reload_mock.assert_called_once_with(config_entry.entry_id)

    async def test_sensor_selection_change_triggers_reload(
        self, hass_with_coordinator, config_entry
    ):
        """Deselecting a sensor must re-run the platform setups."""
        hass = hass_with_coordinator
        hass.config_entries.async_update_entry(
            config_entry, options={CONF_SELECTED_SENSORS: ["pH_value"]}
        )

        with patch.object(hass.config_entries, "async_schedule_reload") as reload_mock:
            await async_update_listener(hass, config_entry)

        reload_mock.assert_called_once_with(config_entry.entry_id)

    async def test_feature_reordering_does_not_reload(self, hass_with_coordinator, config_entry):
        """The selection is a set - a different order is not a change."""
        hass = hass_with_coordinator
        hass.config_entries.async_update_entry(
            config_entry, options={CONF_ACTIVE_FEATURES: ["led_lighting", "filter_control"]}
        )

        with patch.object(hass.config_entries, "async_schedule_reload") as reload_mock:
            await async_update_listener(hass, config_entry)

        reload_mock.assert_not_called()

    async def test_polling_interval_change_does_not_reload(
        self, hass_with_coordinator, config_entry
    ):
        """Settings that are applied on the live coordinator must not reload."""
        hass = hass_with_coordinator
        hass.config_entries.async_update_entry(config_entry, options={CONF_POLLING_INTERVAL: 60})

        with patch.object(hass.config_entries, "async_schedule_reload") as reload_mock:
            await async_update_listener(hass, config_entry)

        reload_mock.assert_not_called()
