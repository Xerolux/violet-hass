"""Regression tests for switch command confirmation.

The controller may serve a stale readings snapshot for a few seconds after it
applies a command.  A single refresh right after the command can therefore
still report the *old* state.  The switch must keep its optimistic state until
the coordinator data actually confirms the commanded state, otherwise a
successful OFF flips back to ON in the UI for up to a full (adaptive) poll
cycle — observed live as a 30-60 second delay for the OFF confirmation.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components.switch import SwitchEntityDescription
from pytest_homeassistant_custom_component.common import MockConfigEntry

import custom_components.violet_pool_controller.switch as switch_module
from custom_components.violet_pool_controller.const import (
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_USE_SSL,
    DOMAIN,
)
from custom_components.violet_pool_controller.device import VioletPoolControllerDevice
from custom_components.violet_pool_controller.switch import VioletSwitch


@pytest.fixture
def config_entry():
    """Return a mock config entry for the switch entity."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Test Pool",
        data={
            CONF_API_URL: "192.168.178.55",
            CONF_USE_SSL: False,
            CONF_DEVICE_ID: 1,
            CONF_DEVICE_NAME: "Test Pool Controller",
            CONF_CONTROLLER_NAME: "Test Pool",
        },
    )


@pytest.fixture
def mock_api():
    """Return a mock API client whose commands always succeed."""
    api = MagicMock()
    api.dosing_standalone = False
    api.set_switch_state = AsyncMock(return_value={"success": True})
    return api


@pytest.fixture
def device(hass, config_entry, mock_api):
    """Return a device wired to the mock API."""
    with patch(
        "custom_components.violet_pool_controller.device.async_get_clientsession",
        return_value=MagicMock(),
    ):
        return VioletPoolControllerDevice(
            hass=hass,
            config_entry=config_entry,
            api=mock_api,
        )


def _make_switch(device, config_entry, initial_raw_state=4):
    """Build a VioletSwitch with a mocked coordinator.

    The coordinator's ``async_refresh`` is an ``AsyncMock`` that does not touch
    ``data``; individual tests replace it with a side effect to simulate stale
    or confirming controller data.
    """
    coordinator = MagicMock()
    coordinator.device = device
    coordinator.data = {"LIGHTING": initial_raw_state}
    coordinator.last_update_success = True
    coordinator.async_refresh = AsyncMock()
    coordinator.async_request_refresh = AsyncMock()
    entity = VioletSwitch(
        coordinator,
        config_entry,
        SwitchEntityDescription(key="LIGHTING", name="Beleuchtung"),
    )
    entity.async_write_ha_state = MagicMock()
    return entity, coordinator


@pytest.fixture
def fast_delays(monkeypatch):
    """Make all refresh delays near-zero so tests run instantly."""
    monkeypatch.setattr(switch_module, "REFRESH_DELAY", 0.01)
    monkeypatch.setattr(switch_module, "REFRESH_DELAY_EXT", 0.01)
    monkeypatch.setattr(switch_module, "REFRESH_CONFIRM_RETRY_DELAY", 0.01)


async def _await_background_tasks(monkeypatch, awaitable):
    """Run a command and wait for the refresh tasks it spawned."""
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


async def test_off_not_overwritten_by_stale_readings(
    hass, device, config_entry, mock_api, fast_delays, monkeypatch
):
    """A stale first refresh must not flip a confirmed OFF back to ON."""
    entity, coordinator = _make_switch(device, config_entry, initial_raw_state=4)
    responses = [{"LIGHTING": 4}, {"LIGHTING": 6}]  # stale ON, then confirmed OFF

    async def fake_refresh():
        coordinator.data = responses.pop(0)

    coordinator.async_refresh = AsyncMock(side_effect=fake_refresh)

    await _await_background_tasks(monkeypatch, entity.async_turn_off())

    assert entity.is_on is False
    assert entity._optimistic_state is None
    assert coordinator.async_refresh.await_count == 2
    coordinator.async_request_refresh.assert_not_called()
    mock_api.set_switch_state.assert_awaited_once()


async def test_immediate_confirmation_uses_single_refresh(
    hass, device, config_entry, mock_api, fast_delays, monkeypatch
):
    """When the first refresh already confirms the command, do not retry."""
    entity, coordinator = _make_switch(device, config_entry, initial_raw_state=4)

    async def fake_refresh():
        coordinator.data = {"LIGHTING": 6}

    coordinator.async_refresh = AsyncMock(side_effect=fake_refresh)

    await _await_background_tasks(monkeypatch, entity.async_turn_off())

    assert entity.is_on is False
    assert entity._optimistic_state is None
    assert coordinator.async_refresh.await_count == 1


async def test_unconfirmed_command_falls_back_to_reported_state(
    hass, device, config_entry, mock_api, fast_delays, monkeypatch
):
    """If the data never confirms the command, retries are bounded and the
    optimistic state is dropped in favour of the reported state."""
    entity, coordinator = _make_switch(device, config_entry, initial_raw_state=4)

    async def fake_refresh():
        coordinator.data = {"LIGHTING": 4}  # controller keeps reporting ON

    coordinator.async_refresh = AsyncMock(side_effect=fake_refresh)

    await _await_background_tasks(monkeypatch, entity.async_turn_off())

    assert coordinator.async_refresh.await_count == (
        switch_module.REFRESH_CONFIRM_ATTEMPTS
    )
    assert entity._optimistic_state is None
    assert entity.is_on is True  # reported state wins once attempts ran out


async def test_superseded_task_does_not_clear_newer_optimistic_state(
    hass, device, config_entry, fast_delays
):
    """A refresh task from an older command must not clear or overwrite the
    optimistic state of a newer command."""
    entity, coordinator = _make_switch(device, config_entry, initial_raw_state=4)

    # A newer OFF command already set its optimistic state (generation 2) while
    # the refresh task of the older command (generation 1) is still pending.
    entity._optimistic_state = False
    entity._optimistic_generation = 2

    await entity._delayed_refresh("LIGHTING", generation=1)

    assert entity._optimistic_state is False
    coordinator.async_refresh.assert_not_awaited()


async def test_current_generation_task_clears_optimistic_state(
    hass, device, config_entry, fast_delays
):
    """When the refresh task matches the current command, the optimistic state
    is cleared after the data confirms it."""
    entity, coordinator = _make_switch(device, config_entry, initial_raw_state=4)

    async def fake_refresh():
        coordinator.data = {"LIGHTING": 6}

    coordinator.async_refresh = AsyncMock(side_effect=fake_refresh)

    entity._optimistic_state = False
    entity._optimistic_generation = 1
    await entity._delayed_refresh("LIGHTING", generation=1)

    assert entity._optimistic_state is None
    assert coordinator.async_refresh.await_count == 1


async def test_request_coordinator_refresh_bypasses_debouncer(
    hass, device, config_entry, fast_delays
):
    """Command confirmation must use a direct refresh (``async_refresh``), not
    the debounced ``async_request_refresh`` which batches for 10 seconds."""
    entity, coordinator = _make_switch(device, config_entry)

    assert await entity._request_coordinator_refresh(delay=0.01, log_context="LIGHTING")

    coordinator.async_refresh.assert_awaited_once()
    coordinator.async_request_refresh.assert_not_called()
