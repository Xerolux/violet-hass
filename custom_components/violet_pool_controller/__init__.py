"""Initialisierung der Violet Pool Controller Integration."""
import logging
import asyncio
from typing import Any, Dict, List, Set, Final, Optional

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import aiohttp_client, entity_registry, service
from homeassistant.helpers.typing import ConfigType
import homeassistant.helpers.config_validation as cv
from homeassistant.exceptions import HomeAssistantError
from homeassistant.const import DOMAIN_SWITCH # Added for turn_auto

from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_USE_SSL,
    CONF_DEVICE_ID,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_DEVICE_NAME,
    CONF_POLLING_INTERVAL,
    CONF_TIMEOUT_DURATION,
    CONF_RETRY_ATTEMPTS,
    CONF_ACTIVE_FEATURES,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_RETRY_ATTEMPTS,
)
from .api import VioletPoolAPI
from .device import async_setup_device, VioletPoolDataUpdateCoordinator

# Plattformen, die diese Integration unterstützt
PLATFORMS: Final[List[str]] = [
    "sensor",
    "binary_sensor",
    "switch",
    "climate",
    "cover",
    "number",
]

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Richte die Integration via YAML ein (veraltet).

    Args:
        hass: Home Assistant Instanz.
        config: Konfigurationsdaten aus YAML.

    Returns:
        bool: True bei Erfolg, False sonst.
    """
    if DOMAIN in config:
        _LOGGER.warning(
            "Die YAML-Konfiguration für %s ist nicht unterstützt. "
            "Bitte nutze die UI-Konfiguration (Einstellungen -> Integrationen).",
            DOMAIN
        )
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setze die Integration via Config Entry auf.

    Args:
        hass: Home Assistant Instanz.
        entry: Config Entry mit Gerätekonfiguration.

    Returns:
        bool: True bei Erfolg, False sonst.

    Raises:
        HomeAssistantError: Bei Setup-Fehlern.
    """
    _LOGGER.info("Setting up Violet Pool Controller integration (entry_id=%s)", entry.entry_id)

    ip_address = entry.data.get(CONF_API_URL, entry.data.get("base_ip", "127.0.0.1"))
    use_ssl = entry.data.get(CONF_USE_SSL, True)
    device_id = entry.data.get(CONF_DEVICE_ID, 1)
    username = entry.data.get(CONF_USERNAME, "")
    password = entry.data.get(CONF_PASSWORD, "")
    device_name = entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller")

    polling_interval = int(
        entry.options.get(CONF_POLLING_INTERVAL, entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL))
    )
    timeout_duration = int(
        entry.options.get(CONF_TIMEOUT_DURATION, entry.data.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION))
    )
    retry_attempts = int(
        entry.options.get(CONF_RETRY_ATTEMPTS, entry.data.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS))
    )
    active_features = entry.options.get(CONF_ACTIVE_FEATURES, entry.data.get(CONF_ACTIVE_FEATURES, []))

    sanitized_config = {
        "ip_address": ip_address,
        "use_ssl": use_ssl,
        "device_id": device_id,
        "username": username if not username else "***",
        "password": "***" if password else "",
        "device_name": device_name,
        "polling_interval": polling_interval,
        "timeout_duration": timeout_duration,
        "retry_attempts": retry_attempts,
        "active_features": active_features,
    }
    _LOGGER.info("Final config (entry_id=%s) => %s", entry.entry_id, sanitized_config)

    try:
        session = aiohttp_client.async_get_clientsession(hass)
        api = VioletPoolAPI(
            host=ip_address,
            session=session,
            username=username,
            password=password,
            use_ssl=use_ssl,
            timeout=timeout_duration,
        )
        coordinator = await async_setup_device(hass, entry)
        if not coordinator:
            _LOGGER.error("Fehler beim Einrichten des Coordinators")
            return False
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = coordinator
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        register_services(hass)
        _LOGGER.info("Violet Pool Controller Setup für '%s' (entry_id=%s) abgeschlossen", device_name, entry.entry_id)
        return True
    except Exception as err:
        _LOGGER.exception("Fehler beim Einrichten des Violet Pool Controllers (entry_id=%s): %s", entry.entry_id, err)
        raise HomeAssistantError(f"Fehler beim Einrichten des Violet Pool Controllers: {err}") from err

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entferne die Integration.

    Args:
        hass: Home Assistant Instanz.
        entry: Config Entry zum Entladen.

    Returns:
        bool: True bei Erfolg, False sonst.
    """
    try:
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
        if unload_ok and DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
            hass.data[DOMAIN].pop(entry.entry_id)
            _LOGGER.info("Violet Pool Controller '%s' (entry_id=%s) erfolgreich entladen", entry.data.get(CONF_DEVICE_NAME, "Unbekannt"), entry.entry_id)
        return unload_ok
    except Exception as err:
        _LOGGER.exception("Fehler beim Entladen von Violet Pool Controller (entry_id=%s): %s", entry.entry_id, err)
        return False

def register_services(hass: HomeAssistant) -> None:
    """Registriere Services für die Integration.

    Args:
        hass: Home Assistant Instanz.
    """
    if hass.services.has_service(DOMAIN, "set_temperature_target"):
        _LOGGER.debug("Services für %s sind bereits registriert", DOMAIN)
        return

    SET_TEMPERATURE_TARGET_SCHEMA = vol.Schema({
        vol.Required("entity_ids"): cv.entity_ids,
        vol.Required("temperature"): vol.All(vol.Coerce(float), vol.Range(min=20, max=40)),
    })

    SET_PH_TARGET_SCHEMA = vol.Schema({
        vol.Required("entity_ids"): cv.entity_ids,
        vol.Required("target_value"): vol.All(vol.Coerce(float), vol.Range(min=6.8, max=7.8)),
    })

    SET_CHLORINE_TARGET_SCHEMA = vol.Schema({
        vol.Required("entity_ids"): cv.entity_ids,
        vol.Required("target_value"): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=3.0)),
    })

    TRIGGER_BACKWASH_SCHEMA = vol.Schema({
        vol.Required("entity_ids"): cv.entity_ids,
        vol.Optional("duration", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=900)),
    })

    START_WATER_ANALYSIS_SCHEMA = vol.Schema({
        vol.Required("entity_ids"): cv.entity_ids,
    })

    SET_MAINTENANCE_MODE_SCHEMA = vol.Schema({
        vol.Required("entity_ids"): cv.entity_ids,
        vol.Optional("enable", default=True): cv.boolean,
    })

    async def async_handle_set_temperature_target(call: ServiceCall) -> None:
        """Setze die Zieltemperatur für mehrere Entitäten.

        Args:
            call: ServiceCall mit entity_ids und temperature.
        """
        entity_ids = call.data.get("entity_ids", [])
        temperature = call.data.get("temperature")

        for entity_id in entity_ids:
            if not hass.states.get(entity_id):
                _LOGGER.error("Entity nicht gefunden: %s", entity_id)
                continue
            try:
                await hass.services.async_call(
                    "climate",
                    "set_temperature",
                    {"entity_id": entity_id, "temperature": temperature},
                    blocking=True,
                )
                _LOGGER.info("Zieltemperatur für %s auf %.1f°C gesetzt", entity_id, temperature)
            except Exception as err:
                _LOGGER.error("Fehler beim Setzen der Zieltemperatur für %s: %s", entity_id, err)
                raise HomeAssistantError(f"Fehler beim Setzen der Zieltemperatur für {entity_id}: {err}")

    async def async_handle_set_ph_target(call: ServiceCall) -> None:
        """Setze den pH-Sollwert für mehrere Entitäten.

        Args:
            call: ServiceCall mit entity_ids und target_value.
        """
        entity_ids = call.data.get("entity_ids", [])
        target_value = call.data.get("target_value")

        for entity_id in entity_ids:
            if not hass.states.get(entity_id):
                _LOGGER.error("Entity nicht gefunden: %s", entity_id)
                continue
            try:
                await hass.services.async_call(
                    "number",
                    "set_value",
                    {"entity_id": entity_id, "value": target_value},
                    blocking=True,
                )
                _LOGGER.info("pH-Sollwert für %s auf %.1f gesetzt", entity_id, target_value)
            except Exception as err:
                _LOGGER.error("Fehler beim Setzen des pH-Sollwerts für %s: %s", entity_id, err)
                raise HomeAssistantError(f"Fehler beim Setzen des pH-Sollwerts für {entity_id}: {err}")

    async def async_handle_set_chlorine_target(call: ServiceCall) -> None:
        """Setze den Chlor-Sollwert für mehrere Entitäten.

        Args:
            call: ServiceCall mit entity_ids und target_value.
        """
        entity_ids = call.data.get("entity_ids", [])
        target_value = call.data.get("target_value")

        for entity_id in entity_ids:
            if not hass.states.get(entity_id):
                _LOGGER.error("Entity nicht gefunden: %s", entity_id)
                continue
            try:
                await hass.services.async_call(
                    "number",
                    "set_value",
                    {"entity_id": entity_id, "value": target_value},
                    blocking=True,
                )
                _LOGGER.info("Chlor-Sollwert für %s auf %.1f mg/l gesetzt", entity_id, target_value)
            except Exception as err:
                _LOGGER.error("Fehler beim Setzen des Chlor-Sollwerts für %s: %s", entity_id, err)
                raise HomeAssistantError(f"Fehler beim Setzen des Chlor-Sollwerts für {entity_id}: {err}")

    async def async_handle_trigger_backwash(call: ServiceCall) -> None:
        """Löse eine Rückspülung für mehrere Entitäten aus.

        Args:
            call: ServiceCall mit entity_ids und optional duration.
        """
        entity_ids = call.data.get("entity_ids", [])
        duration = call.data.get("duration", 0)

        for entity_id in entity_ids:
            if not hass.states.get(entity_id):
                _LOGGER.error("Entity nicht gefunden: %s", entity_id)
                continue
            try:
                await hass.services.async_call(
                    "switch",
                    "turn_on",
                    {"entity_id": entity_id},
                    blocking=True,
                )
                _LOGGER.info("Rückspülung für %s gestartet", entity_id)
                if duration > 0:
                    _LOGGER.info("Plane automatische Abschaltung für %s nach %d Sekunden", entity_id, duration)
                    hass.async_create_task(delayed_turn_off(entity_id, duration))
            except Exception as err:
                _LOGGER.error("Fehler beim Starten der Rückspülung für %s: %s", entity_id, err)
                raise HomeAssistantError(f"Fehler beim Starten der Rückspülung für {entity_id}: {err}")

    async def delayed_turn_off(entity_id: str, duration: int) -> None:
        """Schalte einen Switch nach Verzögerung aus.

        Args:
            entity_id: ID der Entität.
            duration: Verzögerung in Sekunden.
        """
        try:
            await asyncio.sleep(duration)
            await hass.services.async_call(
                "switch",
                "turn_off",
                {"entity_id": entity_id},
                blocking=True,
            )
            _LOGGER.info("Rückspülung für %s nach %d Sekunden automatisch beendet", entity_id, duration)
        except Exception as err:
            _LOGGER.error("Fehler bei automatischer Abschaltung von %s: %s", entity_id, err)

    async def async_handle_start_water_analysis(call: ServiceCall) -> None:
        """Starte die Wasseranalyse für mehrere Geräte.

        Args:
            call: ServiceCall mit entity_ids.
        """
        entity_ids = call.data.get("entity_ids", [])
        if not entity_ids:
            _LOGGER.error("Keine entity_ids angegeben")
            raise HomeAssistantError("Keine entity_ids angegeben")

        registry = entity_registry.async_get(hass)
        coordinators = set()

        for entity_id in entity_ids:
            entity_entry = registry.async_get(entity_id)
            if entity_entry and entity_entry.config_entry_id in hass.data[DOMAIN]:
                coordinators.add(hass.data[DOMAIN][entity_entry.config_entry_id])

        for coordinator in coordinators:
            try:
                result = await coordinator.device.async_send_command(
                    endpoint="/startWaterAnalysis",
                    command={},
                )
                if isinstance(result, dict) and result.get("success", False):
                    _LOGGER.info("Wasseranalyse für %s erfolgreich gestartet", coordinator.device.name)
                else:
                    _LOGGER.warning("Wasseranalyse für %s möglicherweise nicht erfolgreich: %s", coordinator.device.name, result)
                await coordinator.async_request_refresh()
            except Exception as err:
                _LOGGER.error("Fehler beim Starten der Wasseranalyse für %s: %s", coordinator.device.name, err)
                raise HomeAssistantError(f"Fehler beim Starten der Wasseranalyse für {coordinator.device.name}: {err}")

    async def async_handle_set_maintenance_mode(call: ServiceCall) -> None:
        """Setze den Wartungsmodus für mehrere Geräte.

        Args:
            call: ServiceCall mit entity_ids und enable.
        """
        entity_ids = call.data.get("entity_ids", [])
        enable = call.data.get("enable", True)
        if not entity_ids:
            _LOGGER.error("Keine entity_ids angegeben")
            raise HomeAssistantError("Keine entity_ids angegeben")

        registry = entity_registry.async_get(hass)
        coordinators = set()

        for entity_id in entity_ids:
            entity_entry = registry.async_get(entity_id)
            if entity_entry and entity_entry.config_entry_id in hass.data[DOMAIN]:
                coordinators.add(hass.data[DOMAIN][entity_entry.config_entry_id])

        for coordinator in coordinators:
            try:
                result = await coordinator.device.async_send_command(
                    endpoint="/set_switch",
                    command={
                        "id": "MAINTENANCE",
                        "action": "ON" if enable else "OFF",
                        "duration": 0,
                        "value": 0,
                    },
                )
                if isinstance(result, dict) and result.get("success", False):
                    _LOGGER.info("Wartungsmodus für %s auf %s gesetzt", coordinator.device.name, "EIN" if enable else "AUS")
                else:
                    _LOGGER.warning("Wartungsmodus für %s möglicherweise nicht gesetzt: %s", coordinator.device.name, result)
                await coordinator.async_request_refresh()
            except Exception as err:
                _LOGGER.error("Fehler beim Setzen des Wartungsmodus für %s: %s", coordinator.device.name, err)
                raise HomeAssistantError(f"Fehler beim Setzen des Wartungsmodus für {coordinator.device.name}: {err}")

    hass.services.async_register(
        DOMAIN, "set_temperature_target", async_handle_set_temperature_target, schema=SET_TEMPERATURE_TARGET_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "set_ph_target", async_handle_set_ph_target, schema=SET_PH_TARGET_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "set_chlorine_target", async_handle_set_chlorine_target, schema=SET_CHLORINE_TARGET_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "trigger_backwash", async_handle_trigger_backwash, schema=TRIGGER_BACKWASH_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "start_water_analysis", async_handle_start_water_analysis, schema=START_WATER_ANALYSIS_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "set_maintenance_mode", async_handle_set_maintenance_mode, schema=SET_MAINTENANCE_MODE_SCHEMA
    )

    TURN_AUTO_SCHEMA = vol.Schema({
        vol.Optional("auto_delay", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=86400)),
    })

    async def async_handle_turn_auto(call: ServiceCall) -> None:
        """Schalte einen Switch in den Automatikmodus mit optionaler Verzögerung für manuellen Override.

        Args:
            call: ServiceCall mit entity_ids (via target) und optional auto_delay.
        """
        auto_delay = call.data.get("auto_delay", 0)
        # entity_ids are extracted based on the 'target' field in services.yaml
        target_entity_ids = await service.extract_entity_ids(hass, call)

        switch_platform = hass.data.get(DOMAIN_SWITCH)
        if not switch_platform:
            _LOGGER.error("Switch platform not loaded, cannot handle turn_auto service.")
            return

        for entity_id in target_entity_ids:
            entity_object = next((e for e in switch_platform.entities if e.entity_id == entity_id), None)

            if entity_object and hasattr(entity_object, 'async_turn_auto'):
                try:
                    _LOGGER.debug(f"Calling async_turn_auto for {entity_id} with delay {auto_delay}s")
                    await entity_object.async_turn_auto(auto_delay=auto_delay)
                    _LOGGER.info(f"Successfully called turn_auto for {entity_id} with delay {auto_delay}s")
                except Exception as e:
                    _LOGGER.error(f"Error calling async_turn_auto for {entity_id}: {e}", exc_info=True)
            elif not entity_object:
                _LOGGER.warning(f"Could not find switch entity with ID {entity_id} to call turn_auto.")
            else: # Entity found, but no async_turn_auto method
                _LOGGER.warning(f"Switch entity {entity_id} does not have an async_turn_auto method.")
    
    hass.services.async_register(
        DOMAIN, "turn_auto", async_handle_turn_auto, schema=TURN_AUTO_SCHEMA
    )

    SET_PV_SURPLUS_SCHEMA = vol.Schema({
        vol.Required("pump_speed"): vol.All(vol.Coerce(int), vol.Range(min=1, max=3)),
    })

    async def async_handle_set_pv_surplus(call: ServiceCall) -> None:
        """Aktiviere den PV-Überschussmodus für einen Switch und setze die Pumpengeschwindigkeit.

        Args:
            call: ServiceCall mit entity_ids (via target) und pump_speed.
        """
        pump_speed = call.data["pump_speed"] # Schema makes it required
        target_entity_ids = await service.extract_entity_ids(hass, call)

        switch_platform = hass.data.get(DOMAIN_SWITCH)
        if not switch_platform:
            _LOGGER.error("Switch platform not loaded, cannot handle set_pv_surplus service.")
            return

        for entity_id in target_entity_ids:
            entity_object = next((e for e in switch_platform.entities if e.entity_id == entity_id), None)

            if entity_object and hasattr(entity_object, 'entity_description') and hasattr(entity_object, 'async_turn_on'):
                # Check if this is the PVSURPLUS switch by its entity_description key
                if getattr(entity_object.entity_description, 'key', None) == "PVSURPLUS":
                    try:
                        _LOGGER.debug(f"Calling async_turn_on for PV Surplus switch {entity_id} with pump_speed {pump_speed}")
                        # The async_turn_on method of VioletPVSurplusSwitch should handle the pump_speed
                        await entity_object.async_turn_on(pump_speed=pump_speed) 
                        _LOGGER.info(f"Successfully set PV surplus for {entity_id} with pump_speed {pump_speed}")
                    except Exception as e:
                        _LOGGER.error(f"Error calling async_turn_on for PV surplus switch {entity_id}: {e}", exc_info=True)
                else:
                    _LOGGER.warning(f"Entity {entity_id} is not the PV Surplus switch. Ignoring for set_pv_surplus.")
            elif not entity_object:
                _LOGGER.warning(f"Could not find switch entity with ID {entity_id} to call set_pv_surplus.")
            elif not hasattr(entity_object, 'entity_description'):
                _LOGGER.warning(f"Switch entity {entity_id} does not have an entity_description. Cannot verify if it's PV Surplus switch.")
            else: # Entity found, but no async_turn_on method
                _LOGGER.warning(f"Switch entity {entity_id} (PVSURPLUS) does not have an async_turn_on method.")

    hass.services.async_register(
        DOMAIN, "set_pv_surplus", async_handle_set_pv_surplus, schema=SET_PV_SURPLUS_SCHEMA
    )

    MANUAL_DOSING_SCHEMA = vol.Schema({
        vol.Required("duration_seconds"): vol.All(vol.Coerce(int), vol.Range(min=1, max=3600)),
    })

    async def async_handle_manual_dosing(call: ServiceCall) -> None:
        """Löse eine manuelle Dosierung für eine bestimmte Dosiereinheit aus.

        Args:
            call: ServiceCall mit entity_ids (via target) und duration_seconds.
        """
        duration_seconds = call.data["duration_seconds"] # Schema makes it required
        target_entity_ids = await service.extract_entity_ids(hass, call)
        
        ent_reg = entity_registry.async_get(hass)
        switch_platform = hass.data.get(DOMAIN_SWITCH)

        if not switch_platform:
            _LOGGER.error("Switch platform not loaded, cannot handle manual_dosing service.")
            return

        for entity_id in target_entity_ids:
            entity_object = next((e for e in switch_platform.entities if e.entity_id == entity_id), None)
            
            if not entity_object:
                _LOGGER.warning(f"Could not find switch entity with ID {entity_id} for manual_dosing.")
                continue

            if not hasattr(entity_object, 'entity_description') or not hasattr(entity_object.entity_description, 'key'):
                _LOGGER.warning(f"Switch entity {entity_id} does not have a valid entity_description.key for manual_dosing.")
                continue
            
            dosing_key = entity_object.entity_description.key

            entity_entry = ent_reg.async_get(entity_id)
            if not entity_entry:
                _LOGGER.warning(f"Could not find entity registry entry for {entity_id}.")
                continue
            
            config_entry_id = entity_entry.config_entry_id
            if not config_entry_id or config_entry_id not in hass.data[DOMAIN]:
                _LOGGER.warning(f"Could not find config entry ID or coordinator for {entity_id}.")
                continue
                
            coordinator = hass.data[DOMAIN][config_entry_id]
            device = coordinator.device

            if device and hasattr(device, 'async_manual_dosing'):
                try:
                    _LOGGER.debug(f"Calling async_manual_dosing for {dosing_key} (entity: {entity_id}) for {duration_seconds}s on device {device.device_name}")
                    success = await device.async_manual_dosing(dosing_key=dosing_key, duration_seconds=duration_seconds)
                    if success:
                        _LOGGER.info(f"Manual dosing for {dosing_key} (entity: {entity_id}) for {duration_seconds}s successfully triggered.")
                    else:
                        _LOGGER.error(f"Manual dosing for {dosing_key} (entity: {entity_id}) for {duration_seconds}s failed. Check device logs.")
                except Exception as e:
                    _LOGGER.error(f"Error calling async_manual_dosing for {dosing_key} (entity: {entity_id}): {e}", exc_info=True)
            elif not device:
                 _LOGGER.warning(f"Device not found for entity {entity_id} (coordinator: {coordinator.name}).")
            else: # device found, but no async_manual_dosing method
                _LOGGER.warning(f"Device {device.device_name} for entity {entity_id} does not have an async_manual_dosing method.")

    hass.services.async_register(
        DOMAIN, "manual_dosing", async_handle_manual_dosing, schema=MANUAL_DOSING_SCHEMA
    )

    _LOGGER.info("Services für %s registriert", DOMAIN)