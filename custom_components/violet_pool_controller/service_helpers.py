"""Helpers and constants for Violet service handling."""

from __future__ import annotations

import os
from collections.abc import Iterable
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol


def as_device_id_list(value: Any) -> list[str]:
    """Normalize raw device id input into a list of strings."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
        return [str(item) for item in value]
    return [str(value)]


DEVICE_ID_SELECTOR = vol.All(as_device_id_list, [cv.string])

DOSING_TYPE_MAPPING = {
    "pH-": "DOS_4_PHM",
    "pH+": "DOS_5_PHP",
    "Chlor": "DOS_1_CL",
    "Flockmittel": "DOS_6_FLOC",
}

MIN_DOSING_DURATION = 5
MAX_DOSING_DURATION = 300
MIN_PUMP_SPEED = 1
MAX_PUMP_SPEED = 3
MIN_TEMPERATURE = 20.0
MAX_TEMPERATURE = 40.0
MIN_PH = 6.8
MAX_PH = 7.8
DEFAULT_SAFETY_INTERVAL = 300


def read_recent_violet_log_lines(
    log_path: str,
    lines: int,
    include_timestamps: bool,
) -> list[str]:
    """Read the most recent Violet-related log lines from disk."""
    if not os.path.exists(log_path):
        return []

    with open(log_path, "r", encoding="utf-8", errors="ignore") as log_file:
        all_lines = log_file.readlines()

    violet_lines = [
        line for line in all_lines if "violet_pool_controller" in line.lower()
    ]
    recent_lines = violet_lines[-lines:] if len(violet_lines) > lines else violet_lines

    if include_timestamps:
        return [line.rstrip() for line in recent_lines]

    import re

    return [
        re.sub(r"^\[?\d{4}-\d{2}-\d{2}[^]]*\]?\s*", "", line).rstrip()
        for line in recent_lines
    ]


def write_text_file(filepath: str, content: str) -> None:
    """Write text content to disk."""
    with open(filepath, "w", encoding="utf-8") as output_file:
        output_file.write(content)
