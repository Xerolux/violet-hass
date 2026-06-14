# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Service schemas for pool controller manual control commands."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.helpers import config_validation as cv

# Device ID list schema (single device_id or list of device_ids)
DEVICE_ID_SCHEMA = vol.Any(
    cv.string,  # Single device_id
    [cv.string],  # List of device_ids
)

# Pump Control Schema
PUMP_CONTROL_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): DEVICE_ID_SCHEMA,
        vol.Optional("speed"): vol.In([0, 1, 2, 3]),  # RPM levels
        vol.Optional("action"): vol.In(["on", "off", "eco", "boost"]),
        vol.Optional("force_off"): cv.boolean,
    }
)

# Heater Control Schema
HEATER_CONTROL_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): DEVICE_ID_SCHEMA,
        vol.Optional("action"): vol.In(["on", "off"]),
        vol.Optional("target_temperature"): vol.All(
            vol.Coerce(float), vol.Range(min=10, max=60)
        ),
    }
)

# Solar Control Schema
SOLAR_CONTROL_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): DEVICE_ID_SCHEMA,
        vol.Optional("action"): vol.In(["on", "off"]),
        vol.Optional("target_temperature"): vol.All(
            vol.Coerce(float), vol.Range(min=10, max=60)
        ),
        vol.Optional("forced_flush"): cv.boolean,
    }
)

# Cover Control Schema
COVER_CONTROL_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): DEVICE_ID_SCHEMA,
        vol.Optional("action"): vol.In(["open", "close", "stop"]),
    }
)

# Backwash Control Schema
BACKWASH_CONTROL_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): DEVICE_ID_SCHEMA,
        vol.Optional("action"): vol.In(["run", "abort"]),
    }
)

# Manual Dosing Schema
MANUAL_DOSING_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): DEVICE_ID_SCHEMA,
        vol.Required("dosing_system"): vol.In(
            [
                "chlorine",
                "electrolysis",
                "ph_minus",
                "ph_plus",
                "flocculant",
                "h2o2",
            ]
        ),
        vol.Required("runtime_seconds"): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=3600)
        ),
    }
)

# Config Update Schema (flexible - allows various CONFIG.* keys)
CONFIG_UPDATE_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): DEVICE_ID_SCHEMA,
        vol.Required("config_updates"): cv.ensure_list,  # List of {key: value} dicts
    }
)

# Extension Relay Control Schema
EXTENSION_RELAY_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): DEVICE_ID_SCHEMA,
        vol.Required("relay"): cv.string,  # EXT1_1, EXT2_3, etc.
        vol.Optional("action"): vol.In(["on", "off"]),
    }
)

# PV Surplus Control Schema
PV_SURPLUS_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): DEVICE_ID_SCHEMA,
        vol.Optional("pump_enabled"): cv.boolean,
        vol.Optional("pump_rpm"): vol.In([0, 1, 2, 3]),
        vol.Optional("heater_enabled"): cv.boolean,
        vol.Optional("heater_target_temperature"): vol.All(
            vol.Coerce(float), vol.Range(min=10, max=60)
        ),
    }
)

# Test Output Schema
TEST_OUTPUT_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): DEVICE_ID_SCHEMA,
        vol.Required("output_name"): cv.string,
        vol.Optional("state"): vol.In([0, 1, 2, 3, 4, 5, 6]),
        vol.Optional("duration_seconds"): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=300)
        ),
    }
)
