"""Tests for entity name normalization."""

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
