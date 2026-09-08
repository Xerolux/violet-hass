"""Helpers and constants for Violet service handling."""

from __future__ import annotations

import os
from collections.abc import Iterable
from typing import Any, TextIO

import homeassistant.helpers.config_validation as cv
import voluptuous as vol


def as_device_id_list(value: Any) -> list[str]:
    """Normalize raw device id input into a list of strings."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
        return [str(item) for item in value]
    if isinstance(value, (bytes, bytearray)):
        return [value.decode("utf-8")]
    return [str(value)]


DEVICE_ID_SELECTOR = vol.All(as_device_id_list, [cv.string])

# ---------------------------------------------------------------------------
# Dosing lookup tables
# ---------------------------------------------------------------------------
# H2O2 is deliberately absent from every table below: the installed API
# package has no H2O2 dosing function, so ``manual_dosing("H2O2", ...)``
# raised "Unknown dosing type" and ``action="stop"`` silently stopped the
# CHLORINE channel instead.  Re-add it only once the API supports it.

# smart_dosing ``dosing_type`` -> physical controller switch key.
DOSING_TYPE_MAPPING = {
    "pH-": "DOS_4_PHM",
    "pH+": "DOS_5_PHP",
    "Chlorine": "DOS_1_CL",
    "Electrolysis": "DOS_2_ELO",
    "Flocculant": "DOS_6_FLOC",
}

# smart_dosing ``dosing_type`` -> the name ``VioletPoolAPI.manual_dosing``
# expects (the API's DOSING_FUNCTIONS keys).
DOSING_API_MAPPING = {
    "pH-": "pH-",
    "pH+": "pH+",
    "Chlorine": "Chlor",
    "Electrolysis": "Elektrolyse",
    "Flocculant": "Flockmittel",
}

# The ``dosing_system`` slug used by the *_http and dosing-configuration
# services.  Shared by the schemas and the handlers so the two cannot drift.
DOSING_SYSTEM_SLUGS = (
    "chlorine",
    "electrolysis",
    "ph_minus",
    "ph_plus",
    "flocculant",
    "h2o2",
)

DOSING_INDEX_MAP = {
    "chlorine": 0,  # DOS_1_CL
    "electrolysis": 1,  # DOS_2_ELO
    "ph_minus": 3,  # DOS_4_PHM (index 2 is unused in firmware)
    "ph_plus": 4,  # DOS_5_PHP
    "flocculant": 5,  # DOS_6_FLOC
    "h2o2": 0,  # shares DOS_1_CL physical output, from_param=3 distinguishes it
}

DOSING_FROM_PARAM_MAP = {
    "h2o2": 3,  # H2O2 uses from=3; all others default to from=1
}

# Dosing-system slug -> config key prefix on the controller.
DOSING_SYSTEMS = {
    "chlorine": "DOSAGE_chlorine",
    "electrolysis": "DOSAGE_electrolysis",
    "ph_minus": "DOSAGE_phminus",
    "ph_plus": "DOSAGE_phplus",
    "flocculant": "DOSAGE_floc",
    "h2o2": "DOSAGE_h2o2",
}

# Dosing-system slug -> physical controller switch key, used to key the
# SafetyGuard cooldown for the *_http dosing services.
DOSING_SYSTEM_TO_KEY = {
    "chlorine": "DOS_1_CL",
    "electrolysis": "DOS_2_ELO",
    "ph_minus": "DOS_4_PHM",
    "ph_plus": "DOS_5_PHP",
    "flocculant": "DOS_6_FLOC",
    "h2o2": "DOS_1_CL",
}

MIN_DOSING_DURATION = 5
MAX_DOSING_DURATION = 300
MIN_PUMP_SPEED = 1
MAX_PUMP_SPEED = 3
DEFAULT_SAFETY_INTERVAL = 300


def _tail_file(file_handle: TextIO, line_count: int) -> list[str]:
    """Read only the tail of a file without loading the entire file."""
    file_handle.seek(0, os.SEEK_END)
    file_size = file_handle.tell()
    buffer_size = min(file_size, max(8192, line_count * 200))
    file_handle.seek(max(0, file_size - buffer_size))
    lines = file_handle.readlines()
    if file_size > buffer_size:
        lines = lines[-line_count:]
    return lines


def read_recent_violet_log_lines(
    log_path: str,
    lines: int,
    include_timestamps: bool,
) -> list[str]:
    """Read the most recent Violet-related log lines from disk."""
    if not os.path.exists(log_path):
        return []

    with open(log_path, encoding="utf-8", errors="ignore") as log_file:
        tail_lines = _tail_file(log_file, lines * 10)

    violet_lines = [line for line in tail_lines if "violet_pool_controller" in line.lower()]
    recent_lines = violet_lines[-lines:] if len(violet_lines) > lines else violet_lines

    if include_timestamps:
        return [line.rstrip() for line in recent_lines]

    import re

    return [re.sub(r"^\[?\d{4}-\d{2}-\d{2}[^]]*\]?\s*", "", line).rstrip() for line in recent_lines]


def write_text_file(filepath: str, content: str) -> None:
    """Write text content to disk."""
    with open(filepath, "w", encoding="utf-8") as output_file:
        output_file.write(content)
