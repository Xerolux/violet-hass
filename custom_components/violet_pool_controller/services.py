# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Service registration and handler composition for Violet services."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant, SupportsResponse

from .const import DOMAIN
from .service_control import VioletControlServiceHandlers
from .service_diagnostics import VioletDiagnosticServiceHandlers
from .service_helpers import as_device_id_list
from .service_manager import VioletServiceManager
from .service_schemas import get_service_schemas

_LOGGER = logging.getLogger(__name__)


# =============================================================================
# SERVICE HANDLERS
# =============================================================================


class VioletServiceHandlers(
    VioletControlServiceHandlers, VioletDiagnosticServiceHandlers
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

    @staticmethod
    def _normalize_device_ids(raw: Any) -> list[str]:
        """
        Normalize a raw device id payload to a list of ids.

        Args:
            raw: The raw device ID input.

        Returns:
            A list of device IDs.
        """
        return as_device_id_list(raw)


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

    _LOGGER.info(
        "Successfully registered %d services",
        len(regular_services) + 5,  # 5 diagnostic services
    )
