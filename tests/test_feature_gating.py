"""Every entity must be removable through some setting.

Reported on the forum after 2.4.0: deselecting everything ECO- and DMX-related
left the entities in place. Root cause: the sensor selection only gates the
sensor platform, and ECO carried no feature id at all - no setting could remove
its switch, binary sensor or select. DMX scenes hung off "LED Lighting", so
deselecting the DMX *sensors* never touched the scene lights.
"""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller import async_migrate_entry
from custom_components.violet_pool_controller.const import (
    AVAILABLE_FEATURES,
    CONF_ACTIVE_FEATURES,
    CONF_API_URL,
    CONF_DEVICE_NAME,
    CONFIG_ENTRY_VERSION,
    DOMAIN,
)
from custom_components.violet_pool_controller.const_features import (
    BINARY_SENSORS,
    DMX_LIGHTS,
    SELECT_CONTROLS,
    SWITCHES,
)
from custom_components.violet_pool_controller.const_sensors import SENSOR_FEATURE_MAP

FEATURE_IDS = {feature["id"] for feature in AVAILABLE_FEATURES}

# (label, table, key field)
ENTITY_TABLES = (
    ("switch", SWITCHES, "key"),
    ("binary_sensor", BINARY_SENSORS, "key"),
    ("select", SELECT_CONTROLS, "key"),
    ("light", DMX_LIGHTS, "key"),
)


def _enabled_by_default(entry: dict) -> bool:
    """Return whether Home Assistant creates this entity enabled."""
    return bool(entry.get("entity_registry_enabled_default", True))


class TestEveryVisibleEntityCanBeSwitchedOff:
    """An entity a user sees must be removable through a feature."""

    @pytest.mark.parametrize(("label", "table", "field"), ENTITY_TABLES)
    def test_enabled_entities_declare_a_feature(self, label, table, field) -> None:
        """No enabled-by-default entity may be ungated.

        Disabled-by-default diagnostics are exempt: they are hidden until a user
        explicitly enables them, so they cannot clutter anything.
        """
        ungated = [
            entry[field]
            for entry in table
            if _enabled_by_default(entry) and not entry.get("feature_id")
        ]

        assert not ungated, f"{label} entities without a feature_id: {ungated}"

    @pytest.mark.parametrize(("label", "table", "field"), ENTITY_TABLES)
    def test_feature_ids_exist(self, label, table, field) -> None:
        """A feature id nobody offers in the config flow can never be enabled."""
        unknown = {
            str(entry.get("feature_id"))
            for entry in table
            if entry.get("feature_id") and entry["feature_id"] not in FEATURE_IDS
        }

        assert not unknown, f"{label} references unknown features: {sorted(unknown)}"

    def test_sensor_feature_map_only_uses_known_features(self) -> None:
        """The same guarantee for the sensor platform's mapping."""
        unknown = {
            value for value in SENSOR_FEATURE_MAP.values() if value and value not in FEATURE_IDS
        }

        assert not unknown, f"SENSOR_FEATURE_MAP references unknown features: {sorted(unknown)}"


class TestEcoIsGated:
    """ECO was the entity family no setting could remove."""

    @pytest.mark.parametrize(("label", "table", "field"), ENTITY_TABLES)
    def test_eco_entities_belong_to_the_eco_feature(self, label, table, field) -> None:
        """Switch, binary sensor and select must all follow eco_mode."""
        for entry in table:
            key = str(entry.get("device_key") or entry.get(field))
            if key == "ECO":
                assert entry.get("feature_id") == "eco_mode", (
                    f"{label} entity {key} is not gated by eco_mode"
                )

    def test_eco_sensors_belong_to_the_eco_feature(self) -> None:
        """The ECO sensors follow the same feature as the other ECO entities."""
        assert SENSOR_FEATURE_MAP.get("ECO") == "eco_mode"
        assert SENSOR_FEATURE_MAP.get("ECO_RUNTIME") == "eco_mode"


class TestDmxScenesAreTheirOwnFeature:
    """Twelve scene lights should not be tied to the plain pool light."""

    def test_scene_lights_use_the_dmx_feature(self) -> None:
        """All twelve DMX scenes follow dmx_scenes."""
        assert DMX_LIGHTS, "no DMX scenes defined"
        assert {entry["feature_id"] for entry in DMX_LIGHTS} == {"dmx_scenes"}

    def test_dmx_sensors_follow_the_scene_lights(self) -> None:
        """The DMX readings move with the scenes, not with the pool light."""
        assert SENSOR_FEATURE_MAP.get("DMX_MODE") == "dmx_scenes"
        assert SENSOR_FEATURE_MAP.get("DMX_SCENE1") == "dmx_scenes"

    def test_plain_light_stays_with_led_lighting(self) -> None:
        """Turning off the scenes must not take the pool light with it."""
        assert SENSOR_FEATURE_MAP.get("LIGHT") == "led_lighting"


class TestConfigEntryMigration:
    """Existing entries must not silently lose entities on update."""

    async def _migrate(self, hass, features: list[str] | None, version: int = 1):
        """Run the migration over an entry with the given stored features."""
        data = {CONF_API_URL: "192.168.178.55", CONF_DEVICE_NAME: "Test Pool Controller"}
        if features is not None:
            data[CONF_ACTIVE_FEATURES] = features
        entry = MockConfigEntry(domain=DOMAIN, data=data, version=version)
        entry.add_to_hass(hass)

        assert await async_migrate_entry(hass, entry) is True
        return entry

    async def test_eco_is_enabled_for_existing_entries(self, hass) -> None:
        """ECO was always on, so it stays on."""
        entry = await self._migrate(hass, ["filter_control", "heating"])

        assert "eco_mode" in entry.data[CONF_ACTIVE_FEATURES]

    async def test_dmx_inherits_the_lighting_setting(self, hass) -> None:
        """Someone using the lighting keeps their scenes."""
        entry = await self._migrate(hass, ["filter_control", "led_lighting"])

        assert "dmx_scenes" in entry.data[CONF_ACTIVE_FEATURES]

    async def test_dmx_stays_off_when_lighting_was_off(self, hass) -> None:
        """Someone who disabled the lighting must not suddenly get 12 scenes."""
        entry = await self._migrate(hass, ["filter_control"])

        assert "dmx_scenes" not in entry.data[CONF_ACTIVE_FEATURES]

    async def test_version_is_bumped(self, hass) -> None:
        """A migrated entry is not migrated again on the next start."""
        entry = await self._migrate(hass, ["filter_control"])

        assert entry.version == CONFIG_ENTRY_VERSION

    async def test_entry_without_a_selection_is_left_alone(self, hass) -> None:
        """No stored selection means "everything" - nothing to add."""
        entry = await self._migrate(hass, None)

        assert CONF_ACTIVE_FEATURES not in entry.data
        assert entry.version == CONFIG_ENTRY_VERSION

    async def test_current_version_is_a_no_op(self, hass) -> None:
        """Migrating an up-to-date entry must not duplicate ids."""
        entry = await self._migrate(
            hass, ["filter_control", "eco_mode"], version=CONFIG_ENTRY_VERSION
        )

        assert entry.data[CONF_ACTIVE_FEATURES].count("eco_mode") == 1

    async def test_future_version_is_refused(self, hass) -> None:
        """An entry from a newer integration version must not be downgraded."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_URL: "192.168.178.55", CONF_DEVICE_NAME: "Test"},
            version=CONFIG_ENTRY_VERSION + 1,
        )
        entry.add_to_hass(hass)

        assert await async_migrate_entry(hass, entry) is False
