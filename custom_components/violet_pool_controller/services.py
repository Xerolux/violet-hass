"""
Violet Pool Controller - Core Services
Schlanke Kern-Services für die wichtigsten Pool-Funktionen
"""
import logging
import asyncio
from typing import Set, Optional, List
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_registry, device_registry
from homeassistant.exceptions import HomeAssistantError
from homeassistant.const import ATTR_ENTITY_ID

from .const import (
    DOMAIN, 
    ACTION_AUTO, 
    ACTION_ON, 
    ACTION_OFF, 
    ACTION_MAN,
    get_device_state_info, 
    SWITCH_FUNCTIONS
)
from .api import VioletPoolAPIError
from .device import VioletPoolDataUpdateCoordinator
from .services_utils import (
    ENTITY_DEVICE_MAPPING, 
    DOSING_TYPE_MAPPING,
    CORE_SERVICE_SCHEMAS, 
    validate_dosing_safety
)

_LOGGER = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════
# CORE SERVICE MANAGER
# ════════════════════════════════════════════════════════════════════════════

class VioletServiceManager:
    """Zentraler Service Manager für Pool-Steuerung."""
    
    def __init__(self, hass: HomeAssistant):
        """
        Initialisiere Service Manager.
        
        Args:
            hass: Home Assistant Instanz
        """
        self.hass = hass
        self._safety_locks: dict[str, datetime] = {}
        _LOGGER.debug("Service Manager initialisiert")
    
    async def get_coordinators_for_entities(
        self, 
        entity_ids: List[str]
    ) -> Set[VioletPoolDataUpdateCoordinator]:
        """
        Holt Coordinators für Entity IDs.
        
        Args:
            entity_ids: Liste von Entity IDs
            
        Returns:
            Set von Coordinators
        """
        registry = entity_registry.async_get(self.hass)
        coordinators = set()
        
        for entity_id in entity_ids:
            entity_entry = registry.async_get(entity_id)
            if not entity_entry:
                _LOGGER.warning("Entity nicht gefunden: %s", entity_id)
                continue
            
            if entity_entry.config_entry_id not in self.hass.data.get(DOMAIN, {}):
                _LOGGER.warning(
                    "Config Entry nicht gefunden für Entity: %s",
                    entity_id
                )
                continue
            
            coordinator = self.hass.data[DOMAIN][entity_entry.config_entry_id]
            if isinstance(coordinator, VioletPoolDataUpdateCoordinator):
                coordinators.add(coordinator)
                _LOGGER.debug(
                    "Coordinator gefunden für Entity %s",
                    entity_id
                )
        
        _LOGGER.debug(
            "%d Coordinator(s) für %d Entity(s) gefunden",
            len(coordinators),
            len(entity_ids)
        )
        
        return coordinators
    
    async def get_coordinator_for_device(
        self, 
        device_id: str
    ) -> Optional[VioletPoolDataUpdateCoordinator]:
        """
        Holt Coordinator für Device ID.
        
        Args:
            device_id: Device ID
            
        Returns:
            Coordinator oder None
        """
        device_reg = device_registry.async_get(self.hass)
        device_entry = device_reg.async_get(device_id)
        
        if not device_entry:
            _LOGGER.warning("Device nicht gefunden: %s", device_id)
            return None
        
        for config_entry_id in device_entry.config_entries:
            if config_entry_id in self.hass.data.get(DOMAIN, {}):
                coordinator = self.hass.data[DOMAIN][config_entry_id]
                if isinstance(coordinator, VioletPoolDataUpdateCoordinator):
                    _LOGGER.debug(
                        "Coordinator für Device %s gefunden",
                        device_id
                    )
                    return coordinator
        
        _LOGGER.warning("Kein Coordinator für Device %s gefunden", device_id)
        return None
    
    def extract_device_key(self, entity_id: str) -> str:
        """
        Extrahiert Device-Key aus Entity ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Device Key (z.B. "PUMP", "HEATER")
        """
        entity_name = entity_id.split(".")[-1]
        if entity_name.startswith(f"{DOMAIN}_"):
            entity_name = entity_name[len(f"{DOMAIN}_"):]
        
        # Suche in Mapping
        for key, device_key in ENTITY_DEVICE_MAPPING.items():
            if key in entity_name.lower():
                _LOGGER.debug(
                    "Device-Key für %s: %s",
                    entity_id,
                    device_key
                )
                return device_key
        
        # Fallback: Großbuchstaben des Entity-Namens
        device_key = entity_name.upper()
        _LOGGER.debug(
            "Device-Key (Fallback) für %s: %s",
            entity_id,
            device_key
        )
        return device_key
    
    def check_safety_lock(self, device_key: str) -> bool:
        """
        Prüft ob Safety-Lock aktiv ist.
        
        Args:
            device_key: Device Key
            
        Returns:
            True wenn Lock aktiv
        """
        if device_key in self._safety_locks:
            if datetime.now() < self._safety_locks[device_key]:
                remaining = self.get_remaining_lock_time(device_key)
                _LOGGER.debug(
                    "Safety-Lock aktiv für %s (noch %ds)",
                    device_key,
                    remaining
                )
                return True
            
            # Lock abgelaufen, entfernen
            del self._safety_locks[device_key]
            _LOGGER.debug("Safety-Lock für %s abgelaufen", device_key)
        
        return False
    
    def set_safety_lock(self, device_key: str, duration_seconds: int) -> None:
        """
        Setzt Safety-Lock.
        
        Args:
            device_key: Device Key
            duration_seconds: Dauer in Sekunden
        """
        self._safety_locks[device_key] = datetime.now() + timedelta(
            seconds=duration_seconds
        )
        _LOGGER.info(
            "Safety-Lock gesetzt für %s: %ds",
            device_key,
            duration_seconds
        )
    
    def get_remaining_lock_time(self, device_key: str) -> int:
        """
        Verbleibende Lock-Zeit in Sekunden.
        
        Args:
            device_key: Device Key
            
        Returns:
            Verbleibende Sekunden
        """
        if device_key in self._safety_locks:
            remaining = (
                self._safety_locks[device_key] - datetime.now()
            ).total_seconds()
            return max(0, int(remaining))
        return 0


# ════════════════════════════════════════════════════════════════════════════
# CORE SERVICE HANDLERS
# ════════════════════════════════════════════════════════════════════════════

class VioletCoreServiceHandlers:
    """Handler für die wichtigsten Pool-Services."""
    
    def __init__(self, service_manager: VioletServiceManager):
        """
        Initialisiere Service Handlers.
        
        Args:
            service_manager: Service Manager Instanz
        """
        self.manager = service_manager
        self.hass = service_manager.hass
        _LOGGER.debug("Service Handlers initialisiert")
    
    async def handle_set_device_mode(self, call: ServiceCall) -> None:
        """
        Hauptservice: Gerät auf Auto/On/Off/ForceOff setzen.
        
        Ersetzt die meisten anderen Services.
        
        Args:
            call: Service Call mit entity_id, mode, duration, etc.
        """
        entity_ids = call.data[ATTR_ENTITY_ID]
        mode = call.data["mode"]
        duration = call.data.get("duration", 0)
        speed = call.data.get("speed", 2)
        restore_after = call.data.get("restore_after", 0)
        
        _LOGGER.info(
            "Service 'set_device_mode' aufgerufen: Mode=%s, Duration=%d, Speed=%d",
            mode,
            duration,
            speed
        )
        
        coordinators = await self.manager.get_coordinators_for_entities(entity_ids)
        if not coordinators:
            raise HomeAssistantError("Keine Coordinators gefunden")
        
        action_map = {
            "auto": ACTION_AUTO,
            "manual_on": ACTION_ON,
            "manual_off": ACTION_OFF,
            "force_off": ACTION_OFF
        }
        
        for coordinator in coordinators:
            for entity_id in entity_ids:
                device_key = self.manager.extract_device_key(entity_id)
                
                # Prüfe Safety-Lock
                if self.manager.check_safety_lock(device_key):
                    remaining = self.manager.get_remaining_lock_time(device_key)
                    _LOGGER.warning(
                        "%s ist gelockt (noch %ds)",
                        device_key,
                        remaining
                    )
                    continue
                
                try:
                    action = action_map[mode]
                    params = {"key": device_key, "action": action}
                    
                    if duration > 0:
                        params["duration"] = duration
                    
                    if device_key == "PUMP" and action == ACTION_ON:
                        params["last_value"] = speed
                    
                    _LOGGER.debug(
                        "Sende Befehl an %s: %s (Params: %s)",
                        device_key,
                        action,
                        params
                    )
                    
                    result = await coordinator.device.api.set_switch_state(**params)
                    
                    if result.get("success", True):
                        _LOGGER.info(
                            "%s → %s erfolgreich",
                            device_key,
                            mode
                        )
                        
                        # Safety-Lock bei force_off
                        if mode == "force_off":
                            self.manager.set_safety_lock(
                                device_key,
                                duration or 600
                            )
                        
                        # Auto-Restore nach Zeit
                        if restore_after > 0:
                            asyncio.create_task(
                                self._restore_mode(
                                    coordinator,
                                    device_key,
                                    restore_after
                                )
                            )
                    else:
                        _LOGGER.warning(
                            "%s → %s möglicherweise fehlgeschlagen: %s",
                            device_key,
                            mode,
                            result
                        )
                    
                except VioletPoolAPIError as err:
                    _LOGGER.error(
                        "API-Fehler bei %s: %s",
                        device_key,
                        err
                    )
                    raise HomeAssistantError(f"Fehler: {err}") from err
            
            # Daten aktualisieren
            await coordinator.async_request_refresh()
    
    async def _restore_mode(
        self, 
        coordinator: VioletPoolDataUpdateCoordinator, 
        device_key: str, 
        delay: int
    ) -> None:
        """
        Stellt Modus nach Verzögerung wieder her.
        
        Args:
            coordinator: Coordinator
            device_key: Device Key
            delay: Verzögerung in Sekunden
        """
        _LOGGER.info(
            "Auto-Restore geplant für %s in %ds",
            device_key,
            delay
        )
        
        await asyncio.sleep(delay)
        
        try:
            await coordinator.device.api.set_switch_state(
                key=device_key,
                action=ACTION_AUTO
            )
            _LOGGER.info(
                "%s → AUTO wiederhergestellt (nach %ds)",
                device_key,
                delay
            )
            await coordinator.async_request_refresh()
            
        except Exception as err:
            _LOGGER.error(
                "Restore-Fehler für %s: %s",
                device_key,
                err
            )
    
    async def handle_control_pump(self, call: ServiceCall) -> None:
        """
        Pumpensteuerung mit Geschwindigkeit.
        
        Args:
            call: Service Call mit action, speed, duration
        """
        coordinators = await self.manager.get_coordinators_for_entities(
            call.data[ATTR_ENTITY_ID]
        )
        action = call.data["action"]
        speed = call.data.get("speed", 2)
        duration = call.data.get("duration", 0)
        
        _LOGGER.info(
            "Service 'control_pump' aufgerufen: Action=%s, Speed=%d, Duration=%d",
            action,
            speed,
            duration
        )
        
        for coordinator in coordinators:
            try:
                if action == "speed_control":
                    result = await coordinator.device.api.set_switch_state(
                        key="PUMP",
                        action=ACTION_ON,
                        duration=duration,
                        last_value=speed
                    )
                elif action == "force_off":
                    result = await coordinator.device.api.set_switch_state(
                        key="PUMP",
                        action=ACTION_OFF,
                        duration=600
                    )
                    self.manager.set_safety_lock("PUMP", 600)
                elif action == "eco_mode":
                    result = await coordinator.device.api.set_switch_state(
                        key="PUMP",
                        action=ACTION_ON,
                        duration=duration,
                        last_value=1
                    )
                elif action == "boost_mode":
                    result = await coordinator.device.api.set_switch_state(
                        key="PUMP",
                        action=ACTION_ON,
                        duration=duration or 3600,
                        last_value=3
                    )
                elif action == "auto":
                    result = await coordinator.device.api.set_switch_state(
                        key="PUMP",
                        action=ACTION_AUTO
                    )
                
                if result.get("success", True):
                    _LOGGER.info(
                        "Pumpe: %s (Speed %d) erfolgreich",
                        action,
                        speed
                    )
                
                await coordinator.async_request_refresh()
                
            except VioletPoolAPIError as err:
                _LOGGER.error("Pumpen-Fehler: %s", err)
                raise HomeAssistantError(f"Pumpe: {err}") from err
    
    async def handle_smart_dosing(self, call: ServiceCall) -> None:
        """
        Intelligente Dosierung mit Safety-Checks.
        
        Args:
            call: Service Call mit dosing_type, action, duration
        """
        coordinators = await self.manager.get_coordinators_for_entities(
            call.data[ATTR_ENTITY_ID]
        )
        dosing_type = call.data["dosing_type"]
        action = call.data["action"]
        duration = call.data.get("duration", 30)
        safety_override = call.data.get("safety_override", False)
        
        _LOGGER.info(
            "Service 'smart_dosing' aufgerufen: Type=%s, Action=%s, Duration=%d",
            dosing_type,
            action,
            duration
        )
        
        device_key = DOSING_TYPE_MAPPING.get(dosing_type)
        if not device_key:
            raise HomeAssistantError(f"Unbekannter Dosiertyp: {dosing_type}")
        
        for coordinator in coordinators:
            try:
                # Safety-Check (wenn nicht überschrieben)
                if not safety_override:
                    safety_check = await validate_dosing_safety(
                        coordinator,
                        device_key,
                        duration,
                        self.manager
                    )
                    if not safety_check["valid"]:
                        raise HomeAssistantError(
                            f"Safety-Check fehlgeschlagen: {safety_check['error']}"
                        )
                
                # Aktion ausführen
                if action == "manual_dose":
                    result = await coordinator.device.api.set_switch_state(
                        key=device_key,
                        action=ACTION_MAN,
                        duration=duration
                    )
                    if not safety_override:
                        self.manager.set_safety_lock(device_key, 300)
                        
                elif action == "auto":
                    result = await coordinator.device.api.set_switch_state(
                        key=device_key,
                        action=ACTION_AUTO
                    )
                elif action == "stop":
                    result = await coordinator.device.api.set_switch_state(
                        key=device_key,
                        action=ACTION_OFF
                    )
                
                if result.get("success", True):
                    _LOGGER.info(
                        "Dosierung %s: %s (%ds) erfolgreich",
                        dosing_type,
                        action,
                        duration
                    )
                
                await coordinator.async_request_refresh()
                
            except VioletPoolAPIError as err:
                _LOGGER.error("Dosier-Fehler: %s", err)
                raise HomeAssistantError(f"Dosierung: {err}") from err
    
    async def handle_manage_pv_surplus(self, call: ServiceCall) -> None:
        """
        PV-Überschuss Management.
        
        Args:
            call: Service Call mit mode, pump_speed
        """
        coordinators = await self.manager.get_coordinators_for_entities(
            call.data[ATTR_ENTITY_ID]
        )
        mode = call.data["mode"]
        pump_speed = call.data.get("pump_speed", 2)
        
        _LOGGER.info(
            "Service 'manage_pv_surplus' aufgerufen: Mode=%s, Speed=%d",
            mode,
            pump_speed
        )
        
        for coordinator in coordinators:
            try:
                if mode == "activate":
                    result = await coordinator.device.api.set_pv_surplus(
                        active=True,
                        pump_speed=pump_speed
                    )
                elif mode == "deactivate":
                    result = await coordinator.device.api.set_pv_surplus(
                        active=False
                    )
                elif mode == "auto":
                    result = await coordinator.device.api.set_switch_state(
                        key="PVSURPLUS",
                        action=ACTION_AUTO
                    )
                
                if result.get("success", True):
                    _LOGGER.info(
                        "PV-Überschuss: %s (Speed %d) erfolgreich",
                        mode,
                        pump_speed
                    )
                
                await coordinator.async_request_refresh()
                
            except VioletPoolAPIError as err:
                _LOGGER.error("PV-Fehler: %s", err)
                raise HomeAssistantError(f"PV: {err}") from err


# ════════════════════════════════════════════════════════════════════════════
# SERVICE REGISTRATION
# ════════════════════════════════════════════════════════════════════════════

async def async_register_services(hass: HomeAssistant) -> None:
    """
    Registriert Core Services + optional Legacy/Smart.
    
    Args:
        hass: Home Assistant Instanz
    """
    if hass.services.has_service(DOMAIN, "set_device_mode"):
        _LOGGER.debug("Services bereits registriert")
        return
    
    try:
        # Core Services initialisieren
        service_manager = VioletServiceManager(hass)
        handlers = VioletCoreServiceHandlers(service_manager)
        
        # Core Services registrieren
        hass.services.async_register(
            DOMAIN,
            "set_device_mode", 
            handlers.handle_set_device_mode,
            schema=CORE_SERVICE_SCHEMAS["set_device_mode"]
        )
        
        hass.services.async_register(
            DOMAIN,
            "control_pump",
            handlers.handle_control_pump,
            schema=CORE_SERVICE_SCHEMAS["control_pump"]
        )
        
        hass.services.async_register(
            DOMAIN,
            "smart_dosing",
            handlers.handle_smart_dosing,
            schema=CORE_SERVICE_SCHEMAS["smart_dosing"]
        )
        
        hass.services.async_register(
            DOMAIN,
            "manage_pv_surplus",
            handlers.handle_manage_pv_surplus,
            schema=CORE_SERVICE_SCHEMAS["manage_pv_surplus"]
        )
        
        _LOGGER.info("✅ Core Services registriert (4 Services)")
        
        # Optional: Legacy Services laden
        try:
            from .services_legacy import async_register_legacy_services
            await async_register_legacy_services(hass, service_manager)
            _LOGGER.info("✅ Legacy Services geladen")
        except ImportError:
            _LOGGER.debug("Legacy Services nicht verfügbar")
        
        # Optional: Smart Services laden
        try:
            from .services_smart import async_register_smart_services
            await async_register_smart_services(hass, service_manager)
            _LOGGER.info("✅ Smart Services geladen")
        except ImportError:
            _LOGGER.debug("Smart Services nicht verfügbar")
        
        # Optional: DMX & Cover Services laden
        try:
            from .services_dmx_cover import async_register_dmx_cover_services
            await async_register_dmx_cover_services(hass, service_manager)
            _LOGGER.info("✅ DMX & Cover Services geladen")
        except ImportError:
            _LOGGER.debug("DMX & Cover Services nicht verfügbar")
        
    except Exception as err:
        _LOGGER.exception("Service-Registrierung fehlgeschlagen: %s", err)
        raise


async def async_unregister_services(hass: HomeAssistant) -> None:
    """
    Entfernt alle Services.
    
    Args:
        hass: Home Assistant Instanz
    """
    services = [
        "set_device_mode",
        "control_pump",
        "smart_dosing",
        "manage_pv_surplus"
    ]
    
    for service_name in services:
        if hass.services.has_service(DOMAIN, service_name):
            hass.services.async_remove(DOMAIN, service_name)
            _LOGGER.debug("Service '%s' entfernt", service_name)
    
    _LOGGER.info("Services entfernt")