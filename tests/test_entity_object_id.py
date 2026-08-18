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
from homeassistant.helpers.typing import UNDEFINED

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from custom_components.violet_pool_controller.entity import (  # noqa: E402
    VioletPoolControllerEntity,
    strip_redundant_device_prefix,
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


def _make_entity(description: SensorEntityDescription) -> VioletPoolControllerEntity:
    """Build a base entity around the given description."""
    coordinator = MagicMock()
    coordinator.device.device_name = "Violet Pool Controller"
    coordinator.device.controller_name = "Violet Pool Controller"
    coordinator.device.device_info = {}

    config_entry = MagicMock(spec=ConfigEntry)
    config_entry.entry_id = "test_entry"

    return VioletPoolControllerEntity(coordinator, config_entry, description)


@pytest.fixture
def entity() -> VioletPoolControllerEntity:
    """Create a base entity with a translated sensor description."""
    return _make_entity(
        SensorEntityDescription(
            key="onewire1_value",
            name="Pool Temperature",
            translation_key="pool_temperature",
        )
    )


@pytest.fixture
def unnamed_entity() -> VioletPoolControllerEntity:
    """Create a base entity whose description carries no name at all.

    ``EntityDescription.name`` defaults to ``UNDEFINED``, so this is what any
    description that simply omits ``name=`` looks like.
    """
    return _make_entity(
        SensorEntityDescription(
            key="onewire1_value",
            translation_key="pool_temperature",
        )
    )


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


def test_nameless_entity_suggests_no_object_id(unnamed_entity):
    """Without any name Home Assistant must fall back to naming by device."""
    platform_data = _platform_data("Wassertemperatur")
    platform_data.platform_translations = {}
    platform_data.object_id_platform_translations = {}
    platform_data.default_language_platform_translations = {}
    _attach(unnamed_entity, platform_data)

    # UNDEFINED means "no name of its own"; returning it verbatim would produce
    # an entity_id like sensor.violet_pool_controller_undefinedtype_singleton.
    assert unnamed_entity.suggested_object_id is None


@pytest.mark.parametrize(
    "value",
    [None, UNDEFINED],
    ids=["none", "undefined"],
)
def test_name_sanitizer_passes_through_sentinels(value):
    """``None`` and ``UNDEFINED`` must survive the prefix stripping untouched.

    ``UNDEFINED`` is the default of ``EntityDescription.name``. Stringifying it
    would name the entity "UndefinedType._singleton".
    """
    assert strip_redundant_device_prefix(value, "Violet Pool Controller") is value


def test_name_sanitizer_still_strips_the_device_prefix():
    """The regular case keeps working."""
    assert (
        strip_redundant_device_prefix(
            "Violet Pool Controller Beleuchtung", "Violet Pool Controller"
        )
        == "Beleuchtung"
    )


def test_entity_id_is_pinned_to_the_controller(entity):
    """Grouping must not change entity ids.

    Home Assistant composes entity ids from the device an entity belongs to, so
    moving entities onto sub-devices would rename them to
    ``sensor.filter_pump_pool_temperature``. The base entity pins the id to the
    controller name instead, so shared dashboards keep working.
    """
    _attach(entity, _platform_data("Wassertemperatur"))
    platform = MagicMock()
    platform.domain = "sensor"

    assert entity._pinned_entity_id(platform) == (
        "sensor.violet_pool_controller_pool_temperature"
    )


def test_pinned_entity_id_is_language_independent(entity):
    """The pinned id uses the English name, like suggested_object_id does."""
    platform = MagicMock()
    platform.domain = "sensor"

    _attach(entity, _platform_data("Wassertemperatur"))
    german_install = entity._pinned_entity_id(platform)
    _attach(entity, _platform_data("Pool Temperature"))
    english_install = entity._pinned_entity_id(platform)

    assert german_install == english_install


def test_nameless_entity_is_not_pinned(unnamed_entity):
    """Without a name there is nothing to pin; let Home Assistant decide."""
    platform = MagicMock()
    platform.domain = "sensor"
    _attach(unnamed_entity, None)

    assert unnamed_entity._pinned_entity_id(platform) is None


# ---------------------------------------------------------------------------
# Renaming ids that spell out a label we corrected
# ---------------------------------------------------------------------------

_ELO_KEY = "DOS_2_ELO_TOTAL_CAN_AMOUNT_ML"
_ELO_TRANSLATION = "component.violet_pool_controller.entity.sensor.dos_2_elo_total_can.name"
_OLD_ID = "sensor.violet_pool_controller_elektrolyse_kanisterinhalt_ml"
_NEW_ID = "sensor.violet_pool_controller_electrolysis_cell_remaining_runtime"


def _elo_platform_data() -> MagicMock:
    """Platform data for the electrolysis cell sensor, German UI, English ids."""
    platform_data = MagicMock()
    platform_data.domain = "sensor"
    platform_data.platform_name = "violet_pool_controller"
    names = {_ELO_TRANSLATION: "Elektrolysezelle Restlaufzeit"}
    platform_data.platform_translations = names
    platform_data.object_id_platform_translations = names
    platform_data.default_language_platform_translations = {
        _ELO_TRANSLATION: "Electrolysis Cell Remaining Runtime"
    }
    platform_data.component_translations = {}
    platform_data.object_id_component_translations = {}
    return platform_data


def _elo_entity() -> VioletPoolControllerEntity:
    """The sensor whose old id claims to be a canister level in millilitres."""
    entity = _make_entity(
        SensorEntityDescription(
            key=_ELO_KEY,
            name="Elektrolysezelle Restlaufzeit",
            translation_key="dos_2_elo_total_can",
        )
    )
    _attach(entity, _elo_platform_data())
    return entity


def _register(hass, entity: VioletPoolControllerEntity, object_id: str):
    """Put the entity in the registry under an id an older release produced."""
    from homeassistant.helpers import entity_registry as er

    registry = er.async_get(hass)
    registry.async_get_or_create(
        "sensor",
        "violet_pool_controller",
        entity._attr_unique_id,
        suggested_object_id=object_id,
    )
    return registry


async def test_old_id_naming_a_canister_is_renamed(hass) -> None:
    """The reported case: a runtime in hours sitting at "kanisterinhalt_ml"."""
    entity = _elo_entity()
    registry = _register(hass, entity, "violet_pool_controller_elektrolyse_kanisterinhalt_ml")
    assert registry.async_get(_OLD_ID) is not None

    entity._rename_relabelled_entity(hass, entity.platform_data)

    assert registry.async_get(_OLD_ID) is None
    assert registry.async_get(_NEW_ID) is not None


async def test_renaming_is_idempotent(hass) -> None:
    """A second start must not rename again, or the id would keep moving."""
    entity = _elo_entity()
    registry = _register(hass, entity, "violet_pool_controller_elektrolyse_kanisterinhalt_ml")

    entity._rename_relabelled_entity(hass, entity.platform_data)
    entity._rename_relabelled_entity(hass, entity.platform_data)

    assert registry.async_get(_NEW_ID) is not None
    assert len(list(registry.entities)) == 1


async def test_an_id_the_user_chose_is_left_alone(hass) -> None:
    """Only ids that still spell out the wrong label are touched."""
    entity = _elo_entity()
    registry = _register(hass, entity, "pool_zelle_restlaufzeit")

    entity._rename_relabelled_entity(hass, entity.platform_data)

    assert registry.async_get("sensor.pool_zelle_restlaufzeit") is not None
    assert registry.async_get(_NEW_ID) is None


async def test_an_occupied_target_id_is_not_stolen(hass) -> None:
    """Renaming onto an existing entity would break two entities, not one."""
    entity = _elo_entity()
    registry = _register(hass, entity, "violet_pool_controller_elektrolyse_kanisterinhalt_ml")
    registry.async_get_or_create(
        "sensor",
        "violet_pool_controller",
        "someone_elses_unique_id",
        suggested_object_id="violet_pool_controller_electrolysis_cell_remaining_runtime",
    )

    entity._rename_relabelled_entity(hass, entity.platform_data)

    assert registry.async_get(_OLD_ID) is not None


async def test_entities_outside_the_table_are_never_renamed(hass) -> None:
    """Everything a dashboard references keeps its id."""
    entity = _make_entity(
        SensorEntityDescription(
            key="onewire1_value",
            name="Pool Temperature",
            translation_key="pool_temperature",
        )
    )
    _attach(entity, _platform_data("Wassertemperatur"))
    registry = _register(hass, entity, "violet_pool_controller_wassertemperatur")

    entity._rename_relabelled_entity(hass, entity.platform_data)

    assert registry.async_get("sensor.violet_pool_controller_wassertemperatur") is not None


async def test_an_unregistered_entity_is_left_to_home_assistant(hass) -> None:
    """A first run has nothing to rename; the id is built from the fixed name."""
    from homeassistant.helpers import entity_registry as er

    entity = _elo_entity()
    registry = er.async_get(hass)

    entity._rename_relabelled_entity(hass, entity.platform_data)

    assert not list(registry.entities)
