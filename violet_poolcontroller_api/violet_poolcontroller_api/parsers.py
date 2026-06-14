# violet-poolController-api - API für Violet Pool Controller
# Copyright (C) 2024-2026  Xerolux
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Parser utilities for Violet Pool Controller timestamp and duration formats.

The controller returns timestamps and durations in several distinct text
formats.  This module centralises the conversion logic so that higher-level
consumers (Home Assistant integration, standalone scripts) can work with
standard Python ``datetime`` and ``timedelta`` objects instead of raw strings.

Supported formats
-----------------
* ``"04h 33m 12s"`` / ``"1d 04h 33m 12s"`` – runtime strings
* ``"HH:MM:SS"`` – legacy colon-separated duration
* ``"250d 11h 48m"`` – CPU uptime strings
* Unix epoch seconds (int / float / str)
* Unix epoch milliseconds (int / float / str)
* Float seconds with ``"NONE"`` sentinel
"""

from __future__ import annotations

import math
import re
from datetime import UTC, datetime, timedelta

# ---------------------------------------------------------------------------
# Pre-compiled patterns
# ---------------------------------------------------------------------------

# Matches optional days, hours, minutes, seconds with single-letter labels.
# Examples: "04h 33m 12s", "1d 04h 33m 12s", "2h", "45m 30s"
_RE_RUNTIME = re.compile(
    r"(?:(\d+)\s*d)?\s*(?:(\d+)\s*h)?\s*(?:(\d+)\s*m)?\s*(?:(\d+)\s*s)?",
    re.IGNORECASE,
)

# Matches "HH:MM:SS" exactly.
_RE_HMS = re.compile(r"^(\d+):(\d+):(\d+)$")

# Matches optional days and hours (no seconds) – typical CPU uptime format.
# Example: "250d 11h 48m"
_RE_UPTIME = re.compile(
    r"(?:(\d+)\s*d)?\s*(?:(\d+)\s*h)?\s*(?:(\d+)\s*m)?",
    re.IGNORECASE,
)


def parse_runtime_string(value: str) -> timedelta:
    """Parse a runtime string like ``"04h 33m 12s"`` into a ``timedelta``.

    Days are supported: ``"1d 04h 33m 12s"`` → ``timedelta(days=1, hours=4, …)``.
    All components are optional; an empty or non-matching string returns
    ``timedelta(0)``.

    Args:
        value: Raw runtime string from the controller.

    Returns:
        ``timedelta`` representing the duration.
    """
    m = _RE_RUNTIME.search(value.strip())
    if not m:
        return timedelta(0)
    days, hours, minutes, seconds = (int(g) if g else 0 for g in m.groups())
    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def parse_hms_string(value: str) -> timedelta:
    """Parse a legacy ``"HH:MM:SS"`` duration string into a ``timedelta``.

    Args:
        value: Duration string in colon-separated format.

    Returns:
        ``timedelta`` representing the duration, or ``timedelta(0)`` if the
        string does not match the expected format.
    """
    m = _RE_HMS.match(value.strip())
    if not m:
        return timedelta(0)
    hours, minutes, seconds = (int(g) for g in m.groups())
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def parse_uptime_string(value: str) -> timedelta:
    """Parse a CPU uptime string like ``"250d 11h 48m"`` into a ``timedelta``.

    Unlike :func:`parse_runtime_string`, seconds are not expected in this
    format.  An empty or non-matching string returns ``timedelta(0)``.

    Args:
        value: Raw uptime string from the controller.

    Returns:
        ``timedelta`` representing the uptime duration.
    """
    m = _RE_UPTIME.search(value.strip())
    if not m:
        return timedelta(0)
    days, hours, minutes = (int(g) if g else 0 for g in m.groups())
    return timedelta(days=days, hours=hours, minutes=minutes)


def parse_epoch_seconds(value: int | float | str) -> datetime | None:
    """Convert Unix epoch seconds to a UTC-aware ``datetime``.

    A value of ``0`` (or ``"0"``) is treated as *no timestamp available* and
    returns ``None``, because the controller uses zero as a sentinel for
    unset timestamps.

    Args:
        value: Unix timestamp in seconds (int, float, or numeric string).

    Returns:
        UTC-aware ``datetime``, or ``None`` when ``value`` is zero or
        non-numeric.
    """
    try:
        ts = float(value)
    except (ValueError, TypeError):
        return None
    if not math.isfinite(ts) or ts == 0:
        return None
    return datetime.fromtimestamp(ts, tz=UTC)


def parse_epoch_milliseconds(value: int | float | str) -> datetime | None:
    """Convert Unix epoch milliseconds to a UTC-aware ``datetime``.

    A value of ``0`` (or ``"0"``) is treated as *no timestamp available* and
    returns ``None``.

    Args:
        value: Unix timestamp in milliseconds (int, float, or numeric string).

    Returns:
        UTC-aware ``datetime``, or ``None`` when ``value`` is zero or
        non-numeric.
    """
    try:
        ts_ms = float(value)
    except (ValueError, TypeError):
        return None
    if not math.isfinite(ts_ms) or ts_ms == 0:
        return None
    return datetime.fromtimestamp(ts_ms / 1000.0, tz=UTC)


def parse_optional_seconds(value: str | float | int) -> timedelta | None:
    """Parse float seconds with a ``"NONE"`` sentinel.

    The controller uses the string ``"NONE"`` in some fields to indicate that
    a duration is not applicable.  This function converts numeric values to
    ``timedelta`` and the sentinel to ``None``.

    Args:
        value: Either a numeric seconds value or the string ``"NONE"``
            (case-insensitive).

    Returns:
        ``timedelta`` for numeric values, or ``None`` for the sentinel.
    """
    if isinstance(value, str) and value.strip().upper() == "NONE":
        return None
    try:
        seconds = float(value)
    except (ValueError, TypeError):
        return None
    if not math.isfinite(seconds):
        return None
    return timedelta(seconds=seconds)
