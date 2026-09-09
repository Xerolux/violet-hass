"""Live check: switch command confirmation against a real controller.

Toggles the pool LIGHTING output ON and OFF through the real entity code path
(coordinator, API client, switch entity) and verifies that the entity keeps the
commanded state until the controller data confirms it.  Regression target: a
successful OFF used to flip back to ON for up to a full poll cycle when the
controller still served a stale readings snapshot.

Usage:
    set VIOLET_HOST / VIOLET_USER / VIOLET_PASS, then:
    pytest tests/live_switch_confirmation_check.py -s
"""

import asyncio
import logging
import os
import time
from unittest.mock import MagicMock

import pytest
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.common import MockConfigEntry
from violet_poolcontroller_api.api import VioletPoolAPI

from custom_components.violet_pool_controller.const import (
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_USE_SSL,
    DOMAIN,
)
from custom_components.violet_pool_controller.device import (
    VioletPoolControllerDevice,
    VioletPoolDataUpdateCoordinator,
)
from custom_components.violet_pool_controller.switch import VioletSwitch

HOST = os.environ.get("VIOLET_HOST", "")
USER = os.environ.get("VIOLET_USER", "")
PASS = os.environ.get("VIOLET_PASS", "")

_LOGGER = logging.getLogger(__name__)

pytestmark = pytest.mark.skipif(
    not HOST or not USER or not PASS,
    reason="set VIOLET_HOST/VIOLET_USER/VIOLET_PASS to run the live check",
)

SAMPLE_INTERVAL = 0.2
CONFIRM_TIMEOUT = 20.0


async def _run_direction(entity, action: str) -> list[tuple[float, bool | None]]:
    """Run one command and sample the entity state until confirmation ends.

    Returns the sampled (elapsed_seconds, is_on) series.
    """
    command = entity.async_turn_on if action == "on" else entity.async_turn_off
    t0 = time.monotonic()
    await command()
    samples: list[tuple[float, bool | None]] = []
    while time.monotonic() - t0 < CONFIRM_TIMEOUT:
        samples.append((round(time.monotonic() - t0, 2), entity.is_on))
        if entity._optimistic_state is None:
            break
        await asyncio.sleep(SAMPLE_INTERVAL)
    # Let the refresh task finish its bookkeeping.
    await asyncio.sleep(0.3)
    samples.append((round(time.monotonic() - t0, 2), entity.is_on))
    return samples


def _assert_monotonic_confirmation(
    samples: list[tuple[float, bool | None]], target: bool, direction: str
) -> None:
    """The state must reach the target immediately and never revert while the
    optimistic cache is still active (i.e. within the sampled window)."""
    reached_at: float | None = None
    for elapsed, is_on in samples:
        if reached_at is None and is_on == target:
            reached_at = elapsed
    assert reached_at is not None, f"{direction}: state never reached {target}"
    for elapsed, is_on in samples:
        if elapsed >= reached_at:
            assert is_on == target, (
                f"{direction}: flip-back to {is_on} at {elapsed}s "
                f"(stale data overwrote the confirmed command)"
            )


async def test_lighting_command_confirmation_live(hass):
    """Commanded state must stick until the controller confirms it."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Live Check",
        data={
            CONF_API_URL: HOST,
            CONF_USE_SSL: False,
            CONF_DEVICE_ID: 1,
            CONF_DEVICE_NAME: "Violet Pool Controller",
            CONF_CONTROLLER_NAME: "Live Check",
        },
    )
    config_entry.add_to_hass(hass)

    api = VioletPoolAPI(
        host=HOST,
        session=async_get_clientsession(hass),
        username=USER,
        password=PASS,
    )
    device = VioletPoolControllerDevice(hass=hass, config_entry=config_entry, api=api)
    coordinator = VioletPoolDataUpdateCoordinator(
        hass, device, "live-check", polling_interval=10
    )
    await coordinator.async_refresh()
    assert coordinator.last_update_success, "controller unreachable"

    if "LIGHT" not in (coordinator.data or {}):
        pytest.skip("controller reports no LIGHTING key")

    entity = VioletSwitch(
        coordinator,
        config_entry,
        SwitchEntityDescription(key="LIGHT", name="Beleuchtung"),
    )
    entity.async_write_ha_state = MagicMock()

    initial_raw = coordinator.data.get("LIGHT")
    _LOGGER.info(f"\ninitial LIGHTING raw state: {initial_raw}")

    try:
        if entity.is_on:
            samples = await _run_direction(entity, "off")
            _assert_monotonic_confirmation(samples, False, "pre-test off")

        _LOGGER.info("\n-- ON direction --")
        on_samples = await _run_direction(entity, "on")
        _LOGGER.info(f"samples: {on_samples}")
        _assert_monotonic_confirmation(on_samples, True, "ON")
        _LOGGER.info(f"ON confirmed after {on_samples[-1][0]}s")

        _LOGGER.info("\n-- OFF direction --")
        off_samples = await _run_direction(entity, "off")
        _LOGGER.info(f"samples: {off_samples}")
        _assert_monotonic_confirmation(off_samples, False, "OFF")
        _LOGGER.info(f"OFF confirmed after {off_samples[-1][0]}s")

        # Final data must agree with the last command.
        assert entity.is_on is False
        _LOGGER.info(
            f"\nfinal raw state: {coordinator.data.get('LIGHT')} "
            "(controller and entity agree on OFF)"
        )
    finally:
        # Never leave the light on.
        if entity.is_on:
            await entity.async_turn_off()
            await asyncio.sleep(3)
