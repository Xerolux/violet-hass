"""
Violet Pool Controller - DMX & Cover Spezial-Services
Erweiterte Steuerung für Beleuchtung, Szenen und Cover-Funktionen
Optional: Nur laden wenn DMX/Cover Features benötigt werden
"""
import logging
import asyncio
import random
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import ATTR_ENTITY_ID, ATTR_DEVICE_ID
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN, ACTION_AUTO, ACTION_ON, ACTION_OFF,
    ACTION_ALLON, ACTION_ALLOFF, ACTION_ALLAUTO
)
from .api import VioletPoolAPIError

_LOGGER = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# DMX & COVER SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

DMX_COVER_SERVICE_SCHEMAS = {
    # DMX Szenen-Steuerung
    "control_dmx_scenes": vol.Schema({
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required("action"): vol.In([
            "all_on", "all_off", "all_auto", 
            "sequence", "random", "party_mode"
        ]),
        vol.Optional("scene_selection"): vol.All(
            cv.ensure_list, 
            [vol.In([f"DMX_SCENE{i}" for i in range(1, 13)])]
        ),
        vol.Optional("sequence_delay", default=2): vol.All(
            vol.Coerce(int), 
            vol.Range(min=1, max=60)
        ),
    }),
    
    # Legacy Light Pulse
    "set_light_color_pulse": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional("pulse_count", default=1): vol.All(
            vol.Coerce(int), 
            vol.Range(min=1, max=10)
        ),
        vol.Optional("pulse_interval", default=500): vol.All(
            vol.Coerce(int), 
            vol.Range(min=100, max=2000)
        ),
    }),
    
    # Digital Input Regeln (für Cover/Automation)
    "manage_digital_rules": vol.Schema({
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required("rule_key"): vol.In([f"DIRULE_{i}" for i in range(1, 8)]),
        vol.Required("action"): vol.In(["trigger", "lock", "unlock", "disable"]),
        vol.Optional("delay", default=0): vol.All(
            vol.Coerce(int), 
            vol.Range(min=0, max=3600)
        ),
    }),
    
    # Extension Relay (oft für DMX/Cover genutzt)
    "control_extension_relay": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("action"): vol.In(["timer_on", "timer_off", "pulse"]),
        vol.Optional("duration", default=3600): vol.All(
            vol.Coerce(int), 
            vol.Range(min=60, max=86400)
        ),
        vol.Optional("pulse_duration", default=1): vol.All(
            vol.Coerce(int), 
            vol.Range(min=1, max=60)
        ),
        vol.Optional("repeat_count", default=1): vol.All(
            vol.Coerce(int), 
            vol.Range(min=1, max=10)
        ),
    }),
}

# ═══════════════════════════════════════════════════════════════════════════════
# DMX & COVER HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

class VioletDmxCoverServiceHandlers:
    """Handler für DMX- und Cover-Spezial-Services."""
    
    def __init__(self, service_manager):
        self.manager = service_manager
        self.hass = service_manager.hass
    
    async def handle_control_dmx_scenes(self, call: ServiceCall) -> None:
        """
        Erweiterte DMX-Szenensteuerung.
        Steuert alle Szenen koordiniert oder in Sequenzen.
        """
        device_id = call.data["device_id"]
        action = call.data["action"]
        scene_selection = call.data.get("scene_selection", [])
        sequence_delay = call.data.get("sequence_delay", 2)
        
        coordinator = await self.manager.get_coordinator_for_device(device_id)
        if not coordinator:
            raise HomeAssistantError(f"Gerät nicht gefunden: {device_id}")
        
        try:
            if action == "all_on":
                # Alle Szenen einschalten
                result = await coordinator.device.api.set_all_dmx_scenes(ACTION_ALLON)
                _LOGGER.info("Alle DMX-Szenen eingeschaltet")
                
            elif action == "all_off":
                # Alle Szenen ausschalten
                result = await coordinator.device.api.set_all_dmx_scenes(ACTION_ALLOFF)
                _LOGGER.info("Alle DMX-Szenen ausgeschaltet")
                
            elif action == "all_auto":
                # Alle Szenen auf AUTO
                result = await coordinator.device.api.set_all_dmx_scenes(ACTION_ALLAUTO)
                _LOGGER.info("Alle DMX-Szenen auf AUTO")
                
            elif action == "sequence":
                # Sequenz durchlaufen
                if not scene_selection:
                    scene_selection = [f"DMX_SCENE{i}" for i in range(1, 13)]
                
                _LOGGER.info("Starte DMX-Sequenz: %d Szenen", len(scene_selection))
                
                for i, scene in enumerate(scene_selection, 1):
                    _LOGGER.debug("Sequenz %d/%d: %s", i, len(scene_selection), scene)
                    await coordinator.device.api.set_switch_state(scene, ACTION_ON)
                    await asyncio.sleep(sequence_delay)
                    await coordinator.device.api.set_switch_state(scene, ACTION_OFF)
                
                result = {
                    "success": True, 
                    "response": f"Sequenz mit {len(scene_selection)} Szenen abgeschlossen"
                }
                
            elif action == "random":
                # Zufällige Szenen aktivieren
                all_scenes = [f"DMX_SCENE{i}" for i in range(1, 13)]
                random_scenes = random.sample(all_scenes, min(5, len(all_scenes)))
                
                _LOGGER.info("Aktiviere zufällige DMX-Szenen: %s", ', '.join(random_scenes))
                
                for scene in random_scenes:
                    await coordinator.device.api.set_switch_state(scene, ACTION_ON)
                
                result = {
                    "success": True, 
                    "response": f"Zufällige Szenen aktiviert: {', '.join(random_scenes)}"
                }
                
            elif action == "party_mode":
                # Party-Modus: Alle an + Farbpulse
                _LOGGER.info("🎉 Party-Modus aktiviert!")
                await coordinator.device.api.set_all_dmx_scenes(ACTION_ALLON)
                await coordinator.device.api.set_light_color_pulse()
                
                result = {"success": True, "response": "Party-Modus aktiviert 🎉"}
            
            if result.get("success", True):
                _LOGGER.info("✅ DMX-Aktion '%s' erfolgreich", action)
            else:
                _LOGGER.warning("DMX-Aktion '%s' fehlgeschlagen: %s", 
                              action, result.get("response", result))
            
            await coordinator.async_request_refresh()
            
        except VioletPoolAPIError as err:
            _LOGGER.error("DMX-Steuerung Fehler: %s", err)
            raise HomeAssistantError(f"DMX-Steuerung fehlgeschlagen: {err}") from err
    
    async def handle_set_light_color_pulse(self, call: ServiceCall) -> None:
        """
        Legacy: Licht-Farbpuls Service.
        Sendet Farbpulse an die Beleuchtung.
        """
        coordinators = await self.manager.get_coordinators_for_entities(
            call.data[ATTR_ENTITY_ID]
        )
        pulse_count = call.data.get("pulse_count", 1)
        pulse_interval = call.data.get("pulse_interval", 500)
        
        for coordinator in coordinators:
            try:
                _LOGGER.info("Starte %d Farbpulse (Intervall: %dms)", 
                           pulse_count, pulse_interval)
                
                for i in range(pulse_count):
                    result = await coordinator.device.api.set_light_color_pulse()
                    
                    if not result.get("success", True):
                        _LOGGER.warning("Farbpuls %d/%d fehlgeschlagen: %s", 
                                      i+1, pulse_count, result.get("response", result))
                    
                    if i < pulse_count - 1:
                        await asyncio.sleep(pulse_interval / 1000)
                
                _LOGGER.info("✅ Farbpuls-Sequenz abgeschlossen (%d Pulse)", pulse_count)
                
            except VioletPoolAPIError as err:
                _LOGGER.error("Farbpuls Fehler: %s", err)
                raise HomeAssistantError(f"Farbpuls fehlgeschlagen: {err}") from err
            
            await coordinator.async_request_refresh()
    
    async def handle_manage_digital_rules(self, call: ServiceCall) -> None:
        """
        Digitale Input-Regeln verwalten.
        Für Cover-Automatisierung und Sensoren.
        """
        device_id = call.data["device_id"]
        rule_key = call.data["rule_key"]
        action = call.data["action"]
        delay = call.data.get("delay", 0)
        
        coordinator = await self.manager.get_coordinator_for_device(device_id)
        if not coordinator:
            raise HomeAssistantError(f"Gerät nicht gefunden: {device_id}")
        
        try:
            if action == "trigger":
                # Regel sofort triggern
                if delay > 0:
                    _LOGGER.info("Regel %s wird in %ds getriggert", rule_key, delay)
                    asyncio.create_task(
                        self._delayed_rule_trigger(coordinator, rule_key, delay)
                    )
                    result = {
                        "success": True, 
                        "response": f"Regel {rule_key} geplant für {delay}s"
                    }
                else:
                    result = await coordinator.device.api.trigger_digital_input_rule(rule_key)
                    _LOGGER.info("Regel %s getriggert", rule_key)
                    
            elif action == "lock":
                # Regel sperren
                result = await coordinator.device.api.set_digital_input_rule_lock(rule_key, True)
                _LOGGER.info("Regel %s gesperrt", rule_key)
                
            elif action == "unlock":
                # Regel entsperren
                result = await coordinator.device.api.set_digital_input_rule_lock(rule_key, False)
                _LOGGER.info("Regel %s entsperrt", rule_key)
                
            elif action == "disable":
                # Regel deaktivieren
                result = await coordinator.device.api.set_digital_input_rule_lock(rule_key, True)
                _LOGGER.info("Regel %s deaktiviert", rule_key)
            
            if result.get("success", True):
                _LOGGER.info("✅ Digital-Regel '%s' Aktion '%s' erfolgreich", rule_key, action)
            else:
                _LOGGER.warning("Digital-Regel Aktion fehlgeschlagen: %s", 
                              result.get("response", result))
            
            await coordinator.async_request_refresh()
            
        except VioletPoolAPIError as err:
            _LOGGER.error("Digital-Regel Fehler: %s", err)
            raise HomeAssistantError(f"Digital-Regel fehlgeschlagen: {err}") from err
    
    async def _delayed_rule_trigger(self, coordinator, rule_key: str, delay_seconds: int):
        """Verzögertes Triggern einer Regel."""
        await asyncio.sleep(delay_seconds)
        try:
            result = await coordinator.device.api.trigger_digital_input_rule(rule_key)
            if result.get("success", True):
                _LOGGER.info("Verzögerter Trigger für %s ausgeführt", rule_key)
            await coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Verzögerter Trigger Fehler für %s: %s", rule_key, err)
    
    async def handle_control_extension_relay(self, call: ServiceCall) -> None:
        """
        Extension-Relais steuern.
        Oft für DMX-Controller oder Cover-Motoren verwendet.
        """
        coordinators = await self.manager.get_coordinators_for_entities(
            call.data[ATTR_ENTITY_ID]
        )
        action = call.data["action"]
        duration = call.data.get("duration", 3600)
        pulse_duration = call.data.get("pulse_duration", 1)
        repeat_count = call.data.get("repeat_count", 1)
        
        for coordinator in coordinators:
            for entity_id in call.data[ATTR_ENTITY_ID]:
                device_key = self.manager.extract_device_key(entity_id)
                
                # Prüfe ob Extension-Relais
                if not (device_key.startswith("EXT1_") or 
                       device_key.startswith("EXT2_") or 
                       device_key.startswith("OMNI_DC")):
                    _LOGGER.warning("%s ist kein Extension-Relais", entity_id)
                    continue
                
                try:
                    if action == "timer_on":
                        # Timer: An für X Sekunden
                        result = await coordinator.device.api.set_switch_state(
                            key=device_key, action=ACTION_ON, duration=duration
                        )
                        _LOGGER.info("Relais %s → AN (%ds)", device_key, duration)
                        
                    elif action == "timer_off":
                        # Timer: Aus für X Sekunden
                        result = await coordinator.device.api.set_switch_state(
                            key=device_key, action=ACTION_OFF, duration=duration
                        )
                        _LOGGER.info("Relais %s → AUS (%ds)", device_key, duration)
                        
                    elif action == "pulse":
                        # Puls-Sequenz
                        _LOGGER.info("Starte Puls-Sequenz für %s: %d Wiederholungen", 
                                   device_key, repeat_count)
                        
                        for i in range(repeat_count):
                            # AN
                            await coordinator.device.api.set_switch_state(
                                key=device_key, action=ACTION_ON, duration=pulse_duration
                            )
                            await asyncio.sleep(pulse_duration + 1)
                            
                            # AUS
                            await coordinator.device.api.set_switch_state(
                                key=device_key, action=ACTION_OFF, duration=pulse_duration
                            )
                            
                            if i < repeat_count - 1:
                                await asyncio.sleep(pulse_duration + 1)
                        
                        result = {
                            "success": True, 
                            "response": f"Puls-Sequenz abgeschlossen ({repeat_count}x)"
                        }
                    
                    if result.get("success", True):
                        _LOGGER.info("✅ Relais-Aktion '%s' erfolgreich", action)
                    else:
                        _LOGGER.warning("Relais-Steuerung fehlgeschlagen: %s", 
                                      result.get("response", result))
                        
                except VioletPoolAPIError as err:
                    _LOGGER.error("Extension-Relais Fehler: %s", err)
                    raise HomeAssistantError(f"Relais-Steuerung fehlgeschlagen: {err}") from err
            
            await coordinator.async_request_refresh()


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════

async def async_register_dmx_cover_services(hass: HomeAssistant, service_manager) -> None:
    """Registriere DMX & Cover Spezial-Services."""
    
    handlers = VioletDmxCoverServiceHandlers(service_manager)
    
    dmx_cover_services = {
        "control_dmx_scenes": handlers.handle_control_dmx_scenes,
        "set_light_color_pulse": handlers.handle_set_light_color_pulse,
        "manage_digital_rules": handlers.handle_manage_digital_rules,
        "control_extension_relay": handlers.handle_control_extension_relay,
    }
    
    for service_name, handler in dmx_cover_services.items():
        hass.services.async_register(
            DOMAIN,
            service_name,
            handler,
            schema=DMX_COVER_SERVICE_SCHEMAS[service_name]
        )
    
    _LOGGER.info("✅ DMX & Cover Services registriert (%d Services)", len(dmx_cover_services))
