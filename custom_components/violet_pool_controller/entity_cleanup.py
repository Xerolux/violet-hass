# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Registry cleanup for entities the integration no longer provides.

Home Assistant keeps an entity registry entry alive even when the integration
stops creating the matching entity.  Without an explicit cleanup, disabling a
feature (or deselecting a sensor) in the options flow leaves the old entities
behind as permanently unavailable "restored" entries — the integration looks
like the selection had no effect at all.

To avoid guessing which entities *should* exist, every platform reports the
unique ids it actually provided during setup via :func:`track_provided_entities`.
Once all platforms have reported, :func:`async_remove_orphaned_entities` drops
every registry entry of the config entry that is not part of that set.

Reporting the provided ids (instead of only looking at the live entity objects)
is important: entities that are disabled in the registry — either by the user or
by ``entity_registry_enabled_default = False`` — never reach the entity platform,
yet they must survive the cleanup.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN

if TYPE_CHECKING:
    from collections.abc import Iterable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.const import Platform
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

_STORE_SUFFIX = "_provided_unique_ids"


def _store_key(entry: ConfigEntry) -> str:
    """Return the ``hass.data`` key holding the reported unique ids."""
    return f"{entry.entry_id}{_STORE_SUFFIX}"


@callback
def track_provided_entities(
    hass: HomeAssistant,
    entry: ConfigEntry,
    platform: Platform | str,
    entities: Iterable[Entity],
) -> None:
    """Record which unique ids a platform provided for this config entry.

    Must be called by every platform exactly once per setup — including the
    early-return paths where the platform provides nothing, because the cleanup
    only runs once all platforms have reported.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry being set up.
        platform: The platform domain reporting its entities.
        entities: The entities handed to ``async_add_entities`` (may be empty).
    """
    store: dict[str, set[str]] = hass.data.setdefault(DOMAIN, {}).setdefault(_store_key(entry), {})
    store[str(platform)] = {
        unique_id for entity in entities if (unique_id := entity.unique_id) is not None
    }


@callback
def async_remove_orphaned_entities(
    hass: HomeAssistant,
    entry: ConfigEntry,
    platforms: Iterable[Platform | str],
) -> int:
    """Remove registry entries the integration no longer provides.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry to clean up.
        platforms: All platforms that are expected to have reported.

    Returns:
        The number of removed registry entries.
    """
    store: dict[str, set[str]] = hass.data.get(DOMAIN, {}).get(_store_key(entry), {})

    missing = [str(platform) for platform in platforms if str(platform) not in store]
    if missing:
        # A platform failed or was skipped — removing entities now could delete
        # perfectly valid entries, so leave the registry untouched.
        _LOGGER.debug(
            "Skipping entity cleanup for entry_id=%s: no report from %s",
            entry.entry_id,
            ", ".join(sorted(missing)),
        )
        return 0

    provided: set[str] = set().union(*store.values()) if store else set()
    if not provided:
        _LOGGER.debug(
            "Skipping entity cleanup for entry_id=%s: no entities were provided",
            entry.entry_id,
        )
        return 0

    entity_registry = er.async_get(hass)
    removed = 0

    for registry_entry in er.async_entries_for_config_entry(entity_registry, entry.entry_id):
        if registry_entry.unique_id in provided:
            continue

        _LOGGER.debug(
            "Removing entity %s (unique_id=%s): no longer provided by the integration",
            registry_entry.entity_id,
            registry_entry.unique_id,
        )
        entity_registry.async_remove(registry_entry.entity_id)
        removed += 1

    if removed:
        _LOGGER.info(
            "Removed %d entity/entities that are no longer provided for entry_id=%s "
            "(disabled feature, deselected sensor or removed hardware)",
            removed,
            entry.entry_id,
        )

    return removed


@callback
def discard_provided_entities(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Drop the reported unique ids of a config entry (called on unload)."""
    hass.data.get(DOMAIN, {}).pop(_store_key(entry), None)
