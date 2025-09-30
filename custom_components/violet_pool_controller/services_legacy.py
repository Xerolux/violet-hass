"""
Violet Pool Controller - Legacy Services
Alte Services für Rückwärtskompatibilität
Optional: Nur laden wenn benötigt
"""
import logging
import asyncio
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, ACTION_AUTO, ACTION_ON, ACTION_OFF
from .api import VioletPoolAPIError

_LOGGER = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

LEGACY_SERVICE_SCHEMAS = {
    "turn_auto": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional("auto_delay", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=86400)),
        vol.Optional("last_value", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=3)),
    }),
    
    "set_pv_surplus": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional("pump_speed", default=2): vol.All(vol.Coerce(int), vol.Range(min=1, max=3)),
        vol.Optional("active", default=True): cv.boolean,
    }),
    
    "manual_dosing": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("duration_seconds"): vol.All(vol.Coerce(int), vol.Range(min=1, max=3600)),
        vol.Optional("dosing_type"): vol.In(["pH-", "pH+", "Chlor", "Flockmittel"]),
    }),
    
    "set_extension_timer": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("duration"): vol.All(vol.Coerce(int), vol.Range(min=60, max=86400)),
        vol.Optional("auto_off", default=True): cv.boolean,
    }),
    
    "force_device_off": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional("lock_duration", default=600): vol.All(vol.Coerce(int), vol.Range(min=60, max=3600)),
    }),
}

# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

class VioletLegacyServiceHandlers:
    """Handler für Legacy Services."""
    
    def __init__(self, service_manager):
        self.manager = service_manager
        self.hass = service_manager.hass
    
    async def handle_turn_auto(self, call: ServiceCall) -> None:
        """Legacy: Gerät auf AUTO setzen."""
        coordinators = await self.manager.get_coordinators_for_entities(call.data[ATTR_ENTITY_ID])
        auto_delay = call.data.get("auto_delay", 0)
        last_value = call.data.get("last_value", 0)
        
        for coordinator in coordinators:
            for entity_id in call.data[ATTR_ENTITY_ID]:
                device_key = self.manager.extract_device_key(entity_id)
                
                try:
                    result = await coordinator.device.api.set_switch_state(
                        key=device_key, 
                        action=ACTION_AUTO, 
                        duration=auto_delay,
                        last_value=last_value
                    )
                    
                    if result.get("success", True):
                        _LOGGER.info("%s → AUTO", device_key)
                        
                except VioletPoolAPIError as err:
                    _LOGGER.error("Legacy AUTO-Fehler: %s", err)
                    raise HomeAssistantError(f"AUTO fehlgeschlagen: {err}") from err
            
            await coordinator.async_request_refresh()
    
    async def handle_set_pv_surplus(self, call: ServiceCall) -> None:
        """Legacy: PV-Überschuss setzen."""
        coordinators = await self.manager.get_coordinators_for_entities(call.data[ATTR_ENTITY_ID])
        pump_speed = call.data.get("pump_speed", 2)
        active = call.data.get("active", True)
        
        for coordinator in coordinators:
            try:
                result = await coordinator.device.api.set_pv_surplus(
                    active=active, 
                    pump_speed=pump_speed
                )
                
                if result.get("success", True):
                    status = "aktiviert" if active else "deaktiviert"
                    _LOGGER.info("PV-Überschuss %s (Speed %d)", status, pump_speed)
                    
            except VioletPoolAPIError as err:
                _LOGGER.error("Legacy PV-Fehler: %s", err)
                raise HomeAssistantError(f"PV fehlgeschlagen: {err}") from err
            
            await coordinator.async_request_refresh()
    
    async def handle_manual_dosing(self, call: ServiceCall) -> None:
        """Legacy: Manuelle Dosierung."""
        coordinators = await self.manager.get_coordinators_for_entities(call.data[ATTR_ENTITY_ID])
        duration = call.data["duration_seconds"]
        dosing_type = call.data.get("dosing_type")
        
        for coordinator in coordinators:
            for entity_id in call.data[ATTR_ENTITY_ID]:
                if not dosing_type:
                    # Auto-detect
                    if "cl" in entity_id.lower():
                        dosing_type = "Chlor"
                    elif "ph_minus" in entity_id.lower():
                        dosing_type = "pH-"
                    elif "ph_plus" in entity_id.lower():
                        dosing_type = "pH+"
                    elif "floc" in entity_id.lower():
                        dosing_type = "Flockmittel"
                
                try:
                    result = await coordinator.device.api.manual_dosing(dosing_type, duration)
                    
                    if result.get("success", True):
                        _LOGGER.info("Dosierung %s: %ds", dosing_type, duration)
                        
                except VioletPoolAPIError as err:
                    _LOGGER.error("Legacy Dosier-Fehler: %s", err)
                    raise HomeAssistantError(f"Dosierung fehlgeschlagen: {err}") from err
            
            await coordinator.async_request_refresh()
    
    async def handle_set_extension_timer(self, call: ServiceCall) -> None:
        """Legacy: Extension Timer setzen."""
        coordinators = await self.manager.get_coordinators_for_entities(call.data[ATTR_ENTITY_ID])
        duration = call.data["duration"]
        auto_off = call.data.get("auto_off", True)
        
        for coordinator in coordinators:
            for entity_id in call.data[ATTR_ENTITY_ID]:
                device_key = self.manager.extract_device_key(entity_id)
                
                try:
                    if auto_off:
                        result = await coordinator.device.api.set_switch_state(
                            key=device_key, action=ACTION_ON, duration=duration
                        )
                    else:
                        result = await coordinator.device.api.set_switch_state(
                            key=device_key, action=ACTION_ON
                        )
                    
                    if result.get("success", True):
                        _LOGGER.info("Timer %s: %ds", device_key, duration)
                        
                except VioletPoolAPIError as err:
                    _LOGGER.error("Legacy Timer-Fehler: %s", err)
                    raise HomeAssistantError(f"Timer fehlgeschlagen: {err}") from err
            
            await coordinator.async_request_refresh()
    
    async def handle_force_device_off(self, call: ServiceCall) -> None:
        """Legacy: Gerät forciert ausschalten."""
        coordinators = await self.manager.get_coordinators_for_entities(call.data[ATTR_ENTITY_ID])
        lock_duration = call.data.get("lock_duration", 600)
        
        for coordinator in coordinators:
            for entity_id in call.data[ATTR_ENTITY_ID]:
                device_key = self.manager.extract_device_key(entity_id)
                
                try:
                    result = await coordinator.device.api.set_switch_state(
                        key=device_key, action=ACTION_OFF, duration=lock_duration
                    )
                    
                    if result.get("success", True):
                        _LOGGER.info("%s forciert AUS (%ds)", device_key, lock_duration)
                        self.manager.set_safety_lock(device_key, lock_duration)
                        
                except VioletPoolAPIError as err:
                    _LOGGER.error("Legacy Force-Off-Fehler: %s", err)
                    raise HomeAssistantError(f"Force-Off fehlgeschlagen: {err}") from err
            
            await coordinator.async_request_refresh()


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════

async def async_register_legacy_services(hass: HomeAssistant, service_manager) -> None:
    """Registriere Legacy Services."""
    
    handlers = VioletLegacyServiceHandlers(service_manager)
    
    legacy_services = {
        "turn_auto": handlers.handle_turn_auto,
        "set_pv_surplus": handlers.handle_set_pv_surplus,
        "manual_dosing": handlers.handle_manual_dosing,
        "set_extension_timer": handlers.handle_set_extension_timer,
        "force_device_off": handlers.handle_force_device_off,
    }
    
    for service_name, handler in legacy_services.items():
        hass.services.async_register(
            DOMAIN, 
            service_name, 
            handler,
            schema=LEGACY_SERVICE_SCHEMAS[service_name]
        )
    
    _LOGGER.info("Legacy Services registriert (%d Services)", len(legacy_services))
