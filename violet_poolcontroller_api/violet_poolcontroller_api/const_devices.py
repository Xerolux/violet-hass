# violet-poolController-api - API f├╝r Violet Pool Controller
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


"""Module defining constants related to device characteristics and states.

Includes detailed parameter configurations for various devices (e.g., pumps,
heaters), state mappings for normalizing device statuses, and visual
configurations like icons and colors. Also provides helper functions and a
`VioletState` class to consistently interpret and manage device states
throughout the integration.
"""

from __future__ import annotations

from enum import IntEnum, StrEnum
from typing import Any, cast

# =============================================================================
# TYPED ENUMERATIONS
# =============================================================================


class OutputState(IntEnum):
    """Output state codes returned by getReadings (manual section 26.1).

    These codes apply to ~30 outputs: pump, heater, solar, light, dosing
    channels, extension relays, etc.  Use the ``is_on``, ``is_manual``, and
    ``is_emergency`` properties instead of comparing raw integers.
    """

    AUTO_OFF = 0
    AUTO_ON = 1
    AUTO_PRIO_OFF = 2
    AUTO_PRIO_ON = 3
    MANUAL_ON = 4
    EMERGENCY_OFF = 5
    MANUAL_OFF = 6

    @property
    def is_on(self) -> bool:
        """Return True when the output is currently active."""
        return self in (OutputState.AUTO_ON, OutputState.AUTO_PRIO_ON, OutputState.MANUAL_ON)

    @property
    def is_manual(self) -> bool:
        """Return True when the output is in manual (non-auto) mode."""
        return self in (OutputState.MANUAL_ON, OutputState.MANUAL_OFF)

    @property
    def is_emergency(self) -> bool:
        """Return True when an emergency rule is responsible for the state."""
        return self in (OutputState.AUTO_PRIO_ON, OutputState.EMERGENCY_OFF)


class DmxSceneState(IntEnum):
    """Output state codes for DMX scenes (subset of OutputState values)."""

    AUTO_OFF = 0
    AUTO_ON = 1
    MANUAL_ON = 4
    MANUAL_OFF = 6

    @property
    def is_on(self) -> bool:
        """Return True when the DMX scene is active."""
        return self in (DmxSceneState.AUTO_ON, DmxSceneState.MANUAL_ON)


class RuleState(IntEnum):
    """State codes for digital-input switching rules (DIRULE_*)."""

    INACTIVE = 0
    ACTIVE = 1
    BLOCKED_BY_RULE = 5
    BLOCKED_MANUALLY = 6


class CoverState(StrEnum):
    """Pool cover motion states returned by the COVER_STATE reading."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    OPENING = "OPENING"
    CLOSING = "CLOSING"
    STOPPED = "STOPPED"


class OnewireState(StrEnum):
    """1-wire temperature sensor status values (OW*_state readings).

    Note: The controller uses ``DATA_MISSMATCH`` (double-s) — preserved here
    for exact string matching against the API response.
    """

    OK = "OK"
    CRC_FAULT = "CRC_FAULT"
    DATA_MISMATCH = "DATA_MISSMATCH"
    NOT_CONNECTED = "NOT_CONNECTED"
    NO_SENSOR_CONFIGURED = "NO_SENSOR_CONFIGURED"


class PvSurplusState(IntEnum):
    """PV surplus trigger source states returned by the PVSURPLUS reading.

    Unlike other outputs, PVSURPLUS uses values 0/1/2 instead of the
    standard 0-6 scheme (manual section 26.3).
    """

    OFF = 0
    ON_BY_INPUT = 1
    ON_BY_HTTP = 2

    @property
    def is_on(self) -> bool:
        """Return True when PV surplus mode is active (regardless of source)."""
        return self in (PvSurplusState.ON_BY_INPUT, PvSurplusState.ON_BY_HTTP)


# =============================================================================
# COVER CONTROL FUNCTIONS
# =============================================================================

COVER_FUNCTIONS: dict[str, str] = {
    "OPEN": "COVER_OPEN",
    "CLOSE": "COVER_CLOSE",
    "STOP": "COVER_STOP",
}

# =============================================================================
# DEVICE PARAMETERS - Extended Configuration
# =============================================================================

DEVICE_PARAMETERS: dict[str, dict[str, Any]] = {
    "PUMP": {
        "supports_speed": True,
        "api_template": "PUMP,{action},{duration},{speed}",
    },
    "HEATER": {
        "supports_timer": True,
        "api_template": "HEATER,{action},{duration},0",
    },
    "SOLAR": {
        "supports_timer": True,
        "api_template": "SOLAR,{action},{duration},0",
    },
    "LIGHT": {
        "supports_color_pulse": True,
        "api_template": "LIGHT,{action},0,0",
    },
    # NOTE: The api_template entries for DOS_* are NOT usable with
    # /setFunctionManually - the controller rejects dosing outputs there
    # (confirmed by PoolDigital). VioletPoolAPI.set_switch_state() routes
    # all DOS_* keys to POST /triggerManualDosing instead; the templates
    # remain only for backwards compatibility of this public constant.
    "DOS_1_CL": {
        "supports_timer": True,
        "dosing_type": "Chlor",
        "api_template": "DOS_1_CL,{action},{duration},0",
    },
    "DOS_4_PHM": {
        "supports_timer": True,
        "dosing_type": "pH-",
        "api_template": "DOS_4_PHM,{action},{duration},0",
    },
    "DOS_5_PHP": {
        "supports_timer": True,
        "dosing_type": "pH+",
        "api_template": "DOS_5_PHP,{action},{duration},0",
    },
    "DOS_2_ELO": {
        "supports_timer": True,
        "dosing_type": "Elektrolyse",
        "api_template": "DOS_2_ELO,{action},{duration},0",
    },
    "DOS_6_FLOC": {
        "supports_timer": True,
        "dosing_type": "Flockmittel",
        "api_template": "DOS_6_FLOC,{action},{duration},0",
    },
    "BACKWASH": {
        "supports_timer": True,
        "api_template": "BACKWASH,{action},{duration},0",
    },
    "BACKWASHRINSE": {
        "supports_timer": True,
        "api_template": "BACKWASHRINSE,{action},{duration},0",
    },
    "PVSURPLUS": {
        "supports_speed": True,
        "api_template": "PVSURPLUS,{action},{speed},0",
    },
    "ECO": {
        "api_template": "ECO,{action},0,0",
    },
    "REFILL": {
        "supports_timer": True,
        "api_template": "REFILL,{action},{duration},0",
    },
}

# Dynamically add extension relays
for ext_bank in [1, 2]:
    for relay_num in range(1, 9):
        key = f"EXT{ext_bank}_{relay_num}"
        DEVICE_PARAMETERS[key] = {
            "supports_timer": True,
            "api_template": f"EXT{ext_bank}_{relay_num},{{action}},{{duration}},0",
        }

# Dynamically add digital input rules (controller exposes SWITCHINGRULE_1..8
# internally; we mirror that with DIRULE_1..8).
for rule_num in range(1, 9):
    key = f"DIRULE_{rule_num}"
    DEVICE_PARAMETERS[key] = {
        "supports_lock": True,
        "api_template": f"DIRULE_{rule_num},{{action}},0,0",
    }

# Dynamically add DMX scenes
for scene_num in range(1, 13):
    key = f"DMX_SCENE{scene_num}"
    DEVICE_PARAMETERS[key] = {
        "api_template": f"DMX_SCENE{scene_num},{{action}},0,0",
    }

# =============================================================================
# STATE MAPPINGS - Critical for 3-State Logic
# =============================================================================

DEVICE_STATE_MAPPING = {
    # String-based states from the API
    "ON": {"mode": "manual", "active": True, "desc": "Manual ON"},
    "OFF": {"mode": "manual", "active": False, "desc": "Manual OFF"},
    "AUTO": {"mode": "auto", "active": None, "desc": "Auto Mode"},
    # Numeric states from the API (source: getReadings spec Rev. 14-07-2024)
    "0": {"mode": "auto", "active": False, "desc": "Auto - Standby"},
    "1": {"mode": "auto", "active": True, "desc": "Auto - Active (Scheduled)"},
    "2": {"mode": "auto", "active": False, "desc": "Auto - Priority OFF (Rule Blocked)"},
    "3": {"mode": "auto", "active": True, "desc": "Auto - Priority ON (Emergency Rule)"},
    "4": {"mode": "manual", "active": True, "desc": "Manual ON (Forced)"},
    "5": {"mode": "auto", "active": False, "desc": "Rule OFF (Emergency Rule)"},
    "6": {"mode": "manual", "active": False, "desc": "Manual OFF"},
    # Special protection modes (from PUMPSTATE field with pipe separator)
    "3|PUMP_ANTI_FREEZE": {
        "mode": "frost_protection",
        "active": True,
        "desc": "Frost Protection Active",
    },
    "PUMP_ANTI_FREEZE": {
        "mode": "frost_protection",
        "active": True,
        "desc": "Frost Protection Active",
    },
    # Generic operational states
    "STOPPED": {"mode": "manual", "active": False, "desc": "Stopped"},
    "ERROR": {"mode": "error", "active": False, "desc": "Error State"},
    "MAINTENANCE": {"mode": "maintenance", "active": False, "desc": "Maintenance"},
}

# Simplified map for quick boolean checks (is the device considered "on"?)
STATE_MAP = {
    # Numeric states (as int and str)
    0: False,
    1: True,
    2: False,
    3: True,
    4: True,
    5: False,
    6: False,
    "0": False,
    "1": True,
    "2": False,
    "3": True,
    "4": True,
    "5": False,
    "6": False,
    # String states
    "ON": True,
    "OFF": False,
    "AUTO": False,
    "MAN": True,
    "MANUAL": True,
    "ACTIVE": True,
    "RUNNING": True,
    "IDLE": False,
}

# State mapping specific to cover entities
COVER_STATE_MAP = {
    "0": "open",
    "1": "opening",
    "2": "closed",
    "3": "closing",
    "4": "stopped",
    "OPEN": "open",
    "OPENING": "opening",
    "CLOSED": "closed",
    "CLOSING": "closing",
    "STOPPED": "stopped",
}

# =============================================================================
# STATE VISUALIZATION
# =============================================================================

STATE_ICONS = {
    "auto_active": "mdi:autorenew",
    "auto_inactive": "mdi:autorenew-off",
    "manual_on": "mdi:power-plug",
    "manual_off": "mdi:power-plug-off",
    "frost_protection": "mdi:snowflake-alert",
    "error": "mdi:alert-circle",
    "maintenance": "mdi:wrench",
}

STATE_COLORS = {
    "auto_active": "#4CAF50",  # Green
    "auto_inactive": "#2196F3",  # Blue
    "manual_on": "#FF9800",  # Orange
    "manual_off": "#F44336",  # Red
    "frost_protection": "#00BCD4",  # Cyan (frost/ice color)
    "error": "#9C27B0",  # Purple
    "maintenance": "#607D8B",  # Blue Grey
}

STATE_TRANSLATIONS = {
    "en": {
        "auto_active": "Auto (Active)",
        "auto_inactive": "Auto (Ready)",
        "manual_on": "Manual On",
        "manual_off": "Manual Off",
        "frost_protection": "Frost Protection",
        "error": "Error",
        "maintenance": "Maintenance",
        "unknown": "Unknown",
    },
    "de": {
        "auto_active": "Automatik (Aktiv)",
        "auto_inactive": "Automatik (Bereit)",
        "manual_on": "Manuell Ein",
        "manual_off": "Manuell Aus",
        "frost_protection": "Frostschutz",
        "error": "Fehler",
        "maintenance": "Wartung",
        "unknown": "Unbekannt",
    },
}

# Default language for human-readable state texts.  Defaults to German for
# backwards compatibility; consumers (e.g. the Home Assistant integration)
# can switch globally via set_state_translation_language() or per instance
# via VioletState(..., language="en").
DEFAULT_STATE_LANGUAGE = "de"
_state_language = DEFAULT_STATE_LANGUAGE


def set_state_translation_language(language: str) -> None:
    """Set the global default language for state display texts.

    Args:
        language: A language code present in STATE_TRANSLATIONS
            (currently ``"de"`` or ``"en"``).

    Raises:
        ValueError: If the language is not available.

    """
    if language not in STATE_TRANSLATIONS:
        msg = f"Unsupported language '{language}'. Available: {sorted(STATE_TRANSLATIONS)}"
        raise ValueError(msg)
    global _state_language  # noqa: PLW0603
    _state_language = language


def get_state_translation_language() -> str:
    """Return the current global default language for state display texts."""
    return _state_language


# =============================================================================
# HELPER FUNCTIONS and STATE CLASS
# =============================================================================


def get_device_state_info(raw_state: Any) -> dict[str, Any]:  # noqa: ANN401
    """Get extended state information for a given raw state.

    Handles plain numeric states ("2"), pipe-separated composite states
    ("2|BLOCKED_BY_OUTSIDE_TEMP"), and empty arrays ("[]").
    """
    state_str = str(raw_state).upper().strip()

    # Direct lookup first (handles exact matches like "3|PUMP_ANTI_FREEZE")
    if state_str in DEVICE_STATE_MAPPING:
        return cast("dict[str, Any]", DEVICE_STATE_MAPPING[state_str])

    # Handle pipe-separated composite states by extracting numeric prefix
    if "|" in state_str:
        prefix = state_str.split("|", 1)[0].strip()
        if prefix in DEVICE_STATE_MAPPING:
            return cast("dict[str, Any]", DEVICE_STATE_MAPPING[prefix])

    # Handle empty arrays (e.g., SOLARSTATE = "[]")
    if state_str in ("[]", "{}", ""):
        return {"mode": "unknown", "active": None, "desc": "No data"}

    return cast(
        "dict[str, Any]",
        {"mode": "unknown", "active": None, "desc": f"Unknown: {raw_state}"},
    )


def get_device_mode_from_state(raw_state: Any) -> str:  # noqa: ANN401
    """Determine the UI display mode from a raw state."""
    state_info = get_device_state_info(raw_state)
    mode, active = state_info["mode"], state_info["active"]

    if mode == "manual":
        return "manual_on" if active else "manual_off"
    if mode == "auto":
        return "auto_active" if active else "auto_inactive"
    return cast("str", mode)


class VioletState:
    """A helper class to interpret and manage complex device states.

    This class provides a structured way to access different aspects of a
    device's state, such as its operational mode, activity status, and
    UI representations (icon, color, translated name).

    Attributes:
        raw_state (str): The original state value from the controller.
        device_key (str | None): The unique key of the device.
        language (str | None): Optional language override for display texts.

    """

    def __init__(
        self,
        raw_state: Any,  # noqa: ANN401
        device_key: str | None = None,
        language: str | None = None,
    ) -> None:
        """Initialize VioletState from a raw controller value.

        Args:
            raw_state: The raw state value from the controller.
            device_key: The unique key of the device.
            language: Optional language code for display texts ("de"/"en").
                Falls back to the global default
                (see set_state_translation_language).

        """
        self.raw_state = str(raw_state).strip()
        self.device_key = device_key
        self.language = language
        self._info = get_device_state_info(self.raw_state)

    @property
    def mode(self) -> str:
        """The primary operational mode (e.g., 'auto', 'manual', 'error')."""
        return cast("str", self._info["mode"])

    @property
    def is_active(self) -> bool | None:
        """Whether the device is currently active (running)."""
        return cast("bool | None", self._info["active"])

    @property
    def description(self) -> str:
        """A human-readable description of the current state."""
        return cast("str", self._info["desc"])

    @property
    def display_mode(self) -> str:
        """The translated name for the current state, suitable for UI display.

        Uses the per-instance language if set, otherwise the global default
        language (German unless changed via set_state_translation_language).
        """
        return self.display_mode_for(self.language or _state_language)

    def display_mode_for(self, language: str) -> str:
        """Return the translated state name for a specific language.

        Args:
            language: A language code present in STATE_TRANSLATIONS.

        Returns:
            The translated state text, falling back to a title-cased
            mode key for unknown languages or modes.

        """
        mode_key = get_device_mode_from_state(self.raw_state)
        return STATE_TRANSLATIONS.get(language, {}).get(
            mode_key,
            mode_key.replace("_", " ").title(),
        )

    @property
    def icon(self) -> str:
        """The appropriate icon for the current state."""
        mode_key = get_device_mode_from_state(self.raw_state)
        return STATE_ICONS.get(mode_key, "mdi:help-circle")

    def __repr__(self) -> str:
        """Return a string representation of the state."""
        return f"VioletState(raw='{self.raw_state}', mode='{self.mode}', active={self.is_active})"
