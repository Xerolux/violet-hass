"""The datapoint selection applies to every platform, not only to sensors.

Until 2.4.1 the selection was read by ``sensor.py`` alone, while the config
flow listed the raw controller keys - so deselecting ``ECO`` removed the ECO
sensor and left its switch, binary sensor and select in place.
"""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller import async_migrate_entry
from custom_components.violet_pool_controller.const import (
    CONF_API_URL,
    CONF_DEVICE_NAME,
    CONF_SELECTED_SENSORS,
    CONFIG_ENTRY_VERSION,
    DOMAIN,
)
from custom_components.violet_pool_controller.const_features import (
    BINARY_SENSORS,
    DMX_LIGHTS,
    SELECT_CONTROLS,
    SWITCHES,
)
from custom_components.violet_pool_controller.entity_selection import (
    DatapointSelection,
    async_get_selection,
)


def _entry(selection: list[str] | None, *, in_options: bool = False, version: int = 2):
    """Create a config entry with the given stored selection."""
    data = {CONF_API_URL: "192.168.178.55", CONF_DEVICE_NAME: "Test Pool Controller"}
    options: dict = {}
    if selection is not None:
        (options if in_options else data)[CONF_SELECTED_SENSORS] = selection
    return MockConfigEntry(domain=DOMAIN, data=data, options=options, version=version)


class TestSelectionSemantics:
    """The rules that keep existing installations safe."""

    def test_no_selection_allows_everything(self) -> None:
        """An entry that never saw the selection step keeps all entities."""
        selection = async_get_selection(_entry(None))

        assert selection.selects_everything
        assert selection.allows("ECO")
        assert selection.allows("ANY_FUTURE_KEY")

    def test_stored_selection_is_exclusive(self) -> None:
        """A stored selection lists exactly what the user wants."""
        selection = async_get_selection(_entry(["PUMP", "onewire1_value"]))

        assert selection.allows("PUMP")
        assert not selection.allows("ECO")

    def test_options_take_precedence_over_data(self) -> None:
        """Changing the selection later must win over the initial setup."""
        entry = _entry(["PUMP"])
        entry.add_to_hass  # noqa: B018 - not added, options are read directly
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_URL: "1.2.3.4", CONF_SELECTED_SENSORS: ["PUMP", "ECO"]},
            options={CONF_SELECTED_SENSORS: ["PUMP"]},
        )

        selection = async_get_selection(entry)

        assert selection.allows("PUMP")
        assert not selection.allows("ECO")

    def test_synthetic_entities_are_never_filtered(self) -> None:
        """Entities without a controller key cannot appear in the list."""
        selection = async_get_selection(_entry(["PUMP"]))

        assert selection.allows(None)

    def test_empty_selection_removes_everything_with_a_key(self) -> None:
        """Deselecting all datapoints is a legitimate choice, not "unset"."""
        selection = async_get_selection(_entry([]))

        assert not selection.selects_everything
        assert not selection.allows("PUMP")
        assert selection.allows(None)


class TestEveryControlPlatformIsCovered:
    """Each platform's key field must be reachable by the selection."""

    @pytest.mark.parametrize(
        ("label", "table", "field"),
        [
            ("switch", SWITCHES, "key"),
            ("binary_sensor", BINARY_SENSORS, "key"),
            ("select", SELECT_CONTROLS, "device_key"),
            ("light", DMX_LIGHTS, "key"),
        ],
    )
    def test_definitions_expose_a_controller_key(self, label, table, field) -> None:
        """Without a key the selection could never reach these entities."""
        missing = [entry.get("key") for entry in table if not entry.get(field)]

        assert not missing, f"{label} definitions without {field}: {missing}"

    def test_a_deselected_key_blocks_its_control(self) -> None:
        """The ECO case from the report, at the level the platforms use."""
        selection = DatapointSelection(keys=frozenset({"PUMP"}))

        assert not selection.allows("ECO")
        assert not selection.allows("DMX_SCENE1")


class TestMigrationKeepsExistingEntities:
    """Nobody may lose an entity by updating."""

    async def _migrate(self, hass, selection, *, in_options=False):
        """Run the migration over an entry with the given stored selection."""
        entry = _entry(selection, in_options=in_options)
        entry.add_to_hass(hass)

        assert await async_migrate_entry(hass, entry) is True
        return entry

    async def test_control_keys_are_added_to_a_sensor_selection(self, hass) -> None:
        """The switch of a deselected sensor key survives the update."""
        entry = await self._migrate(hass, ["onewire1_value"])
        stored = entry.data[CONF_SELECTED_SENSORS]

        assert "onewire1_value" in stored
        assert "PUMP" in stored
        assert "ECO" in stored
        assert "DMX_SCENE1" in stored

    async def test_selection_in_options_is_migrated_too(self, hass) -> None:
        """Selections changed after setup live in the options."""
        entry = await self._migrate(hass, ["onewire1_value"], in_options=True)

        assert "PUMP" in entry.options[CONF_SELECTED_SENSORS]

    async def test_entry_without_a_selection_stays_untouched(self, hass) -> None:
        """No selection means everything - adding keys would be noise."""
        entry = await self._migrate(hass, None)

        assert CONF_SELECTED_SENSORS not in entry.data
        assert entry.version == CONFIG_ENTRY_VERSION

    async def test_no_duplicates_are_introduced(self, hass) -> None:
        """A key the user already selected must not be added twice."""
        entry = await self._migrate(hass, ["PUMP"])
        stored = entry.data[CONF_SELECTED_SENSORS]

        assert stored.count("PUMP") == 1

    async def test_version_is_bumped(self, hass) -> None:
        """The widening runs once, not on every start."""
        entry = await self._migrate(hass, ["PUMP"])

        assert entry.version == CONFIG_ENTRY_VERSION

    async def test_migration_from_version_one_runs_both_steps(self, hass) -> None:
        """A pre-2.4.1 entry gets the features *and* the widened selection."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_API_URL: "192.168.178.55",
                CONF_DEVICE_NAME: "Test",
                "active_features": ["filter_control", "led_lighting"],
                CONF_SELECTED_SENSORS: ["onewire1_value"],
            },
            version=1,
        )
        entry.add_to_hass(hass)

        assert await async_migrate_entry(hass, entry) is True

        assert "eco_mode" in entry.data["active_features"]
        assert "dmx_scenes" in entry.data["active_features"]
        assert "PUMP" in entry.data[CONF_SELECTED_SENSORS]
        assert entry.version == CONFIG_ENTRY_VERSION
