# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Service registration and handler composition for Violet services."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant, SupportsResponse

from .const import DOMAIN
from .refill_overflow_service import VioletRefillOverflowServiceHandlers
from .service_control import VioletControlServiceHandlers
from .service_diagnostics import VioletDiagnosticServiceHandlers
from .service_manager import VioletServiceManager
from .service_schemas import get_service_schemas

_LOGGER = logging.getLogger(__name__)


# =============================================================================
# SERVICE HANDLERS
# =============================================================================


class VioletServiceHandlers(
    VioletControlServiceHandlers,
    VioletDiagnosticServiceHandlers,
    VioletRefillOverflowServiceHandlers,
):
    """Compose all Violet service handlers."""

    def __init__(self, manager: VioletServiceManager):
        """
        Initialize service handlers.

        Args:
            manager: The service manager instance.
        """
        self.manager = manager
        self.hass = manager.hass


# =============================================================================
# REGISTRATION
# =============================================================================


async def async_register_services(hass: HomeAssistant) -> None:
    """
    Register all Violet Pool services.

    Args:
        hass: The Home Assistant instance.
    """
    # Check if services already registered
    if hass.services.has_service(DOMAIN, "control_pump"):
        _LOGGER.debug("Services already registered")
        return

    _LOGGER.info("Registering Violet Pool services")

    # Create service manager
    manager = VioletServiceManager(hass)
    handlers = VioletServiceHandlers(manager)

    # Get schemas
    schemas = get_service_schemas()

    # Register services
    # Regular services (no return value)
    regular_services = {
        "control_pump": handlers.handle_control_pump,
        "smart_dosing": handlers.handle_smart_dosing,
        "manage_pv_surplus": handlers.handle_manage_pv_surplus,
        "control_dmx_scenes": handlers.handle_control_dmx_scenes,
        "set_light_color_pulse": handlers.handle_set_light_color_pulse,
        "manage_digital_rules": handlers.handle_manage_digital_rules,
        "test_output": handlers.handle_test_output,
    }

    for service_name, handler in regular_services.items():
        hass.services.async_register(
            DOMAIN, service_name, handler, schema=schemas.get(service_name)
        )

    # NEW HTTP-based control services (Direct setFunctionManually API)
    http_control_services = {
        "control_pump_http": handlers.handle_control_pump_http,
        "control_heater_http": handlers.handle_control_heater_http,
        "control_solar_http": handlers.handle_control_solar_http,
        "control_cover_http": handlers.handle_control_cover_http,
        "control_backwash_http": handlers.handle_control_backwash_http,
        "manual_dosing_http": handlers.handle_manual_dosing_http,
        "control_refill_http": handlers.handle_control_refill_http,
    }

    for service_name, handler in http_control_services.items():
        hass.services.async_register(
            DOMAIN, service_name, handler, schema=schemas.get(service_name)
        )

    # Dosing configuration services
    dosing_config_services = {
        "configure_dosing": handlers.handle_configure_dosing,
        "set_dosing_target": handlers.handle_set_dosing_target,
        "set_dosing_daytime": handlers.handle_set_dosing_daytime,
        "set_dosing_max_daily": handlers.handle_set_dosing_max_daily,
        "enable_dosing": handlers.handle_enable_dosing,
    }

    for service_name, handler in dosing_config_services.items():
        hass.services.async_register(
            DOMAIN, service_name, handler, schema=schemas.get(service_name)
        )

    # Rule management services
    rule_management_services = {
        "configure_temp_rule": handlers.handle_configure_temp_rule,
        "configure_analog_rule": handlers.handle_configure_analog_rule,
        "configure_switching_rule": handlers.handle_configure_switching_rule,
        "configure_timer_rule": handlers.handle_configure_timer_rule,
        "enable_rule": handlers.handle_enable_rule,
    }

    for service_name, handler in rule_management_services.items():
        hass.services.async_register(
            DOMAIN, service_name, handler, schema=schemas.get(service_name)
        )

    # System configuration services (Phase 4)
    system_config_services = {
        "control_extension_relay": handlers.handle_control_extension_relay,
        "configure_sensor_calibration": handlers.handle_configure_sensor_calibration,
    }

    for service_name, handler in system_config_services.items():
        hass.services.async_register(
            DOMAIN, service_name, handler, schema=schemas.get(service_name)
        )

    # Refill and Overflow protection services
    refill_overflow_services = {
        "configure_refill": handlers.handle_configure_refill,
        "configure_overflow": handlers.handle_configure_overflow,
    }

    for service_name, handler in refill_overflow_services.items():
        hass.services.async_register(
            DOMAIN, service_name, handler, schema=schemas.get(service_name)
        )

    # Services returning data
    hass.services.async_register(
        DOMAIN,
        "export_diagnostic_logs",
        handlers.handle_export_diagnostic_logs,
        schema=schemas.get("export_diagnostic_logs"),
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        "get_connection_status",
        handlers.handle_get_connection_status,
        schema=schemas.get("get_connection_status"),
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        "get_error_summary",
        handlers.handle_get_error_summary,
        schema=schemas.get("get_error_summary"),
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        "test_connection",
        handlers.handle_test_connection,
        schema=schemas.get("test_connection"),
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        "clear_error_history",
        handlers.handle_clear_error_history,
        schema=schemas.get("clear_error_history"),
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        "get_refill_status",
        handlers.handle_get_refill_status,
        schema=schemas.get("get_refill_status"),
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        "get_overflow_status",
        handlers.handle_get_overflow_status,
        schema=schemas.get("get_overflow_status"),
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        "get_calibration_status",
        handlers.handle_get_calibration_status,
        schema=schemas.get("get_calibration_status"),
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        "get_backwash_status",
        handlers.handle_get_backwash_status,
        schema=schemas.get("get_backwash_status"),
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        "get_system_update_status",
        handlers.handle_get_system_update_status,
        schema=schemas.get("get_system_update_status"),
        supports_response=SupportsResponse.ONLY,
    )

    # Maintenance services: fault-blocking clear + canister refill accounting
    hass.services.async_register(
        DOMAIN,
        "reset_blocking",
        handlers.handle_reset_blocking,
        schema=schemas.get("reset_blocking"),
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        "set_can_amount",
        handlers.handle_set_can_amount,
        schema=schemas.get("set_can_amount"),
        supports_response=SupportsResponse.ONLY,
    )

    # System service management (FTP/Samba/SSH/Shairport/HomeKit/Alexa/Tunnels)
    hass.services.async_register(
        DOMAIN,
        "set_system_service",
        handlers.handle_set_system_service,
        schema=schemas.get("set_system_service"),
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        "get_system_services_status",
        handlers.handle_get_system_services_status,
        schema=schemas.get("get_system_services_status"),
        supports_response=SupportsResponse.ONLY,
    )

    # OmniTronic multi-port valve + live-trace diagnostic
    hass.services.async_register(
        DOMAIN,
        "set_omni_position",
        handlers.handle_set_omni_position,
        schema=schemas.get("set_omni_position"),
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        "get_live_trace_snapshot",
        handlers.handle_get_live_trace_snapshot,
        schema=schemas.get("get_live_trace_snapshot"),
        supports_response=SupportsResponse.ONLY,
    )

    total_services = (
        len(regular_services)
        + len(http_control_services)
        + len(dosing_config_services)
        + len(rule_management_services)
        + len(system_config_services)
        + len(refill_overflow_services)
        + 16  # diagnostic + status + maintenance services (see registrations above)
    )
    _LOGGER.info("Successfully registered %d services", total_services)
