"""Device-bezogene Konstanten für die Violet Pool Controller Integration."""

# =============================================================================
# DEVICE PARAMETERS - Extended Configuration
# =============================================================================

DEVICE_PARAMETERS = {
    "PUMP": {
        "supports_speed": True,
        "supports_timer": True,
        "supports_force_off": True,
        "speeds": {1: "Eco (Niedrig)", 2: "Normal (Mittel)", 3: "Boost (Hoch)"},
        "default_on_speed": 2,
        "force_off_duration": 600,
        "activity_sensors": ["PUMP_RPM_1_VALUE", "PUMP_RUNTIME"],
        "activity_threshold": {"PUMP_RPM_1_VALUE": 100},
        "api_template": "PUMP,{action},{duration},{speed}",
    },
    "HEATER": {
        "supports_timer": True,
        "supports_temperature": True,
        "default_on_duration": 0,
        "activity_sensors": ["onewire5_value", "onewire1_value", "HEATER_RUNTIME"],
        "activity_threshold": {"temp_diff": 2.0},
        "api_template": "HEATER,{action},{duration},0",
    },
    "SOLAR": {
        "supports_timer": True,
        "default_on_duration": 0,
        "activity_sensors": ["onewire3_value", "onewire1_value", "SOLAR_RUNTIME"],
        "activity_threshold": {"temp_diff": 5.0},
        "api_template": "SOLAR,{action},{duration},0",
    },
    "LIGHT": {
        "supports_color_pulse": True,
        "color_pulse_duration": 150,
        "api_template": "LIGHT,{action},0,0",
        "color_pulse_template": "LIGHT,COLOR,0,0",
    },
    "DOS_1_CL": {
        "supports_timer": True,
        "dosing_type": "Chlor",
        "default_dosing_duration": 30,
        "max_dosing_duration": 300,
        "safety_interval": 300,
        "activity_sensors": ["DOS_1_CL_RUNTIME", "DOS_1_CL_STATE"],
        "api_template": "DOS_1_CL,{action},{duration},0",
    },
    "DOS_4_PHM": {
        "supports_timer": True,
        "dosing_type": "pH-",
        "default_dosing_duration": 30,
        "max_dosing_duration": 300,
        "safety_interval": 300,
        "activity_sensors": ["DOS_4_PHM_RUNTIME", "DOS_4_PHM_STATE"],
        "api_template": "DOS_4_PHM,{action},{duration},0",
    },
    "DOS_5_PHP": {
        "supports_timer": True,
        "dosing_type": "pH+",
        "default_dosing_duration": 30,
        "max_dosing_duration": 300,
        "safety_interval": 300,
        "activity_sensors": ["DOS_5_PHP_RUNTIME", "DOS_5_PHP_STATE"],
        "api_template": "DOS_5_PHP,{action},{duration},0",
    },
    "DOS_6_FLOC": {
        "supports_timer": True,
        "dosing_type": "Flockmittel",
        "default_dosing_duration": 60,
        "max_dosing_duration": 600,
        "safety_interval": 600,
        "activity_sensors": ["DOS_6_FLOC_RUNTIME"],
        "api_template": "DOS_6_FLOC,{action},{duration},0",
    },
    "BACKWASH": {
        "supports_timer": True,
        "default_duration": 180,
        "max_duration": 900,
        "activity_sensors": ["BACKWASH_RUNTIME", "BACKWASHSTATE"],
        "api_template": "BACKWASH,{action},{duration},0",
    },
    "BACKWASHRINSE": {
        "supports_timer": True,
        "default_duration": 60,
        "max_duration": 300,
        "activity_sensors": ["BACKWASH_RUNTIME"],
        "api_template": "BACKWASHRINSE,{action},{duration},0",
    },
    "PVSURPLUS": {
        "supports_speed": True,
        "speeds": {1: "Eco", 2: "Normal", 3: "Boost"},
        "default_speed": 2,
        "activity_sensors": ["PVSURPLUS"],
        "activity_threshold": {"PVSURPLUS": 1},
        "api_template": "PVSURPLUS,{action},{speed},0",
    },
}

# Extension relays with runtime sensors
for ext_bank in [1, 2]:
    for relay_num in range(1, 9):
        key = f"EXT{ext_bank}_{relay_num}"
        DEVICE_PARAMETERS[key] = {
            "supports_timer": True,
            "default_on_duration": 3600,
            "max_duration": 86400,
            "activity_sensors": [f"EXT{ext_bank}_{relay_num}_RUNTIME"],
            "api_template": f"EXT{ext_bank}_{relay_num},{{action}},{{duration}},0",
        }

# Digital Rules
for rule_num in range(1, 8):
    key = f"DIRULE_{rule_num}"
    DEVICE_PARAMETERS[key] = {
        "supports_lock": True,
        "action_type": "PUSH",
        "pulse_duration": 500,
        "api_template": f"DIRULE_{rule_num},{{action}},0,0",
    }

# DMX Scenes
for scene_num in range(1, 13):
    key = f"DMX_SCENE{scene_num}"
    DEVICE_PARAMETERS[key] = {
        "supports_group_control": True,
        "group_actions": ["ALLON", "ALLOFF", "ALLAUTO"],
        "api_template": f"DMX_SCENE{scene_num},{{action}},0,0",
    }

# =============================================================================
# STATE MAPPINGS - CRITICAL FOR 3-STATE SUPPORT
# =============================================================================

# Device State Mapping - Extended state information with State 4
DEVICE_STATE_MAPPING = {
    # String-based states
    "ON": {"mode": "manual", "active": True, "priority": 80},
    "OFF": {"mode": "manual", "active": False, "priority": 70},
    "AUTO": {"mode": "auto", "active": None, "priority": 60},
    "MAN": {"mode": "manual", "active": True, "priority": 80},
    "MANUAL": {"mode": "manual", "active": True, "priority": 80},
    # Numeric states (as documented in API)
    "0": {"mode": "auto", "active": False, "priority": 50, "desc": "AUTO - Standby"},
    "1": {"mode": "manual", "active": True, "priority": 80, "desc": "Manuell EIN"},
    "2": {"mode": "auto", "active": True, "priority": 60, "desc": "AUTO - Aktiv"},
    "3": {"mode": "auto", "active": True, "priority": 65, "desc": "AUTO - Aktiv (Zeitsteuerung)"},
    "4": {"mode": "manual", "active": True, "priority": 85, "desc": "Manuell EIN (forciert)"},
    "5": {"mode": "auto", "active": False, "priority": 55, "desc": "AUTO - Wartend"},
    "6": {"mode": "manual", "active": False, "priority": 70, "desc": "Manuell AUS"},
    # Additional states
    "STOPPED": {"mode": "manual", "active": False, "priority": 75},
    "ERROR": {"mode": "error", "active": False, "priority": 100},
    "MAINTENANCE": {"mode": "maintenance", "active": False, "priority": 90},
}

# CRITICAL FIX: STATE_MAP with State 4
STATE_MAP = {
    # Numeric states as integer (direct API values)
    0: False,  # AUTO-Standby (OFF)
    1: True,   # Manuell EIN
    2: True,   # AUTO-Aktiv (ON)
    3: True,   # AUTO-Zeitsteuerung (ON)
    4: True,   # ⭐ Manuell forciert EIN (ON) - CRITICAL FIX!
    5: False,  # AUTO-Wartend (OFF)
    6: False,  # Manuell AUS
    # Numeric states as string (if API delivers as string)
    "0": False,
    "1": True,
    "2": True,
    "3": True,
    "4": True,  # ⭐ CRITICAL FIX!
    "5": False,
    "6": False,
    # String-based states
    "ON": True,
    "OFF": False,
    "AUTO": False,
    "TRUE": True,
    "FALSE": False,
    "OPEN": True,
    "CLOSED": False,
    "OPENING": True,
    "CLOSING": True,
    "STOPPED": False,
    "MAN": True,
    "MANUAL": True,
    "ACTIVE": True,
    "RUNNING": True,
    "IDLE": False,
}

# COVER_STATE_MAP with string states
COVER_STATE_MAP = {
    # Numeric states
    "0": "open",
    "1": "opening",
    "2": "closed",
    "3": "closing",
    "4": "stopped",
    # String states (recognized from API)
    "OPEN": "open",
    "CLOSED": "closed",
    "OPENING": "opening",
    "CLOSING": "closing",
    "STOPPED": "stopped",
}

# =============================================================================
# STATE VISUALIZATION
# =============================================================================

STATE_ICONS = {
    "PUMP": {
        "auto_active": "mdi:water-pump",
        "auto_inactive": "mdi:water-pump-off",
        "manual_on": "mdi:water-pump",
        "manual_off": "mdi:water-pump-off",
        "error": "mdi:water-pump-alert",
        "maintenance": "mdi:water-pump-wrench",
    },
    "HEATER": {
        "auto_active": "mdi:radiator",
        "auto_inactive": "mdi:radiator-disabled",
        "manual_on": "mdi:radiator",
        "manual_off": "mdi:radiator-off",
        "error": "mdi:radiator-alert",
        "maintenance": "mdi:radiator-wrench",
    },
    "SOLAR": {
        "auto_active": "mdi:solar-power",
        "auto_inactive": "mdi:solar-power-variant-outline",
        "manual_on": "mdi:solar-power",
        "manual_off": "mdi:solar-power-off",
        "error": "mdi:solar-power-alert",
    },
    "LIGHT": {
        "auto_active": "mdi:lightbulb-on",
        "auto_inactive": "mdi:lightbulb-auto",
        "manual_on": "mdi:lightbulb-on",
        "manual_off": "mdi:lightbulb-off",
        "color_pulse": "mdi:lightbulb-multiple",
    },
    "DOS_1_CL": {
        "auto_active": "mdi:flask",
        "auto_inactive": "mdi:flask-outline",
        "manual_on": "mdi:flask-plus",
        "manual_off": "mdi:flask-off",
    },
    "DOS_4_PHM": {
        "auto_active": "mdi:flask-minus",
        "auto_inactive": "mdi:flask-minus-outline",
        "manual_on": "mdi:flask-minus",
        "manual_off": "mdi:flask-off",
    },
    "DOS_5_PHP": {
        "auto_active": "mdi:flask-plus",
        "auto_inactive": "mdi:flask-plus-outline",
        "manual_on": "mdi:flask-plus",
        "manual_off": "mdi:flask-off",
    },
    "BACKWASH": {
        "auto_active": "mdi:valve-open",
        "auto_inactive": "mdi:valve",
        "manual_on": "mdi:valve-open",
        "manual_off": "mdi:valve-closed",
    },
    "PVSURPLUS": {
        "auto_active": "mdi:solar-power-variant",
        "auto_inactive": "mdi:solar-power-variant-outline",
        "manual_on": "mdi:solar-power-variant",
        "manual_off": "mdi:solar-power-variant-outline",
    },
}

STATE_COLORS = {
    "auto_active": "#4CAF50",     # Grün
    "auto_inactive": "#2196F3",   # Blau
    "manual_on": "#FF9800",       # Orange
    "manual_off": "#F44336",      # Rot
    "error": "#9C27B0",           # Lila
    "maintenance": "#607D8B",     # Grau
}

STATE_TRANSLATIONS = {
    "de": {
        "auto_active": "Automatik (Aktiv)",
        "auto_inactive": "Automatik (Bereit)",
        "manual_on": "Manuell Ein",
        "manual_off": "Manuell Aus",
        "error": "Fehler",
        "maintenance": "Wartung",
        "unknown": "Unbekannt",
    },
    "en": {
        "auto_active": "Auto (Active)",
        "auto_inactive": "Auto (Ready)",
        "manual_on": "Manual On",
        "manual_off": "Manual Off",
        "error": "Error",
        "maintenance": "Maintenance",
        "unknown": "Unknown",
    },
}

# =============================================================================
# VALIDATION AND MONITORING
# =============================================================================

DEVICE_VALIDATION_RULES = {
    "PUMP": {
        "min_speed": 1,
        "max_speed": 3,
        "min_off_duration": 60,
        "max_off_duration": 3600,
        "rpm_thresholds": {"min_active": 100, "max_normal": 3000},
    },
    "HEATER": {
        "min_temp": 20.0,
        "max_temp": 40.0,
        "temp_step": 0.5,
        "max_temp_diff": 50.0,
    },
    "DOS_1_CL": {
        "min_dosing": 5,
        "max_dosing": 300,
        "safety_interval": 300,
        "max_daily_runtime": 1800,
    },
    "DOS_4_PHM": {
        "min_dosing": 5,
        "max_dosing": 300,
        "safety_interval": 300,
        "max_daily_runtime": 1800,
    },
    "DOS_5_PHP": {
        "min_dosing": 5,
        "max_dosing": 300,
        "safety_interval": 300,
        "max_daily_runtime": 1800,
    },
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_device_state_info(raw_state: str, device_key: str = None) -> dict:
    """Get extended state information for a device."""
    if not raw_state:
        return {"mode": "auto", "active": False, "priority": 50, "desc": "Unknown"}

    upper_state = str(raw_state).upper().strip()

    if upper_state in DEVICE_STATE_MAPPING:
        return DEVICE_STATE_MAPPING[upper_state]

    return {"mode": "auto", "active": None, "priority": 10, "desc": f"Unknown state: {raw_state}"}


def legacy_is_on_state(raw_state: str) -> bool:
    """Legacy function for simple On/Off check."""
    if not raw_state:
        return False

    # Test integer values directly
    try:
        int_state = int(raw_state) if isinstance(raw_state, (int, float)) else int(str(raw_state))
        if int_state in STATE_MAP:
            return STATE_MAP[int_state]
    except (ValueError, TypeError):
        pass

    # Then string values
    upper_state = str(raw_state).upper().strip()
    if upper_state in STATE_MAP:
        return STATE_MAP[upper_state]

    # Fallback to extended state information
    state_info = get_device_state_info(raw_state)
    if state_info.get("active") is not None:
        return state_info.get("active")

    return False


def get_device_mode_from_state(raw_state: str, device_key: str = None) -> str:
    """Get device mode from raw state value."""
    state_info = get_device_state_info(raw_state, device_key)
    mode = state_info.get("mode", "auto")
    active = state_info.get("active")

    if mode == "manual":
        return "manual_on" if active else "manual_off"
    elif mode == "auto":
        return "auto_active" if active else "auto_inactive"
    else:
        return mode


def get_device_icon(device_key: str, mode: str) -> str:
    """Get appropriate icon for a device based on mode."""
    if device_key in STATE_ICONS:
        return STATE_ICONS[device_key].get(
            mode, STATE_ICONS[device_key].get("auto_inactive", "mdi:help")
        )

    fallback_icons = {
        "auto_active": "mdi:auto-mode",
        "auto_inactive": "mdi:auto-mode-outline",
        "manual_on": "mdi:power-on",
        "manual_off": "mdi:power-off",
        "error": "mdi:alert-circle",
        "maintenance": "mdi:wrench",
    }

    return fallback_icons.get(mode, "mdi:help")


def get_device_color(mode: str) -> str:
    """Get display color for a device mode."""
    return STATE_COLORS.get(mode, "#9E9E9E")


# =============================================================================
# VIOLET STATE CLASS
# =============================================================================


class VioletState:
    """Extended state class for 3-State support."""

    def __init__(self, raw_state: str, device_key: str = None):
        self.raw_state = str(raw_state).strip()
        self.device_key = device_key
        self._state_info = get_device_state_info(self.raw_state, device_key)

    @property
    def mode(self) -> str:
        """Device mode: auto, manual, error, maintenance."""
        return self._state_info.get("mode", "auto")

    @property
    def is_active(self) -> bool:
        """Is the device active? None = depends on external factors."""
        return self._state_info.get("active")

    @property
    def priority(self) -> int:
        """Display priority for UI sorting."""
        return self._state_info.get("priority", 50)

    @property
    def description(self) -> str:
        """Human-readable description of the state."""
        return self._state_info.get("desc", f"State: {self.raw_state}")

    @property
    def display_mode(self) -> str:
        """Display name for UI."""
        mode_key = get_device_mode_from_state(self.raw_state, self.device_key)
        return STATE_TRANSLATIONS.get("de", {}).get(mode_key, mode_key)

    @property
    def icon(self) -> str:
        """Appropriate icon for current state."""
        mode_key = get_device_mode_from_state(self.raw_state, self.device_key)
        return get_device_icon(self.device_key, mode_key)

    @property
    def color(self) -> str:
        """Display color for current state."""
        mode_key = get_device_mode_from_state(self.raw_state, self.device_key)
        return get_device_color(mode_key)

    def is_manual_mode(self) -> bool:
        """Is the device in manual mode?"""
        return self.mode == "manual"

    def is_auto_mode(self) -> bool:
        """Is the device in automatic mode?"""
        return self.mode == "auto"

    def is_error_state(self) -> bool:
        """Is the device in an error state?"""
        return self.mode in ["error", "maintenance"]

    def __str__(self) -> str:
        return f"VioletState({self.device_key}): {self.display_mode} ({self.raw_state})"

    def __repr__(self) -> str:
        return (
            f"VioletState(raw_state='{self.raw_state}', "
            f"device_key='{self.device_key}', mode='{self.mode}', "
            f"active={self.is_active})"
        )


__all__ = [
    "DEVICE_PARAMETERS",
    "DEVICE_STATE_MAPPING",
    "STATE_MAP",
    "COVER_STATE_MAP",
    "STATE_ICONS",
    "STATE_COLORS",
    "STATE_TRANSLATIONS",
    "DEVICE_VALIDATION_RULES",
    "get_device_state_info",
    "legacy_is_on_state",
    "get_device_mode_from_state",
    "get_device_icon",
    "get_device_color",
    "VioletState",
]
