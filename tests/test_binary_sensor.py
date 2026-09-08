"""The binary sensors must follow the feature each entry declares.

``BINARY_SENSORS`` carries a ``feature_id`` per entry, but the platform used to
consult a second, hand-written map instead. That map listed neither the twelve
digital inputs nor the four can-empty contacts, so ``INPUT1..12`` and
``INPUT_CE1..4`` appeared regardless of the "Digital Inputs" setting.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller.binary_sensor import (
    VioletBinarySensor,
    async_setup_entry,
)
from custom_components.violet_pool_controller.const import (
    BINARY_SENSORS,
    CONF_ACTIVE_FEATURES,
    CONF_API_URL,
    CONF_DEVICE_NAME,
    DOMAIN,
)
from custom_components.violet_pool_controller.runtime_data import VioletRuntimeData

DIGITAL_INPUT_KEYS = {f"INPUT{i}" for i in range(1, 13)} | {
    f"INPUT_CE{i}" for i in range(1, 5)
}

# Enough data for every table entry to pass the "is this key reported" check.
ALL_DATA = {str(entry["key"]): "0" for entry in BINARY_SENSORS}


def _entry(hass, features: list[str]) -> MockConfigEntry:
    """Return a config entry whose coordinator reports every binary key."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Pool",
        data={
            CONF_API_URL: "192.168.178.55",
            CONF_DEVICE_NAME: "Test Pool Controller",
            CONF_ACTIVE_FEATURES: features,
        },
    )
    entry.add_to_hass(hass)

    coordinator = MagicMock()
    coordinator.data = dict(ALL_DATA)
    coordinator.device.hardware_config = None
    coordinator.device.device_info = {}
    coordinator.last_update_success = True
    coordinator.device.available = True
    entry.runtime_data = VioletRuntimeData(coordinator=coordinator)
    return entry


async def _created_keys(hass, features: list[str]) -> set[str]:
    """Run the platform setup and return the keys it created entities for."""
    entry = _entry(hass, features)
    added: list = []

    def _add(entities, update_before_add=False):
        added.extend(entities)

    await async_setup_entry(hass, entry, _add)
    return {e.entity_description.key for e in added}


class TestFeatureGating:
    """Each entry is gated by the feature it declares in the table."""

    async def test_digital_inputs_are_hidden_when_the_feature_is_off(self, hass) -> None:
        """INPUT1..12 and INPUT_CE1..4 follow the digital_inputs feature."""
        keys = await _created_keys(hass, ["filter_control"])

        assert not (keys & DIGITAL_INPUT_KEYS)

    async def test_digital_inputs_appear_when_the_feature_is_on(self, hass) -> None:
        """Enabling the feature creates all sixteen inputs."""
        keys = await _created_keys(hass, ["digital_inputs"])

        assert DIGITAL_INPUT_KEYS <= keys

    async def test_pump_follows_filter_control(self, hass) -> None:
        """A feature that is off removes its binary sensor."""
        assert "PUMP" in await _created_keys(hass, ["filter_control"])
        assert "PUMP" not in await _created_keys(hass, ["heating"])

    async def test_eco_follows_the_eco_feature(self, hass) -> None:
        """ECO used to be mapped to None, so no setting could remove it."""
        assert "ECO" in await _created_keys(hass, ["eco_mode"])
        assert "ECO" not in await _created_keys(hass, ["filter_control"])

    async def test_ungated_diagnostics_are_always_created(self, hass) -> None:
        """Entries without a feature_id stay available to everyone."""
        assert "HW_BASE_MODULE" in await _created_keys(hass, [])


class TestBinarySensorState:
    """State interpretation follows the shared 0-6 mapping."""

    @staticmethod
    def _sensor(hass, key: str, raw) -> VioletBinarySensor:
        entry = _entry(hass, ["filter_control"])
        entry.runtime_data.coordinator.data = {key: raw}
        return VioletBinarySensor(
            entry.runtime_data.coordinator,
            entry,
            BinarySensorEntityDescription(key=key, name=key, icon="mdi:gauge"),
        )

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [("1", True), ("3", True), ("4", True), ("0", False), ("2", False), ("6", False)],
    )
    def test_is_on(self, hass, raw, expected) -> None:
        """Codes 1, 3 and 4 mean on; 0, 2, 5 and 6 mean off."""
        assert self._sensor(hass, "PUMP", raw).is_on is expected

    def test_icon_is_never_synthesised(self, hass) -> None:
        """The platform used to append "-off", inventing icons like mdi:gauge-off.

        Material Design has no such icon, so Home Assistant rendered nothing.
        The declared icon must be used unchanged in both states.
        """
        assert self._sensor(hass, "PUMP", "0").icon == "mdi:gauge"
        assert self._sensor(hass, "PUMP", "1").icon == "mdi:gauge"
