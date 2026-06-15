"""Tests for entity name normalization and entity_id migration."""

from unittest.mock import MagicMock

from custom_components.violet_pool_controller import (
    _migrate_duplicate_prefix_entity_ids,
)
from custom_components.violet_pool_controller.entity import strip_redundant_device_prefix


def test_strip_redundant_device_prefix_from_german_light_name() -> None:
    """Avoid entity ids like switch.violet_pool_controller_violet_pool_controller_beleuchtung."""
    assert (
        strip_redundant_device_prefix(
            "Violet Pool Controller Beleuchtung",
            "Violet Pool Controller",
        )
        == "Beleuchtung"
    )


def test_strip_redundant_device_prefix_repeated_slug_prefix() -> None:
    """Strip repeated slug-style prefixes from imported/controller names."""
    assert (
        strip_redundant_device_prefix(
            "violet_pool_controller_violet_pool_controller_beleuchtung",
            "Violet Pool Controller",
        )
        == "beleuchtung"
    )


def test_strip_redundant_device_prefix_keeps_plain_entity_name() -> None:
    """Do not alter already clean entity-specific names."""
    assert strip_redundant_device_prefix("Beleuchtung", "Violet Pool Controller") == "Beleuchtung"


def test_strip_redundant_device_prefix_none_input() -> None:
    """Return None when input is None."""
    assert strip_redundant_device_prefix(None, "Violet Pool Controller") is None


def test_strip_redundant_device_prefix_only_prefix() -> None:
    """Do not strip when the name IS the device prefix (no entity suffix)."""
    assert (
        strip_redundant_device_prefix("Violet Pool Controller", "Violet Pool Controller")
        == "Violet Pool Controller"
    )


def test_strip_redundant_device_prefix_english_pump_name() -> None:
    """Strip English hardware-config names that include the device prefix."""
    assert (
        strip_redundant_device_prefix(
            "Violet Pool Controller Filter Pump",
            "Violet Pool Controller",
        )
        == "Filter Pump"
    )


def _make_entity_entry(entity_id: str, config_entry_id: str = "entry1") -> MagicMock:
    entry = MagicMock()
    entry.entity_id = entity_id
    entry.config_entry_id = config_entry_id
    return entry


def _make_registry(entities: list[MagicMock]) -> MagicMock:
    registry = MagicMock()
    registry.async_get.return_value = None  # target id not taken
    return registry


def _run_migration(entities: list[MagicMock], target_taken: bool = False) -> MagicMock:
    """Run migration with given entity entries; return the mocked registry."""
    import custom_components.violet_pool_controller as pkg

    registry = MagicMock()
    registry.async_get.return_value = MagicMock() if target_taken else None

    original = pkg.er.async_entries_for_config_entry
    pkg.er.async_entries_for_config_entry = lambda _reg, _id: entities
    try:
        _migrate_duplicate_prefix_entity_ids(registry, "entry1")
    finally:
        pkg.er.async_entries_for_config_entry = original

    return registry


def test_migrate_duplicate_prefix_renames_entity() -> None:
    """Migration renames entity_ids with a doubled domain slug."""
    old_id = "switch.violet_pool_controller_violet_pool_controller_beleuchtung"
    entity = _make_entity_entry(old_id)

    registry = _run_migration([entity])

    registry.async_update_entity.assert_called_once_with(
        old_id,
        new_entity_id="switch.violet_pool_controller_beleuchtung",
    )


def test_migrate_duplicate_prefix_skips_clean_entity() -> None:
    """Migration leaves entity_ids that don't have a duplicate prefix alone."""
    entity = _make_entity_entry("switch.violet_pool_controller_beleuchtung")

    registry = _run_migration([entity])

    registry.async_update_entity.assert_not_called()


def test_migrate_duplicate_prefix_skips_when_target_taken() -> None:
    """Migration skips rename when the target entity_id is already in use."""
    old_id = "switch.violet_pool_controller_violet_pool_controller_pump"
    entity = _make_entity_entry(old_id)

    registry = _run_migration([entity], target_taken=True)

    registry.async_update_entity.assert_not_called()


def test_migrate_duplicate_prefix_collapses_triple_slug() -> None:
    """Migration collapses three or more consecutive domain slugs to one."""
    old_id = (
        "switch.violet_pool_controller_"
        "violet_pool_controller_violet_pool_controller_beleuchtung"
    )
    entity = _make_entity_entry(old_id)

    registry = _run_migration([entity])

    registry.async_update_entity.assert_called_once_with(
        old_id,
        new_entity_id="switch.violet_pool_controller_beleuchtung",
    )
