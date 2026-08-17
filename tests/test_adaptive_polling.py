"""Tests for the coordinator's polling-interval handling.

Regression coverage for three bugs in the previous "dynamic polling" logic:

1. Raw controller states are not always integers. ``"3|PUMP_ANTI_FREEZE"`` or a
   plain ``"1"`` made the comparison raise ``TypeError``, which surfaced as
   ``UpdateFailed`` on *every* poll - the integration never became available.
2. The interval was re-read from ``config_entry.data`` on every poll, so a
   polling interval configured through the options flow was silently discarded
   after the first update.
3. Polling was sped up to half the configured interval whenever the pump ran,
   i.e. the configured value was not respected as the fastest rate.
"""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller.const import (
    ADAPTIVE_IDLE_MAX_INTERVAL,
    CONF_ADAPTIVE_POLLING,
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_POLLING_INTERVAL,
    CONF_USE_SSL,
    DOMAIN,
)
from custom_components.violet_pool_controller.device import (
    VioletPoolControllerDevice,
    VioletPoolDataUpdateCoordinator,
)

IDLE_DATA = {"PUMP": 0, "pH_value": "7.2"}


def _make_entry(data_interval: int = 10, options: dict | None = None) -> MockConfigEntry:
    """Create a config entry with the given polling settings."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Test Pool",
        data={
            CONF_API_URL: "192.168.178.55",
            CONF_USE_SSL: False,
            CONF_DEVICE_ID: 1,
            CONF_DEVICE_NAME: "Test Pool Controller",
            CONF_CONTROLLER_NAME: "Test Pool",
            CONF_POLLING_INTERVAL: data_interval,
        },
        options=options or {},
    )


def _make_coordinator(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    readings: dict,
    polling_interval: int = 30,
    adaptive_polling: bool = True,
) -> VioletPoolDataUpdateCoordinator:
    """Create a coordinator backed by a mocked API returning ``readings``."""
    api = MagicMock()
    api.get_readings = AsyncMock(return_value=readings)
    api.get_output_runtimes = AsyncMock(return_value={})
    api.get_config = AsyncMock(return_value={})
    api.dosing_standalone = False

    with patch(
        "custom_components.violet_pool_controller.device.async_get_clientsession",
        return_value=MagicMock(),
    ):
        device = VioletPoolControllerDevice(hass=hass, config_entry=entry, api=api)

    return VioletPoolDataUpdateCoordinator(
        hass=hass,
        device=device,
        name="test_coordinator",
        polling_interval=polling_interval,
        adaptive_polling=adaptive_polling,
    )


class TestPollingIntervalRobustness:
    """The poll must survive every state representation the controller uses."""

    @pytest.mark.parametrize(
        "pump_state",
        [1, "1", "4", "3|PUMP_ANTI_FREEZE", "0", 0, None, "N/A"],
    )
    async def test_poll_succeeds_for_any_state_representation(
        self, hass: HomeAssistant, pump_state
    ) -> None:
        """A poll must never fail because of how the state is encoded."""
        coordinator = _make_coordinator(
            hass, _make_entry(), {"PUMP": pump_state, "pH_value": "7.2"}
        )

        data = await coordinator._async_update_data()

        assert data["pH_value"] == "7.2"

    @pytest.mark.parametrize("pump_state", ["1", "4", "3|PUMP_ANTI_FREEZE", 1])
    async def test_string_active_state_keeps_configured_interval(
        self, hass: HomeAssistant, pump_state
    ) -> None:
        """An active pump - however encoded - polls at the configured rate."""
        coordinator = _make_coordinator(
            hass, _make_entry(), {"PUMP": pump_state}, polling_interval=30
        )

        await coordinator._async_update_data()

        assert coordinator.update_interval == timedelta(seconds=30)


class TestConfiguredIntervalIsHonoured:
    """The configured interval is the fastest rate, and it comes from options."""

    async def test_options_interval_is_not_overwritten_by_data(
        self, hass: HomeAssistant
    ) -> None:
        """An interval set via the options flow survives a poll."""
        entry = _make_entry(data_interval=10, options={CONF_POLLING_INTERVAL: 60})
        coordinator = _make_coordinator(hass, entry, {"PUMP": 1}, polling_interval=60)

        await coordinator._async_update_data()

        assert coordinator.base_interval == 60
        assert coordinator.update_interval >= timedelta(seconds=60)

    async def test_never_polls_faster_than_configured(self, hass: HomeAssistant) -> None:
        """Running equipment must not shorten the configured interval."""
        coordinator = _make_coordinator(
            hass, _make_entry(), {"PUMP": 1, "DOS_1_CL": 4}, polling_interval=30
        )

        await coordinator._async_update_data()

        assert coordinator.update_interval == timedelta(seconds=30)


class TestIdleBackOff:
    """While nothing runs, the controller is polled less often."""

    async def test_idle_stretches_the_interval(self, hass: HomeAssistant) -> None:
        """Idle equipment triples the interval (capped at the maximum)."""
        coordinator = _make_coordinator(hass, _make_entry(), IDLE_DATA, polling_interval=10)

        await coordinator._async_update_data()

        assert coordinator.update_interval == timedelta(seconds=30)

    async def test_idle_interval_is_capped(self, hass: HomeAssistant) -> None:
        """The back-off never exceeds ADAPTIVE_IDLE_MAX_INTERVAL."""
        coordinator = _make_coordinator(hass, _make_entry(), IDLE_DATA, polling_interval=40)

        await coordinator._async_update_data()

        assert coordinator.update_interval == timedelta(seconds=ADAPTIVE_IDLE_MAX_INTERVAL)

    async def test_configured_interval_wins_over_cap(self, hass: HomeAssistant) -> None:
        """A configured interval above the cap is never shortened."""
        coordinator = _make_coordinator(hass, _make_entry(), IDLE_DATA, polling_interval=300)

        await coordinator._async_update_data()

        assert coordinator.update_interval == timedelta(seconds=300)

    async def test_dosing_counts_as_active(self, hass: HomeAssistant) -> None:
        """Chemical dosing keeps the fast interval even with the pump off."""
        coordinator = _make_coordinator(
            hass, _make_entry(), {"PUMP": 0, "DOS_4_PHM": "4"}, polling_interval=10
        )

        await coordinator._async_update_data()

        assert coordinator.update_interval == timedelta(seconds=10)

    async def test_back_off_disabled_by_option(self, hass: HomeAssistant) -> None:
        """With adaptive polling off, the interval is always the configured one."""
        coordinator = _make_coordinator(
            hass, _make_entry(), IDLE_DATA, polling_interval=10, adaptive_polling=False
        )

        await coordinator._async_update_data()

        assert coordinator.update_interval == timedelta(seconds=10)


class TestApplyPollingOptions:
    """Options changes are applied to the running coordinator."""

    async def test_changed_interval_is_applied(self, hass: HomeAssistant) -> None:
        """A new interval is stored and takes effect immediately."""
        coordinator = _make_coordinator(hass, _make_entry(), IDLE_DATA, polling_interval=10)
        await coordinator._async_update_data()

        assert coordinator.apply_polling_options(45, True) is True
        assert coordinator.base_interval == 45
        assert coordinator.update_interval == timedelta(seconds=45)

    async def test_unchanged_options_report_no_change(self, hass: HomeAssistant) -> None:
        """Saving the options without changes must not trigger a refresh."""
        coordinator = _make_coordinator(hass, _make_entry(), IDLE_DATA, polling_interval=10)
        await coordinator._async_update_data()

        # update_interval is now stretched to 30s, but the configured value is
        # unchanged - this must not be mistaken for a settings change.
        assert coordinator.update_interval == timedelta(seconds=30)
        assert coordinator.apply_polling_options(10, True) is False

    async def test_toggling_adaptive_polling_is_a_change(self, hass: HomeAssistant) -> None:
        """Switching the back-off off is applied without touching the interval."""
        coordinator = _make_coordinator(hass, _make_entry(), IDLE_DATA, polling_interval=10)

        assert coordinator.apply_polling_options(10, False) is True
        assert coordinator.adaptive_polling is False

        await coordinator._async_update_data()
        assert coordinator.update_interval == timedelta(seconds=10)


class TestAdaptivePollingOption:
    """The option is read from the config entry during setup."""

    async def test_option_reaches_the_coordinator(self, hass: HomeAssistant) -> None:
        """``adaptive_polling: False`` in the options disables the back-off."""
        entry = _make_entry(options={CONF_ADAPTIVE_POLLING: False})
        coordinator = _make_coordinator(
            hass,
            entry,
            IDLE_DATA,
            polling_interval=10,
            adaptive_polling=entry.options[CONF_ADAPTIVE_POLLING],
        )

        await coordinator._async_update_data()

        assert coordinator.update_interval == timedelta(seconds=10)
