# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Extended state constants and state hierarchy definitions for Violet Pool Controller."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# =============================================================================
# STATE HIERARCHY (0-6) - State Priority System
# =============================================================================
# The Violet controller uses a state hierarchy where higher values cannot be
# overwritten by lower values. This ensures manual/emergency control always
# overrides automatic scheduling.

# State Codes
STATE_AUTO_STANDBY: Final = 0          # Auto mode: device off/standby
STATE_AUTO_ACTIVE: Final = 1           # Auto mode: active/scheduled on
STATE_AUTO_PRIORITY_OFF: Final = 2     # Auto mode: blocked by control rule
STATE_AUTO_PRIORITY_ON: Final = 3      # Auto mode: priority on (emergency rule)
STATE_MANUAL_ON: Final = 4             # Manual mode: forced on
STATE_EMERGENCY_OFF: Final = 5         # Emergency mode: off (emergency rule)
STATE_MANUAL_OFF: Final = 6            # Manual mode: forced off

# State Groups
AUTO_OFF_STATES: Final[set[int]] = {
    STATE_AUTO_STANDBY,
    STATE_AUTO_PRIORITY_OFF,
    STATE_EMERGENCY_OFF,
    STATE_MANUAL_OFF,
}
AUTO_ON_STATES: Final[set[int]] = {
    STATE_AUTO_ACTIVE,
    STATE_AUTO_PRIORITY_ON,
    STATE_MANUAL_ON,
}
ON_STATES: Final[set[int]] = {
    STATE_AUTO_ACTIVE,
    STATE_AUTO_PRIORITY_ON,
    STATE_MANUAL_ON,
}
OFF_STATES: Final[set[int]] = {
    STATE_AUTO_STANDBY,
    STATE_AUTO_PRIORITY_OFF,
    STATE_EMERGENCY_OFF,
    STATE_MANUAL_OFF,
}

# Priority Levels (inverted: higher number = higher priority)
PRIORITY_AUTO: Final = 0               # Automatic scheduling (lowest priority)
PRIORITY_RULE_BLOCKED: Final = 1       # Blocked by control rule
PRIORITY_EMERGENCY: Final = 2          # Emergency/safety rule override
PRIORITY_MANUAL: Final = 3             # Manual control (highest priority)


@dataclass(frozen=True)
class StateDefinition:
    """Complete state definition with metadata."""

    code: int
    name_en: str
    name_de: str
    description_en: str
    description_de: str
    is_active: bool
    priority_level: int
    control_source: str

    @property
    def display_name(self) -> str:
        """Return English display name."""
        return self.name_en

    @property
    def display_name_de(self) -> str:
        """Return German display name."""
        return self.name_de


# Complete State Definitions Database
STATE_DEFINITIONS: Final[dict[int, StateDefinition]] = {
    STATE_AUTO_STANDBY: StateDefinition(
        code=0,
        name_en="Auto Standby",
        name_de="Auto – Bereitschaft",
        description_en="Device is off, waiting for scheduling trigger",
        description_de="Gerät aus, wartet auf Planungstrigger",
        is_active=False,
        priority_level=PRIORITY_AUTO,
        control_source="automatic",
    ),
    STATE_AUTO_ACTIVE: StateDefinition(
        code=1,
        name_en="Auto Active (Scheduled)",
        name_de="Auto – Aktiv (Geplant)",
        description_en="Device is on by automatic scheduling rule",
        description_de="Gerät ist durch automatische Planungsregel eingeschaltet",
        is_active=True,
        priority_level=PRIORITY_AUTO,
        control_source="automatic",
    ),
    STATE_AUTO_PRIORITY_OFF: StateDefinition(
        code=2,
        name_en="Auto Priority OFF (Rule Blocked)",
        name_de="Auto – Priorität AUS (Regel blockiert)",
        description_en="Device blocked by control rule or external condition",
        description_de="Gerät durch Kontrollregel oder externe Bedingung blockiert",
        is_active=False,
        priority_level=PRIORITY_RULE_BLOCKED,
        control_source="rule_blocker",
    ),
    STATE_AUTO_PRIORITY_ON: StateDefinition(
        code=3,
        name_en="Auto Priority ON (Emergency Rule)",
        name_de="Auto – Priorität AN (Notfallregel)",
        description_en="Device forced on by emergency or safety rule",
        description_de="Gerät durch Notfall- oder Sicherheitsregel erzwungen",
        is_active=True,
        priority_level=PRIORITY_EMERGENCY,
        control_source="emergency_rule",
    ),
    STATE_MANUAL_ON: StateDefinition(
        code=4,
        name_en="Manual ON (Forced)",
        name_de="Manuell AN (Erzwungen)",
        description_en="Device manually forced on by user",
        description_de="Gerät manuell vom Benutzer erzwungen",
        is_active=True,
        priority_level=PRIORITY_MANUAL,
        control_source="user_manual",
    ),
    STATE_EMERGENCY_OFF: StateDefinition(
        code=5,
        name_en="Emergency OFF (Safety Rule)",
        name_de="Notfall AUS (Sicherheitsregel)",
        description_en="Device forced off by safety/emergency rule",
        description_de="Gerät durch Sicherheits-/Notfallregel erzwungen",
        is_active=False,
        priority_level=PRIORITY_EMERGENCY,
        control_source="emergency_rule",
    ),
    STATE_MANUAL_OFF: StateDefinition(
        code=6,
        name_en="Manual OFF (User Control)",
        name_de="Manuell AUS (Benutzer)",
        description_en="Device manually turned off by user",
        description_de="Gerät manuell vom Benutzer ausgeschaltet",
        is_active=False,
        priority_level=PRIORITY_MANUAL,
        control_source="user_manual",
    ),
}


def get_state_definition(state_code: int) -> StateDefinition | None:
    """Get state definition by code."""
    return STATE_DEFINITIONS.get(state_code)


def get_state_name(state_code: int, german: bool = False) -> str:
    """Get state name by code."""
    definition = get_state_definition(state_code)
    if definition:
        return definition.name_de if german else definition.name_en
    return f"Unknown State {state_code}"


def get_state_description(state_code: int, german: bool = False) -> str:
    """Get state description by code."""
    definition = get_state_definition(state_code)
    if definition:
        return definition.description_de if german else definition.description_en
    return "No description available"


def get_priority_level(state_code: int) -> int:
    """Get priority level (0-3) for state code."""
    definition = get_state_definition(state_code)
    return definition.priority_level if definition else 0


def is_active_state(state_code: int) -> bool:
    """Check if state code represents active/on condition."""
    definition = get_state_definition(state_code)
    return definition.is_active if definition else False


def get_control_source(state_code: int) -> str:
    """Get control source description for state code."""
    definition = get_state_definition(state_code)
    return definition.control_source if definition else "unknown"
