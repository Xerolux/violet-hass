"""The DMX scene lights must follow the feature they declare.

Every entry in ``DMX_LIGHTS`` carries ``feature_id: "dmx_scenes"``, but the
light platform used to gate itself on ``led_lighting`` and never read that
field. Turning the scenes off left twelve lights in place, and turning the
plain pool light off removed all of them.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from homeassistant.const import Platform
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller.const import (
    CONF_ACTIVE_FEATURES,
    CONF_API_URL,
    CONF_DEVICE_NAME,
    DMX_LIGHTS,
    DOMAIN,
)
from custom_components.violet_pool_controller.light import (
    VioletDmxLight,
    async_setup_entry,
)
from custom_components.violet_pool_controller.runtime_data import VioletRuntimeData

SCENE_DATA = {entry["key"]: "0" for entry in DMX_LIGHTS}


def _entry(hass, features: list[str], data: dict | None = None) -> MockConfigEntry:
    """Return a config entry whose coordinator reports every DMX scene."""
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
    coordinator.data = SCENE_DATA if data is None else data
    coordinator.device.hardware_config = None
    coordinator.device.device_info = {}
    coordinator.last_update_success = True
    coordinator.device.available = True
    entry.runtime_data = VioletRuntimeData(coordinator=coordinator)
    return entry


async def _setup(hass, features: list[str]) -> list:
    """Run the light platform setup and return the entities it created."""
    entry = _entry(hass, features)
    added: list = []

    def _add(entities, update_before_add=False):
        added.extend(entities)

    await async_setup_entry(hass, entry, _add)
    assert entry.runtime_data.provided_unique_ids.get(Platform.LIGHT) is not None
    return added


class TestDmxLightFeatureGating:
    """The scenes belong to dmx_scenes, not to led_lighting."""

    async def test_led_lighting_alone_creates_no_scene_lights(self, hass) -> None:
        """The plain pool light must not drag in twelve scene lights."""
        assert await _setup(hass, ["led_lighting"]) == []

    async def test_dmx_scenes_creates_all_twelve(self, hass) -> None:
        """Enabling the scenes creates one light per scene."""
        entities = await _setup(hass, ["dmx_scenes"])

        assert len(entities) == 12
        assert {e.entity_description.key for e in entities} == set(SCENE_DATA)

    async def test_both_features_still_creates_twelve(self, hass) -> None:
        """led_lighting neither adds nor removes scene lights."""
        assert len(await _setup(hass, ["dmx_scenes", "led_lighting"])) == 12


class TestDmxLightState:
    """A scene reports on for the active state codes only."""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("0", False),
            ("1", True),
            ("2", False),  # rule-blocked OFF
            ("3", True),
            ("4", True),
            ("5", False),
            ("6", False),
            ("4|DMX_MANUAL", True),  # composite state
            ("2|DMX_BLOCKED", False),
            ("[]", None),
            (None, None),
        ],
    )
    def test_is_on_reads_the_state_code(self, hass, raw, expected) -> None:
        """Composite values carry the state code in their leading part."""
        entry = _entry(hass, ["dmx_scenes"], data={"DMX_SCENE1": raw})
        description = MagicMock()
        description.key = "DMX_SCENE1"
        description.name = "DMX Scene 1"
        description.translation_key = "dmx_scene1"
        light = VioletDmxLight(entry.runtime_data.coordinator, entry, description)

        assert light.is_on is expected
