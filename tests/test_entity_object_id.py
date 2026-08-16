"""Tests for language-independent entity_ids.

Home Assistant derives the entity_id from the *translated* entity name for
languages listed in ``NATIVE_ENTITY_IDS`` (German among them). Without an
explicit ``suggested_object_id`` a German installation ends up with different
entity_ids than an English one, which breaks every shared dashboard.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.config_entries import ConfigEntry

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from custom_components.violet_pool_controller.entity import (  # noqa: E402
    VioletPoolControllerEntity,
)

_TRANSLATION_KEY = "component.violet_pool_controller.entity.sensor.pool_temperature.name"


def _platform_data(language_name: str) -> MagicMock:
    """Return stub platform data with a German UI and English object ids."""
    platform_data = MagicMock()
    platform_data.domain = "sensor"
    platform_data.platform_name = "violet_pool_controller"
    platform_data.platform_translations = {_TRANSLATION_KEY: language_name}
    platform_data.object_id_platform_translations = {_TRANSLATION_KEY: language_name}
    platform_data.default_language_platform_translations = {_TRANSLATION_KEY: "Pool Temperature"}
    platform_data.component_translations = {}
    platform_data.object_id_component_translations = {}
    return platform_data


def _attach(entity: VioletPoolControllerEntity, platform_data: MagicMock | None) -> None:
    """Attach stub platform data under both the new and the old HA attribute.

    Home Assistant 2026.x exposes the platform translations via
    ``Entity.platform_data``; releases before that use ``Entity.platform``.
    """
    entity.platform_data = platform_data
    entity.platform = platform_data


@pytest.fixture
def entity() -> VioletPoolControllerEntity:
    """Create a base entity with a translated sensor description."""
    coordinator = MagicMock()
    coordinator.device.device_name = "Violet Pool Controller"
    coordinator.device.controller_name = "Violet Pool Controller"
    coordinator.device.device_info = {}

    config_entry = MagicMock(spec=ConfigEntry)
    config_entry.entry_id = "test_entry"

    description = SensorEntityDescription(
        key="onewire1_value",
        name="Pool Temperature",
        translation_key="pool_temperature",
    )
    return VioletPoolControllerEntity(coordinator, config_entry, description)


def test_object_id_stays_english_for_translated_entity(entity):
    """The German name is displayed, but the entity_id is derived in English."""
    _attach(entity, _platform_data("Wassertemperatur"))

    assert entity.name == "Wassertemperatur"
    assert entity.suggested_object_id == "Pool Temperature"


def test_object_id_matches_name_on_english_installs(entity):
    """English installations are unaffected by the override."""
    _attach(entity, _platform_data("Pool Temperature"))

    assert entity.name == "Pool Temperature"
    assert entity.suggested_object_id == "Pool Temperature"


def test_untranslated_entity_falls_back_to_description_name(entity):
    """Dynamic sensors without a translation keep their English description name."""
    platform_data = _platform_data("Wassertemperatur")
    platform_data.platform_translations = {}
    platform_data.object_id_platform_translations = {}
    platform_data.default_language_platform_translations = {}
    _attach(entity, platform_data)

    assert entity.suggested_object_id == "Pool Temperature"


def test_no_platform_data_does_not_raise(entity):
    """Before the entity is added to a platform the override must not blow up."""
    _attach(entity, None)

    assert entity.suggested_object_id == "Pool Temperature"
