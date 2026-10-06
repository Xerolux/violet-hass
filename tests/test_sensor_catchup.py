"""Tests for sensor creation when keys appear after the first poll.

Reported on poolsteuerung.de: after a controller restart window the daily
dosing values were present again in the API response, but Home Assistant
never showed them. The data-dependent sensor entities were only created when
their key was part of the FIRST coordinator poll; keys appearing later never
got an entity. These tests pin the catch-up behaviour that closes that gap.
"""

from typing import Any
from unittest.mock import MagicMock

from homeassistant.const import Platform
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller.const import (
    CONF_ACTIVE_FEATURES,
    CONF_API_URL,
    CONF_DEVICE_NAME,
)
from custom_components.violet_pool_controller.runtime_data import VioletRuntimeData
from custom_components.violet_pool_controller.sensor import (
    _create_data_keyed_sensors,
    async_setup_entry,
)

# What the first poll carries while the controller has just restarted and
# omits the computed dosing statistics.
BASE_DATA: dict[str, Any] = {
    "pH_value": 7.2,
    "orp_value": 720,
    "SYSTEM_dosagemodule_alive_count": 1000,
}

# What later polls carry once the controller includes the field groups again.
FULL_DATA: dict[str, Any] = {
    **BASE_DATA,
    "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": 1118,
    "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": 629,
}

ACTIVE_FEATURES = ["filter_control", "chlorine_control", "ph_control"]


def _coordinator(data: dict[str, Any]) -> MagicMock:
    """Return a coordinator mock carrying the given readings."""
    coordinator = MagicMock()
    coordinator.data = data
    coordinator.device.available = True
    coordinator.last_update_success = True
    coordinator.device.device_info = {}
    return coordinator


def _config_entry(hass) -> MockConfigEntry:
    """Add a config entry with the dosing features enabled."""
    entry = MockConfigEntry(
        domain="violet_pool_controller",
        title="Test Pool",
        data={
            CONF_API_URL: "192.168.178.55",
            CONF_DEVICE_NAME: "Test Pool Controller",
            CONF_ACTIVE_FEATURES: ACTIVE_FEATURES,
        },
    )
    entry.add_to_hass(hass)
    return entry


def _description_keys(entities: list) -> set[str]:
    """Return the entity-description keys of the given entities."""
    return {
        entity.entity_description.key
        for entity in entities
        if getattr(entity, "entity_description", None) is not None
    }


async def test_data_keyed_sensors_created_once_key_appears() -> None:
    """A key missing from the first poll gets its entity on the next run."""
    coordinator = _coordinator(dict(BASE_DATA))
    config_entry = MagicMock()
    config = {
        "active_features": set(ACTIVE_FEATURES),
        "selected_sensors": set(),
        "create_all": True,
    }
    handled_keys: set[str] = set()

    first = _create_data_keyed_sensors(coordinator, config_entry, config, handled_keys)
    assert "DOS_1_CL_DAILY_DOSING_AMOUNT_ML" not in _description_keys(first)

    coordinator.data = dict(FULL_DATA)
    second = _create_data_keyed_sensors(coordinator, config_entry, config, handled_keys)
    second_keys = _description_keys(second)
    assert "DOS_1_CL_DAILY_DOSING_AMOUNT_ML" in second_keys
    assert "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML" in second_keys

    third = _create_data_keyed_sensors(coordinator, config_entry, config, handled_keys)
    assert not third, "keys handled once must not produce duplicate entities"


async def test_late_keys_get_entities_after_setup(hass) -> None:
    """Keys appearing after setup get entities without a config reload."""
    coordinator = _coordinator(dict(BASE_DATA))
    config_entry = _config_entry(hass)
    config_entry.runtime_data = VioletRuntimeData(coordinator=coordinator)

    added: list[list] = []

    def add_entities(entities, update_before_add: bool = False) -> None:
        added.append(list(entities))

    await async_setup_entry(hass, config_entry, add_entities)

    # Setup registered the catch-up listener on the coordinator.
    assert coordinator.async_add_listener.called
    listener = coordinator.async_add_listener.call_args[0][0]

    initial_keys = _description_keys(added[0])
    assert "DOS_1_CL_DAILY_DOSING_AMOUNT_ML" not in initial_keys
    tracked_after_setup = set(config_entry.runtime_data.provided_unique_ids[Platform.SENSOR])

    # The controller includes the dosing statistics again; the coordinator
    # pushes the new poll to its listeners.
    coordinator.data = dict(FULL_DATA)
    listener()

    late_keys = _description_keys(added[-1])
    assert "DOS_1_CL_DAILY_DOSING_AMOUNT_ML" in late_keys
    assert "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML" in late_keys

    # The late entities are tracked for the registry cleanup.
    tracked_now = config_entry.runtime_data.provided_unique_ids[Platform.SENSOR]
    late_unique_ids = {entity.unique_id for entity in added[-1]}
    assert tracked_now == tracked_after_setup | late_unique_ids

    # A further poll with the same data must not add anything.
    calls_before = len(added)
    listener()
    assert len(added) == calls_before
