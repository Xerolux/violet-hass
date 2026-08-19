# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Detection of the dosing channel that owns the ORP/chlorine setpoints.

The controller keeps one set of setpoints per dosing channel: the chlorine
pump stores them as ``DOSAGE_chlorine_*``, the salt electrolysis cell as
``DOSAGE_electrolysis_*``. Both key sets always exist, so reading the chlorine
keys on a pool that dosed via electrolysis reported the unused chlorine
values – a controller configured to 710 mV showed up as the chlorine channel's
untouched 770 mV in Home Assistant.

Which channel is in charge is decided by the enable flags: ``DOSAGE_*_use``
from ``getConfig`` and the matching ``DOS_*_USE`` readings.

Both channels can be enabled at the same time - an electrolysis cell and a
liquid chlorine pump on one pool. The controller then keeps two independent
setpoints, so there is no single channel that "owns" them and picking one
would hide the other. ``active_dosing_channels`` reports every enabled
channel; the number platform gives each one its own entity.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

CHANNEL_CHLORINE = "chlorine"
CHANNEL_ELECTROLYSIS = "electrolysis"

# Keys that flag a channel as enabled, in order of trust: the config value is
# the authoritative one, the reading is the fallback for polls that ran before
# the first getConfig fetch completed.
_CHANNEL_ENABLE_KEYS: dict[str, tuple[str, ...]] = {
    CHANNEL_CHLORINE: ("DOSAGE_chlorine_use", "DOS_1_CL_USE"),
    CHANNEL_ELECTROLYSIS: ("DOSAGE_electrolysis_use", "DOS_2_ELO_USE"),
}


def _is_enabled(data: Mapping[str, Any], keys: tuple[str, ...]) -> bool:
    """Return whether any of the given enable flags is set."""
    for key in keys:
        value = data.get(key)
        if value is None:
            continue
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        text = str(value).strip().lower()
        if text in ("1", "true", "on", "yes"):
            return True
        if text in ("0", "false", "off", "no", ""):
            return False
    return False


def active_dosing_channels(data: Mapping[str, Any] | None) -> tuple[str, ...]:
    """Return every dosing channel the controller has enabled.

    Args:
        data: The merged coordinator data (readings plus config values);
            a ``VioletReadings`` view or a plain mapping.

    Returns:
        The enabled channels in a stable order. A pool running an electrolysis
        cell alongside a chlorine pump reports both - each keeps its own
        setpoint. Falls back to the chlorine channel when nothing is flagged,
        which is what the integration used before the flags were read at all.
    """
    if not data:
        return (CHANNEL_CHLORINE,)

    channels = tuple(
        channel
        for channel in (CHANNEL_CHLORINE, CHANNEL_ELECTROLYSIS)
        if _is_enabled(data, _CHANNEL_ENABLE_KEYS[channel])
    )
    return channels or (CHANNEL_CHLORINE,)


def active_dosing_channel(data: Mapping[str, Any] | None) -> str:
    """Return the dosing channel that owns the ORP/chlorine setpoints.

    Args:
        data: The merged coordinator data (readings plus config values);
            a ``VioletReadings`` view or a plain mapping.

    Returns:
        ``"electrolysis"`` for a pool dosing via electrolysis only, otherwise
        ``"chlorine"``. With both channels enabled the chlorine channel is the
        primary one; the electrolysis setpoint gets its own entity rather than
        replacing this one.
    """
    channels = active_dosing_channels(data)
    if channels == (CHANNEL_ELECTROLYSIS,):
        return CHANNEL_ELECTROLYSIS
    return CHANNEL_CHLORINE
