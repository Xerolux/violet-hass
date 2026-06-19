# =============================================================================
# Violet Pool Controller – Sensor Organization
# Copyright © 2026 Xerolux
# =============================================================================

"""Sensor organization following original WebUI layout (CID system)."""

from __future__ import annotations

# Sensor grouping following WebUI CID (Control ID) structure
SENSOR_GROUPS: dict[str, dict[str, str | list[str]]] = {
    # CID=1: Pump Control - Circulation & Water Movement
    "pump": {
        "category": "Circulation",
        "icon": "mdi:pump",
        "sensors": [
            "pump_state",
            "pump_speed",
            "pump_runtime",
            "pump_power",
            "pump_anti_freeze",
        ],
    },
    # CID=2: Solar Control - Renewable Heating
    "solar": {
        "category": "Heating - Solar",
        "icon": "mdi:white-balance-sunny",
        "sensors": [
            "solar_state",
            "solar_collector_temp",
            "solar_efficiency",
            "solar_last_off",
            "solar_anti_freeze",
        ],
    },
    # CID=3: Heater Control - Primary Heating
    "heater": {
        "category": "Heating - Electric",
        "icon": "mdi:fire",
        "sensors": [
            "heater_state",
            "pool_temperature",
            "heater_target_temp",
            "boiler_temperature",
            "heater_postrun_delay",
            "hx_temperature",
        ],
    },
    # CID=4: Backwash Control - Filter Maintenance
    "backwash": {
        "category": "Maintenance",
        "icon": "mdi:water-opacity",
        "sensors": [
            "backwash_state",
            "backwash_step",
            "backwash_last_auto_run",
            "backwash_last_manual_run",
            "filter_pressure",
        ],
    },
    # CID=5: Refill Control - Water Level Management
    "refill": {
        "category": "Water Level",
        "icon": "mdi:water-percent",
        "sensors": [
            "refill_state",
            "refill_enabled",
            "refill_type",
            "water_level",
            "refill_active",
        ],
    },
    # CID=6: Overflow Control - Protection
    "overflow": {
        "category": "Water Level Protection",
        "icon": "mdi:water-alert",
        "sensors": [
            "overflow_state",
            "overflow_enabled",
            "overflow_active",
            "dryrun_active",
            "bathing_detected",
        ],
    },
    # CID=7: Light & DMX Control - Lighting
    "light": {
        "category": "Lighting",
        "icon": "mdi:lightbulb",
        "sensors": [
            "light_state",
            "light_brightness",
            "light_color",
            "dmx_scene",
        ],
    },
    # CID=8: Cover Control - Pool Cover
    "cover": {
        "category": "Maintenance",
        "icon": "mdi:pool",
        "sensors": [
            "cover_state",
            "cover_position",
        ],
    },
    # Chemistry - Water Quality
    "chemistry": {
        "category": "Chemistry",
        "icon": "mdi:flask",
        "sensors": [
            "ph_value",
            "ph_target",
            "orp_value",
            "orp_target",
            "chlorine_level",
            "conductivity",
        ],
    },
    # System & Monitoring
    "system": {
        "category": "System",
        "icon": "mdi:cog",
        "sensors": [
            "system_uptime",
            "cpu_temperature",
            "system_memory",
            "error_count",
            "connection_status",
        ],
    },
}

# Backwash state mappings (from WebUI)
BACKWASH_STATES = {
    0: "Idle",
    1: "Backwash Running",
    2: "Rinse Running",
    3: "Draining",
    4: "Completed",
    5: "Error",
    6: "Paused",
}

BACKWASH_STEPS = {
    0: "Not started",
    1: "Valve to backwash",
    2: "Pump backwash",
    3: "Valve to rinse",
    4: "Pump rinse",
    5: "Valve to normal",
    6: "Drain",
    7: "Completed",
}

# Sensor organization helper for UI rendering
def get_sensors_by_group(group: str) -> dict[str, str | list[str]]:
    """Get all sensors for a group."""
    if group in SENSOR_GROUPS:
        return {
            "category": SENSOR_GROUPS[group]["category"],
            "icon": SENSOR_GROUPS[group]["icon"],
            "sensors": SENSOR_GROUPS[group]["sensors"],
        }
    return {}


def get_all_sensors_organized() -> dict[str, dict]:
    """Get all sensors organized by group."""
    return SENSOR_GROUPS


def get_group_for_sensor(sensor_key: str) -> str | None:
    """Find which group a sensor belongs to."""
    for group, info in SENSOR_GROUPS.items():
        if sensor_key in info["sensors"]:
            return group
    return None
