"""Service implementations for Violet Pool Controller.

This file should be saved as: custom_components/violet_pool_controller/services.py
"""
import logging
from typing import Any
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_registry
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, ACTION_AUTO, ACTION_ON, ACTION_OFF
from .api import VioletPoolAPIError

_LOGGER = logging.getLogger(__name__)

async def async_register_enhanced_services(hass: HomeAssistant) -> None:
    """Register enhanced services for the integration."""
    if hass.services.has_service(DOMAIN, "turn_auto"):
        return

    # Enhanced service schemas
    ENHANCED_SERVICE_SCHEMAS = {
        "turn_auto": vol.Schema({
            vol.Required("entity_id"): cv.entity_ids,
            vol.Optional("auto_delay", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=86400)),
        }),
        "set_pv_surplus": vol.Schema({
            vol.Required("entity_id"): cv.entity_ids,
            vol.Optional("pump_speed", default=2): vol.All(vol.Coerce(int), vol.Range(min=1, max=3)),
        }),
        "manual_dosing": vol.Schema({
            vol.Required("entity_id"): cv.entity_ids,
            vol.Required("duration_seconds"): vol.All(vol.Coerce(int), vol.Range(min=1, max=3600)),
        }),
    }

    async def get_coordinators_for_entities(entity_ids: list[str]) -> set:
        """Get coordinators for given entity IDs."""
        registry = entity_registry.async_get(hass)
        coordinators = set()
        
        for entity_id in entity_ids:
            entity_entry = registry.async_get(entity_id)
            if entity_entry and entity_entry.config_entry_id in hass.data.get(DOMAIN, {}):
                coordinators.add(hass.data[DOMAIN][entity_entry.config_entry_id])
        
        return coordinators

    async def async_handle_turn_auto(call: ServiceCall) -> None:
        """Turn switch to AUTO mode."""
        coordinators = await get_coordinators_for_entities(call.data["entity_id"])
        auto_delay = call.data.get("auto_delay", 0)
        
        for coordinator in coordinators:
            try:
                # Get entity key from entity_id
                for entity_id in call.data["entity_id"]:
                    entity_key = entity_id.split(".")[-1].replace(f"{DOMAIN}_", "").upper()
                    
                    result = await coordinator.device.api.set_switch_state(
                        key=entity_key, 
                        action=ACTION_AUTO, 
                        duration=auto_delay
                    )
                    
                    if result.get("success", True):
                        _LOGGER.info("Switch %s turned to AUTO mode", entity_key)
                    else:
                        _LOGGER.warning("AUTO mode for %s possibly failed: %s", 
                                      entity_key, result.get("response", result))
                
                await coordinator.async_request_refresh()
                
            except VioletPoolAPIError as err:
                _LOGGER.error("Error turning to AUTO mode: %s", err)
                raise HomeAssistantError(f"AUTO mode failed: {err}") from err

    async def async_handle_set_pv_surplus(call: ServiceCall) -> None:
        """Set PV surplus mode."""
        coordinators = await get_coordinators_for_entities(call.data["entity_id"])
        pump_speed = call.data.get("pump_speed", 2)
        
        for coordinator in coordinators:
            try:
                result = await coordinator.device.api.set_pv_surplus(
                    active=True, 
                    pump_speed=pump_speed
                )
                
                if result.get("success", True):
                    _LOGGER.info("PV surplus activated with pump speed %d", pump_speed)
                else:
                    _LOGGER.warning("PV surplus activation possibly failed: %s", 
                                  result.get("response", result))
                
                await coordinator.async_request_refresh()
                
            except VioletPoolAPIError as err:
                _LOGGER.error("Error setting PV surplus: %s", err)
                raise HomeAssistantError(f"PV surplus failed: {err}") from err

    async def async_handle_manual_dosing(call: ServiceCall) -> None:
        """Trigger manual dosing."""
        coordinators = await get_coordinators_for_entities(call.data["entity_id"])
        duration = call.data["duration_seconds"]
        
        for coordinator in coordinators:
            try:
                for entity_id in call.data["entity_id"]:
                    # Determine dosing type from entity_id
                    if "cl" in entity_id.lower() or "chlor" in entity_id.lower():
                        dosing_type = "Chlor"
                    elif "ph_minus" in entity_id.lower() or "phm" in entity_id.lower():
                        dosing_type = "pH-"
                    elif "ph_plus" in entity_id.lower() or "php" in entity_id.lower():
                        dosing_type = "pH+"
                    elif "floc" in entity_id.lower():
                        dosing_type = "Flockmittel"
                    else:
                        _LOGGER.warning("Could not determine dosing type for %s", entity_id)
                        continue
                    
                    result = await coordinator.device.api.manual_dosing(dosing_type, duration)
                    
                    if result.get("success", True):
                        _LOGGER.info("Manual dosing %s started for %d seconds", dosing_type, duration)
                    else:
                        _LOGGER.warning("Manual dosing %s possibly failed: %s", 
                                      dosing_type, result.get("response", result))
                
                await coordinator.async_request_refresh()
                
            except VioletPoolAPIError as err:
                _LOGGER.error("Error with manual dosing: %s", err)
                raise HomeAssistantError(f"Manual dosing failed: {err}") from err

    # Register enhanced services
    hass.services.async_register(
        DOMAIN, "turn_auto", 
        async_handle_turn_auto, 
        schema=ENHANCED_SERVICE_SCHEMAS["turn_auto"]
    )
    
    hass.services.async_register(
        DOMAIN, "set_pv_surplus", 
        async_handle_set_pv_surplus, 
        schema=ENHANCED_SERVICE_SCHEMAS["set_pv_surplus"]
    )
    
    hass.services.async_register(
        DOMAIN, "manual_dosing", 
        async_handle_manual_dosing, 
        schema=ENHANCED_SERVICE_SCHEMAS["manual_dosing"]
    )
    
    _LOGGER.info("Enhanced services for %s registered", DOMAIN)
