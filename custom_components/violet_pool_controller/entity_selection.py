# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""The datapoint selection, applied to every platform.

Until 2.4.1 the selection made in the config flow was read by the sensor
platform alone. The step lists the raw controller keys (``ECO``,
``DMX_SCENE1``, ``PUMP``, …) exactly as the controller reports them, so it
reads as "pick the datapoints you want in Home Assistant" - but deselecting
``ECO`` removed the ECO *sensor* while its switch, binary sensor and select
stayed. This module makes the selection mean what it looks like.

Two rules keep the behaviour predictable:

* **No stored selection means everything.** A config entry that never went
  through the selection step must not lose entities.
* **Only entities that carry a controller key are affected.** Synthetic
  entities - system health, connection latency, the firmware update, the
  saturation-index calculators - have no key in ``getReadings`` and can never
  appear in the list, so the selection cannot be applied to them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.core import callback

from .const import CONF_SELECTED_SENSORS

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry


@dataclass(frozen=True, slots=True)
class DatapointSelection:
    """Which controller keys the user wants to see as entities."""

    keys: frozenset[str] | None

    @property
    def selects_everything(self) -> bool:
        """Return True when no selection was ever stored."""
        return self.keys is None

    def allows(self, key: str | None) -> bool:
        """Return whether an entity built from ``key`` may be created.

        A missing key means the entity is synthetic and always allowed.
        """
        if self.keys is None or key is None:
            return True
        return key in self.keys


@callback
def async_get_selection(entry: ConfigEntry) -> DatapointSelection:
    """Read the stored datapoint selection from a config entry."""
    selected = entry.options.get(CONF_SELECTED_SENSORS, entry.data.get(CONF_SELECTED_SENSORS))
    if selected is None:
        return DatapointSelection(keys=None)
    return DatapointSelection(keys=frozenset(str(key) for key in selected))
