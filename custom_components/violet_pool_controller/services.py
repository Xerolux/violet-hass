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
from .runtime_data import SERVICE_MANAGER_KEY
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

# Every service the integration registers, in the order it appears in the UI.
# The handler is always ``VioletServiceHandlers.handle_<name>`` and the schema
# always ``get_service_schemas()[<name>]``; the only per-service decision left
# is whether the service returns data, so that is all this table stores.
#
# Keeping the list here rather than in eight near-identical loops is what lets
# ``tests/test_service_parity.py`` compare the registered services against
# ``services.yaml`` and ``strings.json`` without starting Home Assistant.
SERVICES_WITHOUT_RESPONSE: tuple[str, ...] = (
    # Control and action services
    "control_pump",
    "smart_dosing",
    "manage_pv_surplus",
    "control_dmx_scenes",
    "set_light_color_pulse",
    "manage_digital_rules",
    "test_output",
    # Direct setFunctionManually control services
    "control_pump_http",
    "control_heater_http",
    "control_solar_http",
    "control_cover_http",
    "control_backwash_http",
    "manual_dosing_http",
    "control_refill_http",
    # Dosing configuration
    "configure_dosing",
    "set_dosing_target",
    "set_dosing_daytime",
    "set_dosing_max_daily",
    "enable_dosing",
    # Rule management
    "configure_temp_rule",
    "configure_analog_rule",
    "configure_switching_rule",
    "configure_timer_rule",
    "enable_rule",
    # System configuration
    "control_extension_relay",
    "configure_sensor_calibration",
    # Refill and overflow protection
    "configure_refill",
    "configure_overflow",
)

SERVICES_WITH_RESPONSE: tuple[str, ...] = (
    # Diagnostics
    "export_diagnostic_logs",
    "get_connection_status",
    "get_error_summary",
    "test_connection",
    "clear_error_history",
    # Status queries
    "get_refill_status",
    "get_overflow_status",
    "get_calibration_status",
    "get_backwash_status",
    "get_system_update_status",
    # Maintenance
    "reset_blocking",
    "set_can_amount",
    # Controller-side system services
    "set_system_service",
    "get_system_services_status",
    # OmniTronic valve and live trace
    "set_omni_position",
    "get_live_trace_snapshot",
)

SERVICE_HANDLER_NAMES: tuple[str, ...] = SERVICES_WITHOUT_RESPONSE + SERVICES_WITH_RESPONSE


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

    # The service manager is integration-wide rather than per config entry, so
    # it stays in hass.data (per-entry state lives on entry.runtime_data). Other
    # components - e.g. the switch entity's safety gate - reach the SafetyGuard
    # through it.
    manager = VioletServiceManager(hass)
    hass.data.setdefault(DOMAIN, {})[SERVICE_MANAGER_KEY] = manager

    # Re-arm any persisted safety deadlines (e.g. a refill that was running
    # when HA last restarted).
    await manager.async_setup_safety()

    handlers = VioletServiceHandlers(manager)
    schemas = get_service_schemas()

    for service_name in SERVICE_HANDLER_NAMES:
        hass.services.async_register(
            DOMAIN,
            service_name,
            getattr(handlers, f"handle_{service_name}"),
            schema=schemas.get(service_name),
            supports_response=(
                SupportsResponse.ONLY
                if service_name in SERVICES_WITH_RESPONSE
                else SupportsResponse.NONE
            ),
        )

    _LOGGER.info("Successfully registered %d services", len(SERVICE_HANDLER_NAMES))


async def async_unload_services(hass: HomeAssistant) -> None:
    """Remove every service and the integration-wide service manager.

    Called when the last config entry unloads.  Without this the 44 services
    stayed registered against a manager whose controllers were gone, and the
    SafetyGuard's armed timers kept running: reloading the integration then
    found the services already present and skipped registration, so the new
    manager was never wired up.
    """
    domain_data = hass.data.get(DOMAIN, {})
    manager = domain_data.pop(SERVICE_MANAGER_KEY, None)
    if manager is not None:
        await manager.safety_guard.async_shutdown()

    for service_name in SERVICE_HANDLER_NAMES:
        if hass.services.has_service(DOMAIN, service_name):
            hass.services.async_remove(DOMAIN, service_name)

    _LOGGER.info("Removed %d services", len(SERVICE_HANDLER_NAMES))
