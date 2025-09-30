"""
Violet Pool Controller - Smart Services
AI-gesteuerte Pool-Optimierung und intelligente Automatisierung
Optional: Nur laden wenn erweiterte Features benötigt werden
"""
import logging
import asyncio
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.exceptions import HomeAssistantError
from typing import Dict, List
from datetime import datetime

from .const import DOMAIN, ACTION_AUTO, ACTION_ON, ACTION_OFF, ACTION_MAN
from .api import VioletPoolAPIError
from .services_utils import get_dosing_type_from_key

_LOGGER = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# PROFILE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

CHEMICAL_PROFILES = {
    "optimal": {"pH": 7.2, "orp": 700, "chlorine": 1.0},
    "sensitive_skin": {"pH": 7.1, "orp": 680, "chlorine": 0.6},
    "high_usage": {"pH": 7.3, "orp": 750, "chlorine": 1.5},
    "minimal_chemicals": {"pH": 7.2, "orp": 650, "chlorine": 0.4}
}

# ═══════════════════════════════════════════════════════════════════════════════
# SMART SERVICE SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

SMART_SERVICE_SCHEMAS = {
    "smart_pool_optimization": vol.Schema({
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required("optimization_mode"): vol.In(["energy_saving", "water_quality", "balanced", "custom"]),
        vol.Optional("duration_hours", default=24): vol.All(vol.Coerce(int), vol.Range(min=1, max=168)),
        vol.Optional("weather_integration", default=True): cv.boolean,
    }),
    
    "adaptive_chemical_balancing": vol.Schema({
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required("target_profile"): vol.In(["optimal", "sensitive_skin", "high_usage", "minimal_chemicals"]),
        vol.Optional("adjustment_speed"): vol.In(["conservative", "normal", "aggressive"]),
        vol.Optional("monitoring_duration", default=72): vol.All(vol.Coerce(int), vol.Range(min=6, max=168)),
    }),
    
    "seasonal_pool_preparation": vol.Schema({
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required("season_mode"): vol.In(["spring_startup", "summer_maintenance", "autumn_preparation", "winter_shutdown"]),
        vol.Optional("schedule_execution", default=True): cv.boolean,
    }),
}

# ═══════════════════════════════════════════════════════════════════════════════
# SMART HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

class VioletSmartServiceHandlers:
    """Handler für Smart/AI Services."""
    
    def __init__(self, service_manager):
        self.manager = service_manager
        self.hass = service_manager.hass
    
    async def handle_smart_pool_optimization(self, call: ServiceCall) -> None:
        """
        Intelligente Pool-Optimierung basierend auf Modus.
        Steuert alle Geräte koordiniert für optimale Performance.
        """
        device_id = call.data["device_id"]
        optimization_mode = call.data["optimization_mode"]
        duration_hours = call.data.get("duration_hours", 24)
        
        coordinator = await self.manager.get_coordinator_for_device(device_id)
        if not coordinator:
            raise HomeAssistantError(f"Gerät nicht gefunden: {device_id}")
        
        try:
            # Optimierungsplan generieren
            plan = self._generate_optimization_plan(
                coordinator.data, 
                optimization_mode
            )
            
            _LOGGER.info("Starte Pool-Optimierung: %s (%d Schritte)", 
                        optimization_mode, len(plan["steps"]))
            
            # Plan ausführen
            for i, step in enumerate(plan["steps"], 1):
                device_key = step["device"]
                action = step["action"]
                params = step.get("params", {})
                
                _LOGGER.debug("Schritt %d/%d: %s → %s", 
                            i, len(plan["steps"]), device_key, action)
                
                # Aktion ausführen
                if device_key == "PUMP":
                    await coordinator.device.api.set_switch_state(
                        key=device_key, 
                        action=action,
                        duration=params.get("duration", 0),
                        last_value=params.get("speed", 2)
                    )
                elif device_key.startswith("DOS_"):
                    if action == ACTION_MAN:
                        dosing_type = get_dosing_type_from_key(device_key)
                        await coordinator.device.api.manual_dosing(
                            dosing_type, 
                            params.get("duration", 30)
                        )
                    else:
                        await coordinator.device.api.set_switch_state(
                            key=device_key, 
                            action=action
                        )
                else:
                    await coordinator.device.api.set_switch_state(
                        key=device_key, 
                        action=action,
                        duration=params.get("duration", 0)
                    )
                
                await asyncio.sleep(2)  # Kurze Pause zwischen Schritten
            
            _LOGGER.info("✅ Pool-Optimierung %s abgeschlossen", optimization_mode)
            await coordinator.async_request_refresh()
            
        except VioletPoolAPIError as err:
            _LOGGER.error("Optimierungs-Fehler: %s", err)
            raise HomeAssistantError(f"Optimierung fehlgeschlagen: {err}") from err
    
    def _generate_optimization_plan(self, data: Dict, mode: str) -> Dict:
        """Generiere intelligenten Optimierungsplan."""
        plan = {"mode": mode, "steps": []}
        
        if mode == "energy_saving":
            # Energie sparen: Langsame Pumpe, Solar bevorzugen
            plan["steps"] = [
                {"device": "PUMP", "action": ACTION_ON, "params": {"speed": 1, "duration": 14400}},  # 4h Eco
                {"device": "SOLAR", "action": ACTION_ON},
                {"device": "HEATER", "action": ACTION_AUTO},
            ]
            
        elif mode == "water_quality":
            # Wasserqualität: Aggressivere Filterung und Chemie
            ph_value = data.get("pH_value", 7.2)
            orp_value = data.get("orp_value", 700)
            
            # pH korrigieren
            if ph_value < 7.0:
                plan["steps"].append({"device": "DOS_5_PHP", "action": ACTION_MAN, "params": {"duration": 30}})
            elif ph_value > 7.4:
                plan["steps"].append({"device": "DOS_4_PHM", "action": ACTION_MAN, "params": {"duration": 30}})
            
            # ORP korrigieren
            if orp_value < 650:
                plan["steps"].append({"device": "DOS_1_CL", "action": ACTION_MAN, "params": {"duration": 60}})
            
            # Pumpe auf Boost
            plan["steps"].extend([
                {"device": "PUMP", "action": ACTION_ON, "params": {"speed": 3, "duration": 7200}},  # 2h Boost
                {"device": "BACKWASH", "action": ACTION_AUTO},
            ])
            
        elif mode == "balanced":
            # Ausgewogen: Normale Betriebsparameter
            plan["steps"] = [
                {"device": "PUMP", "action": ACTION_ON, "params": {"speed": 2, "duration": 10800}},  # 3h Normal
                {"device": "HEATER", "action": ACTION_AUTO},
                {"device": "SOLAR", "action": ACTION_AUTO},
                {"device": "DOS_1_CL", "action": ACTION_AUTO},
                {"device": "DOS_4_PHM", "action": ACTION_AUTO},
                {"device": "DOS_5_PHP", "action": ACTION_AUTO},
            ]
            
        elif mode == "custom":
            # Benutzerdefiniert (könnte erweitert werden)
            plan["steps"] = [
                {"device": "PUMP", "action": ACTION_ON, "params": {"speed": 2}},
                {"device": "HEATER", "action": ACTION_AUTO},
            ]
        
        return plan
    
    async def handle_adaptive_chemical_balancing(self, call: ServiceCall) -> None:
        """
        Adaptive chemische Ausbalancierung.
        Analysiert Ist-Werte und passt Chemie schrittweise an.
        """
        device_id = call.data["device_id"]
        target_profile = call.data["target_profile"]
        adjustment_speed = call.data.get("adjustment_speed", "normal")
        
        coordinator = await self.manager.get_coordinator_for_device(device_id)
        if not coordinator:
            raise HomeAssistantError(f"Gerät nicht gefunden: {device_id}")
        
        try:
            # Zielwerte aus Profil
            target_values = CHEMICAL_PROFILES.get(target_profile, CHEMICAL_PROFILES["optimal"])
            
            # Aktuelle Werte
            current_ph = coordinator.data.get("pH_value", 7.2)
            current_orp = coordinator.data.get("orp_value", 700)
            current_chlorine = coordinator.data.get("pot_value", 1.0)
            
            _LOGGER.info("Chemical Balancing: %s (pH: %.1f → %.1f, ORP: %d → %d)",
                        target_profile, current_ph, target_values["pH"],
                        current_orp, target_values["orp"])
            
            # Anpassungen berechnen
            adjustments = []
            
            # pH-Anpassung
            ph_diff = target_values["pH"] - current_ph
            if abs(ph_diff) > 0.1:
                duration = self._calculate_dosing_duration(ph_diff, adjustment_speed)
                if ph_diff > 0:
                    adjustments.append({
                        "device": "DOS_5_PHP", 
                        "action": ACTION_MAN, 
                        "duration": duration
                    })
                else:
                    adjustments.append({
                        "device": "DOS_4_PHM", 
                        "action": ACTION_MAN, 
                        "duration": duration
                    })
            
            # ORP-Anpassung
            orp_diff = target_values["orp"] - current_orp
            if abs(orp_diff) > 50:
                if orp_diff > 0:
                    duration = self._calculate_dosing_duration(orp_diff / 10, adjustment_speed)
                    adjustments.append({
                        "device": "DOS_1_CL", 
                        "action": ACTION_MAN, 
                        "duration": min(120, duration)
                    })
            
            # Anpassungen ausführen (mit Safety-Checks)
            for adjustment in adjustments:
                device_key = adjustment["device"]
                
                # Safety-Check
                from .services_utils import validate_dosing_safety
                safety_check = await validate_dosing_safety(
                    coordinator, device_key, adjustment["duration"], self.manager
                )
                
                if safety_check["valid"]:
                    await coordinator.device.api.set_switch_state(
                        key=device_key, 
                        action=adjustment["action"], 
                        duration=adjustment["duration"]
                    )
                    _LOGGER.info("Anpassung %s: %ds", device_key, adjustment["duration"])
                    
                    # Safety-Lock setzen
                    self.manager.set_safety_lock(device_key, safety_check["safety_interval"])
                else:
                    _LOGGER.warning("Anpassung übersprungen: %s", safety_check["error"])
                
                await asyncio.sleep(5)
            
            _LOGGER.info("✅ Chemical Balancing abgeschlossen (%d Anpassungen)", len(adjustments))
            await coordinator.async_request_refresh()
            
        except VioletPoolAPIError as err:
            _LOGGER.error("Chemical Balancing Fehler: %s", err)
            raise HomeAssistantError(f"Balancing fehlgeschlagen: {err}") from err
    
    def _calculate_dosing_duration(self, diff: float, speed: str) -> int:
        """Berechne Dosierdauer basierend auf Differenz und Geschwindigkeit."""
        base_duration = abs(diff) * 30
        
        if speed == "conservative":
            return int(min(60, base_duration * 0.7))
        elif speed == "aggressive":
            return int(min(120, base_duration * 1.5))
        else:  # normal
            return int(min(90, base_duration))
    
    async def handle_seasonal_pool_preparation(self, call: ServiceCall) -> None:
        """
        Saisonale Pool-Vorbereitung.
        Führt vordefinierte Sequenzen für verschiedene Jahreszeiten aus.
        """
        device_id = call.data["device_id"]
        season_mode = call.data["season_mode"]
        schedule_execution = call.data.get("schedule_execution", True)
        
        coordinator = await self.manager.get_coordinator_for_device(device_id)
        if not coordinator:
            raise HomeAssistantError(f"Gerät nicht gefunden: {device_id}")
        
        # Saisonale Sequenzen
        seasonal_sequences = {
            "spring_startup": [
                {"device": "PUMP", "action": ACTION_ON, "params": {"speed": 3, "duration": 7200}},  # 2h Vollreinigung
                {"device": "BACKWASH", "action": ACTION_ON, "params": {"duration": 300}},  # 5min Rückspülung
                {"device": "DOS_1_CL", "action": ACTION_MAN, "params": {"duration": 120}},  # Initial-Chlorung
                {"device": "HEATER", "action": ACTION_AUTO},
                {"device": "SOLAR", "action": ACTION_AUTO},
            ],
            
            "summer_maintenance": [
                {"device": "PUMP", "action": ACTION_ON, "params": {"speed": 2, "duration": 14400}},  # 4h täglich
                {"device": "DOS_1_CL", "action": ACTION_AUTO},
                {"device": "DOS_4_PHM", "action": ACTION_AUTO},
                {"device": "DOS_5_PHP", "action": ACTION_AUTO},
                {"device": "SOLAR", "action": ACTION_ON},
            ],
            
            "autumn_preparation": [
                {"device": "PUMP", "action": ACTION_ON, "params": {"speed": 1, "duration": 10800}},  # 3h reduziert
                {"device": "HEATER", "action": ACTION_AUTO},
                {"device": "SOLAR", "action": ACTION_OFF},
                {"device": "DOS_6_FLOC", "action": ACTION_MAN, "params": {"duration": 180}},  # Flockung
            ],
            
            "winter_shutdown": [
                {"device": "PUMP", "action": ACTION_OFF, "params": {"duration": 86400}},
                {"device": "HEATER", "action": ACTION_OFF, "params": {"duration": 86400}},
                {"device": "SOLAR", "action": ACTION_OFF, "params": {"duration": 86400}},
                {"device": "DOS_1_CL", "action": ACTION_OFF, "params": {"duration": 86400}},
            ]
        }
        
        sequence = seasonal_sequences.get(season_mode, [])
        
        try:
            if schedule_execution:
                _LOGGER.info("Starte saisonale Vorbereitung: %s (%d Schritte)", 
                            season_mode, len(sequence))
                
                for i, step in enumerate(sequence, 1):
                    device_key = step["device"]
                    action = step["action"]
                    params = step.get("params", {})
                    
                    _LOGGER.debug("Saison-Schritt %d/%d: %s", i, len(sequence), device_key)
                    
                    if device_key in coordinator.data:
                        await coordinator.device.api.set_switch_state(
                            key=device_key,
                            action=action,
                            duration=params.get("duration", 0),
                            last_value=params.get("speed", 0)
                        )
                    
                    await asyncio.sleep(5)
                
                _LOGGER.info("✅ Saisonale Vorbereitung %s abgeschlossen", season_mode)
            
            await coordinator.async_request_refresh()
            
        except VioletPoolAPIError as err:
            _LOGGER.error("Saison-Vorbereitung Fehler: %s", err)
            raise HomeAssistantError(f"Vorbereitung fehlgeschlagen: {err}") from err


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════

async def async_register_smart_services(hass: HomeAssistant, service_manager) -> None:
    """Registriere Smart Services."""
    
    handlers = VioletSmartServiceHandlers(service_manager)
    
    smart_services = {
        "smart_pool_optimization": handlers.handle_smart_pool_optimization,
        "adaptive_chemical_balancing": handlers.handle_adaptive_chemical_balancing,
        "seasonal_pool_preparation": handlers.handle_seasonal_pool_preparation,
    }
    
    for service_name, handler in smart_services.items():
        hass.services.async_register(
            DOMAIN,
            service_name,
            handler,
            schema=SMART_SERVICE_SCHEMAS[service_name]
        )
    
    _LOGGER.info("Smart Services registriert (%d Services)", len(smart_services))
