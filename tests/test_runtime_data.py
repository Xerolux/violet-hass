"""Tests for the per-entry runtime data.

The coordinator and the per-entry bookkeeping used to live in
``hass.data[DOMAIN]`` under string keys, mixed with integration-wide objects
such as the service manager. They now live on ``entry.runtime_data``, which
Home Assistant manages together with the entry lifecycle.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller.const import (
    CONF_API_URL,
    CONF_DEVICE_NAME,
    DOMAIN,
)
from custom_components.violet_pool_controller.runtime_data import (
    VioletRuntimeData,
    async_all_coordinators,
    async_get_coordinator,
    async_loaded_entries,
    get_runtime_data,
)


def _add_entry(hass: HomeAssistant, title: str = "Test Pool") -> MockConfigEntry:
    """Add a config entry to hass."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=title,
        data={CONF_API_URL: "192.168.178.55", CONF_DEVICE_NAME: title},
    )
    entry.add_to_hass(hass)
    return entry


class TestGetRuntimeData:
    """get_runtime_data tolerates entries that are not set up."""

    async def test_returns_none_without_runtime_data(self, hass: HomeAssistant) -> None:
        """An entry that never went through setup has no runtime data."""
        assert get_runtime_data(_add_entry(hass)) is None

    async def test_returns_none_for_foreign_runtime_data(self, hass: HomeAssistant) -> None:
        """Runtime data of a different shape must not be handed out."""
        entry = _add_entry(hass)
        entry.runtime_data = {"coordinator": MagicMock()}

        assert get_runtime_data(entry) is None

    async def test_returns_the_runtime_data(self, hass: HomeAssistant) -> None:
        """A set-up entry returns its own runtime data."""
        entry = _add_entry(hass)
        runtime_data = VioletRuntimeData(coordinator=MagicMock())
        entry.runtime_data = runtime_data

        assert get_runtime_data(entry) is runtime_data


class TestCoordinatorLookup:
    """Coordinators are resolved through the config entries."""

    async def test_coordinator_by_entry_id(self, hass: HomeAssistant) -> None:
        """A loaded entry id resolves to its coordinator."""
        entry = _add_entry(hass)
        coordinator = MagicMock()
        entry.runtime_data = VioletRuntimeData(coordinator=coordinator)

        assert async_get_coordinator(hass, entry.entry_id) is coordinator

    async def test_unknown_entry_id(self, hass: HomeAssistant) -> None:
        """An unknown id resolves to None instead of raising."""
        assert async_get_coordinator(hass, "does-not-exist") is None

    async def test_unloaded_entry(self, hass: HomeAssistant) -> None:
        """An entry without runtime data resolves to None."""
        entry = _add_entry(hass)

        assert async_get_coordinator(hass, entry.entry_id) is None

    async def test_all_coordinators_skips_unloaded_entries(self, hass: HomeAssistant) -> None:
        """Multi-controller setups only report the loaded entries."""
        loaded = _add_entry(hass, "Pool A")
        _add_entry(hass, "Pool B")
        coordinator = MagicMock()
        loaded.runtime_data = VioletRuntimeData(coordinator=coordinator)

        assert async_all_coordinators(hass) == [coordinator]
        assert async_loaded_entries(hass) == [loaded]


class TestRuntimeDataDefaults:
    """The per-entry stores start empty and are independent per entry."""

    @pytest.mark.parametrize(
        "attribute",
        ["structural_options", "device_ids", "provided_unique_ids", "calculator_inputs"],
    )
    async def test_stores_start_empty(self, hass: HomeAssistant, attribute) -> None:
        """Every bookkeeping store defaults to an empty dict."""
        runtime_data = VioletRuntimeData(coordinator=MagicMock())

        assert getattr(runtime_data, attribute) == {}

    async def test_stores_are_not_shared_between_entries(self, hass: HomeAssistant) -> None:
        """Two controllers must not write into the same store."""
        first = VioletRuntimeData(coordinator=MagicMock())
        second = VioletRuntimeData(coordinator=MagicMock())

        first.device_ids["__main__"] = "abc"

        assert second.device_ids == {}
