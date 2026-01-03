"""This module defines constants related to device characteristics and states.

It includes detailed parameter configurations for various devices (e.g., pumps, heaters),
state mappings for normalizing device statuses, and visual configurations like icons
and colors. The module also provides helper functions and a `VioletState` class to
consistently interpret and manage device states throughout the integration.
"""

from typing import Any, Dict, Optional, cast

# =============================================================================
# DEVICE PARAMETERS - Extended Configuration
# =============================================================================

DEVICE_PARAMETERS = {
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
}

# Dynamically add extension relays
for ext_bank in [1, 2]:
    for relay_num in range(1, 9):
        key = f"EXT{ext_bank}_{relay_num}"
        DEVICE_PARAMETERS[key] = {
            "supports_timer": True,
            "api_template": f"EXT{ext_bank}_{relay_num},{{action}},{{duration}},0",
        }

# Dynamically add digital input rules
for rule_num in range(1, 8):
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
    # Numeric states from the API
    "0": {"mode": "auto", "active": False, "desc": "Auto - Standby"},
    "1": {"mode": "manual", "active": True, "desc": "Manual ON"},
    "2": {"mode": "auto", "active": True, "desc": "Auto - Active"},
    "3": {"mode": "auto", "active": True, "desc": "Auto - Active (Timer)"},
    "4": {"mode": "manual", "active": True, "desc": "Manual ON (Forced)"},
    "5": {"mode": "auto", "active": False, "desc": "Auto - Waiting"},
    "6": {"mode": "manual", "active": False, "desc": "Manual OFF"},
    # Special protection modes (from PUMPSTATE field with pipe separator)
    "3|PUMP_ANTI_FREEZE": {"mode": "frost_protection", "active": True, "desc": "Frost Protection Active"},
    "PUMP_ANTI_FREEZE": {"mode": "frost_protection", "active": True, "desc": "Frost Protection Active"},
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
    2: True,
    3: True,
    4: True,
    5: False,
    6: False,
    "0": False,
    "1": True,
    "2": True,
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

# =============================================================================
# HELPER FUNCTIONS and STATE CLASS
# =============================================================================


def get_device_state_info(raw_state: Any) -> Dict[str, Any]:
    """Get extended state information for a given raw state."""
    state_str = str(raw_state).upper().strip()
    return cast(
        Dict[str, Any],
        DEVICE_STATE_MAPPING.get(
            state_str,
            {"mode": "unknown", "active": None, "desc": f"Unknown: {raw_state}"},
        ),
    )


def get_device_mode_from_state(raw_state: Any) -> str:
    """Determine the UI display mode from a raw state."""
    state_info = get_device_state_info(raw_state)
    mode, active = state_info["mode"], state_info["active"]

    if mode == "manual":
        return "manual_on" if active else "manual_off"
    if mode == "auto":
        return "auto_active" if active else "auto_inactive"
    return mode


class VioletState:
    """A helper class to interpret and manage complex device states.

    This class provides a structured way to access different aspects of a
    device's state, such as its operational mode, activity status, and
    UI representations (icon, color, translated name).

    Attributes:
        raw_state (str): The original state value from the controller.
        device_key (Optional[str]): The unique key of the device.
    """

    def __init__(self, raw_state: Any, device_key: Optional[str] = None):
        self.raw_state = str(raw_state).strip()
        self.device_key = device_key
        self._info = get_device_state_info(self.raw_state)

    @property
    def mode(self) -> str:
        """The primary operational mode (e.g., 'auto', 'manual', 'error')."""
        return self._info["mode"]

    @property
    def is_active(self) -> Optional[bool]:
        """Whether the device is currently active (running)."""
        return self._info["active"]

    @property
    def description(self) -> str:
        """A human-readable description of the current state."""
        return self._info["desc"]

    @property
    def display_mode(self) -> str:
        """The translated name for the current state, suitable for UI display."""
        mode_key = get_device_mode_from_state(self.raw_state)
        return STATE_TRANSLATIONS.get("de", {}).get(
            mode_key, mode_key.replace("_", " ").title()
        )

    @property
    def icon(self) -> str:
        """The appropriate icon for the current state."""
        mode_key = get_device_mode_from_state(self.raw_state)
        return STATE_ICONS.get(mode_key, "mdi:help-circle")

    def __repr__(self) -> str:
        return f"VioletState(raw='{self.raw_state}', mode='{self.mode}', active={self.is_active})"
