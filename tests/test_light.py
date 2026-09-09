"""The DMX scene lights must follow the feature they declare.

Every entry in ``DMX_LIGHTS`` carries ``feature_id: "dmx_scenes"``, but the
light platform used to gate itself on ``led_lighting`` and never read that
field. Turning the scenes off left twelve lights in place, and turning the
plain pool light off removed all of them.

The command tests additionally cover the confirmation behaviour the switch
platform has: the controller can serve a stale readings snapshot for a few
seconds after a command, so the optimistic state must be kept until the
reported state confirms the command.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.components.light import LightEntityDescription
from homeassistant.const import Platform
from pytest_homeassistant_custom_component.common import MockConfigEntry

import custom_components.violet_pool_controller.light as light_module
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


class TestDmxCommandConfirmation:
    """A commanded scene state must stick until the controller confirms it."""

    @pytest.fixture(autouse=True)
    def _fast_delays(self, monkeypatch):
        """Make the confirmation delays near-zero so tests run instantly."""
        monkeypatch.setattr(light_module, "REFRESH_DELAY", 0.01)
        monkeypatch.setattr(light_module, "REFRESH_CONFIRM_RETRY_DELAY", 0.01)

    def _make_light(self, hass, initial_raw="4"):
        """Return (light, coordinator) with a command-succeeding mock API."""
        entry = _entry(hass, ["dmx_scenes"], data={"DMX_SCENE1": initial_raw})
        coordinator = entry.runtime_data.coordinator
        coordinator.device.api.set_switch_state = AsyncMock(
            return_value={"success": True}
        )
        coordinator.async_refresh = AsyncMock()
        coordinator.async_request_refresh = AsyncMock()
        light = VioletDmxLight(
            coordinator,
            entry,
            LightEntityDescription(key="DMX_SCENE1", name="DMX Scene 1"),
        )
        light.async_write_ha_state = MagicMock()
        return light, coordinator

    async def _run_command(self, monkeypatch, awaitable):
        """Run a command and wait for the confirmation task it spawned."""
        tasks: list[asyncio.Task] = []
        real_create_task = asyncio.create_task

        def tracking_create_task(coro, **kwargs):
            task = real_create_task(coro, **kwargs)
            tasks.append(task)
            return task

        monkeypatch.setattr(asyncio, "create_task", tracking_create_task)
        await awaitable
        if tasks:
            await asyncio.gather(*tasks)

    async def test_off_not_overwritten_by_stale_readings(self, hass, monkeypatch):
        """A stale first refresh must not flip a confirmed OFF back to ON."""
        light, coordinator = self._make_light(hass, initial_raw="4")
        responses = [{"DMX_SCENE1": "4"}, {"DMX_SCENE1": "6"}]

        async def fake_refresh():
            coordinator.data = responses.pop(0)

        coordinator.async_refresh = AsyncMock(side_effect=fake_refresh)

        await self._run_command(monkeypatch, light.async_turn_off())

        assert light.is_on is False
        assert light._optimistic_state is None
        assert coordinator.async_refresh.await_count == 2
        coordinator.async_request_refresh.assert_not_called()

    async def test_immediate_confirmation_uses_single_refresh(self, hass, monkeypatch):
        """When the first refresh already confirms, do not retry."""
        light, coordinator = self._make_light(hass, initial_raw="4")

        async def fake_refresh():
            coordinator.data = {"DMX_SCENE1": "6"}

        coordinator.async_refresh = AsyncMock(side_effect=fake_refresh)

        await self._run_command(monkeypatch, light.async_turn_off())

        assert light.is_on is False
        assert coordinator.async_refresh.await_count == 1

    async def test_unconfirmed_command_falls_back_to_reported_state(
        self, hass, monkeypatch
    ):
        """Retries are bounded; the reported state wins when they run out."""
        light, coordinator = self._make_light(hass, initial_raw="4")

        async def fake_refresh():
            coordinator.data = {"DMX_SCENE1": "4"}

        coordinator.async_refresh = AsyncMock(side_effect=fake_refresh)

        await self._run_command(monkeypatch, light.async_turn_off())

        assert coordinator.async_refresh.await_count == (
            light_module.REFRESH_CONFIRM_ATTEMPTS
        )
        assert light._optimistic_state is None
        assert light.is_on is True

    async def test_superseded_task_keeps_newer_optimistic_state(self, hass):
        """A confirmation task of an older command may not clear a newer one."""
        light, coordinator = self._make_light(hass, initial_raw="4")

        light._optimistic_state = False
        light._optimistic_generation = 2

        await light._confirm_command("DMX_SCENE1", generation=1)

        assert light._optimistic_state is False
        coordinator.async_refresh.assert_not_awaited()
