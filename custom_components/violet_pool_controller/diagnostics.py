# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Diagnostics support for Violet Pool Controller."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, INTEGRATION_VERSION
from .error_handler import get_enhanced_error_handler
from .state_constants import get_state_name

# Fields redacted from config entry data (sensitive / privacy-relevant)
_REDACT_KEYS = {"password", "username"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    device = coordinator.device

    # --- Integration & config ---
    redacted_data = async_redact_data(dict(entry.data), _REDACT_KEYS)
    redacted_options = async_redact_data(dict(entry.options), _REDACT_KEYS)

    # --- Poll history statistics ---
    poll_stats: dict[str, Any] = {"total_polls": 0}
    history = device._poll_history
    if history:
        first_poll = history[0][0]
        last_poll = history[-1][0]
        data_counts = [count for _, count, *_ in history]
        poll_stats = {
            "total_polls": len(history),
            "first_poll": first_poll.isoformat()
            if isinstance(first_poll, datetime)
            else str(first_poll),
            "last_poll": last_poll.isoformat()
            if isinstance(last_poll, datetime)
            else str(last_poll),
            "avg_data_points": round(sum(data_counts) / len(data_counts), 1),
        }

    # --- Connection metrics ---
    connection: dict[str, Any] = {
        "system_health_pct": round(device.system_health, 1),
        "last_latency_ms": round(device.connection_latency, 1),
        "average_latency_ms": round(device.average_latency, 1),
        "total_api_requests": device._api_request_count,
        "api_request_rate_per_min": round(device.api_request_rate, 2),
        "seconds_since_last_update": round(device.last_event_age, 1),
        "last_update_success": coordinator.last_update_success,
    }

    # --- Error handler statistics ---
    error_handler = get_enhanced_error_handler()
    error_summary = error_handler.get_error_summary()
    recent_errors = [e.to_dict() for e in error_handler.get_recent_errors(5)]

    return {
        "integration": {
            "version": INTEGRATION_VERSION,
            "domain": DOMAIN,
        },
        "config_entry": {
            "title": entry.title,
            "entry_id": entry.entry_id,
            "data": redacted_data,
            "options": redacted_options,
        },
        "device": {
            "name": device.device_name,
            "controller_name": device.controller_name,
            "firmware": device._firmware_version,
            "device_id": device.device_id,
            "api_url": device.api_url,
            "use_ssl": device.use_ssl,
            "available": device.available,
            "consecutive_failures": device._consecutive_failures,
            "last_error": device.last_error,
        },
        "connection": connection,
        "current_data": dict(coordinator.data) if coordinator.data else {},
        "poll_statistics": poll_stats,
        "error_statistics": error_summary,
        "recent_errors": recent_errors,
        "state_hierarchy_reference": {
            "0": {"name": get_state_name(0), "description": "Auto standby/off"},
            "1": {"name": get_state_name(1), "description": "Auto active/on"},
            "2": {"name": get_state_name(2), "description": "Rule blocked (priority off)"},
            "3": {"name": get_state_name(3), "description": "Emergency rule (priority on)"},
            "4": {"name": get_state_name(4), "description": "Manual on (forced)"},
            "5": {"name": get_state_name(5), "description": "Emergency off (safety rule)"},
            "6": {"name": get_state_name(6), "description": "Manual off"},
        },
    }
