"""Initialisierung der Violet Pool Controller Integration."""
import logging
import asyncio
from typing import Any, Dict, List, Set, Final, Optional

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import aiohttp_client, entity_registry
from homeassistant.helpers.typing import ConfigType
import homeassistant.helpers.config_validation as cv
from homeassistant.exceptions import HomeAssistantError

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
from .api import VioletPoolAPI, ACTION_ALLON, ACTION_ALLAUTO, ACTION_ALLOFF # Import DMX action constants
from .device import async_setup_device, VioletPoolDataUpdateCoordinator
from homeassistant.const import ATTR_DEVICE_ID # Import ATTR_DEVICE_ID

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
        # Pass the api instance to async_setup_device
        coordinator = await async_setup_device(hass, entry, api)
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
                # Use the API method on the device's api instance
                result = await coordinator.device.api.start_water_analysis()
                # The result structure from VioletPoolAPI methods is already a dict or raises an error.
                # We can assume success if no exception is raised, or check specific content if necessary.
                # For now, let's assume methods in VioletPoolAPI return a dict that might include a success indicator
                # or rely on them raising exceptions for failures.
                # The _normalize_response in api.py tries to add "success" for string responses.
                if result.get("success", True): # Assume success if not explicitly false
                    _LOGGER.info("Wasseranalyse für %s erfolgreich gestartet.", coordinator.device.name)
                else:
                    _LOGGER.warning("Wasseranalyse für %s möglicherweise nicht erfolgreich: %s", coordinator.device.name, result.get("response", result))
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
                # Use the API method on the device's api instance
                result = await coordinator.device.api.set_maintenance_mode(enabled=enable)
                # Similar to start_water_analysis, check success.
                if result.get("success", True): # Assume success if not explicitly false
                    _LOGGER.info("Wartungsmodus für %s auf %s gesetzt.", coordinator.device.name, "EIN" if enable else "AUS")
                else:
                    _LOGGER.warning("Wartungsmodus für %s möglicherweise nicht erfolgreich gesetzt: %s", coordinator.device.name, result.get("response", result))
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

    # Schema for set_all_dmx_scenes_mode
    SET_ALL_DMX_SCENES_MODE_SCHEMA = vol.Schema({
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required("dmx_mode"): vol.In([ACTION_ALLON, ACTION_ALLAUTO, ACTION_ALLOFF]),
    })

    async def async_handle_set_all_dmx_scenes_mode(call: ServiceCall) -> None:
        """Handle the set_all_dmx_scenes_mode service call."""
        device_id = call.data.get(ATTR_DEVICE_ID)
        dmx_mode = call.data.get("dmx_mode")
        
        coordinator: Optional[VioletPoolDataUpdateCoordinator] = hass.data[DOMAIN].get(device_id)

        if not coordinator or not hasattr(coordinator, 'device') or not hasattr(coordinator.device, 'api'):
            _LOGGER.error("DMX Scenes: Device %s nicht gefunden oder API nicht verfügbar.", device_id)
            raise HomeAssistantError(f"Violet Pool Controller Gerät {device_id} nicht gefunden.")

        try:
            _LOGGER.info("Setze alle DMX Szenen für %s auf Modus %s", coordinator.device.name, dmx_mode)
            result = await coordinator.device.api.set_all_dmx_scenes(action=dmx_mode)
            if isinstance(result, dict) and result.get("success", True): 
                _LOGGER.info("Alle DMX Szenen für %s erfolgreich auf %s gesetzt.", coordinator.device.name, dmx_mode)
            else:
                _LOGGER.warning("Setzen aller DMX Szenen für %s auf %s möglicherweise nicht erfolgreich: %s", coordinator.device.name, dmx_mode, result.get("response", result))
            await coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Fehler beim Setzen aller DMX Szenen für %s: %s", coordinator.device.name, err)
            raise HomeAssistantError(f"Fehler beim Setzen aller DMX Szenen für {coordinator.device.name}: {err}")

    hass.services.async_register(
        DOMAIN, "set_all_dmx_scenes_mode", async_handle_set_all_dmx_scenes_mode, schema=SET_ALL_DMX_SCENES_MODE_SCHEMA
    )

    # Schema for set_digital_input_rule_lock_state
    SET_DIGITAL_INPUT_RULE_LOCK_STATE_SCHEMA = vol.Schema({
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required("rule_key"): cv.string,
        vol.Required("lock_state"): cv.boolean,
    })

    async def async_handle_set_digital_input_rule_lock_state(call: ServiceCall) -> None:
        """Handle the set_digital_input_rule_lock_state service call."""
        device_id = call.data.get(ATTR_DEVICE_ID)
        rule_key = call.data.get("rule_key")
        lock_state = call.data.get("lock_state")

        coordinator: Optional[VioletPoolDataUpdateCoordinator] = hass.data[DOMAIN].get(device_id)

        if not coordinator or not hasattr(coordinator, 'device') or not hasattr(coordinator.device, 'api'):
            _LOGGER.error("DIRULE Lock: Device %s nicht gefunden oder API nicht verfügbar.", device_id)
            raise HomeAssistantError(f"Violet Pool Controller Gerät {device_id} nicht gefunden.")

        try:
            _LOGGER.info("Setze Lock-Status für DIRULE %s auf %s für Gerät %s", rule_key, lock_state, coordinator.device.name)
            result = await coordinator.device.api.set_digital_input_rule_lock(rule_key=rule_key, lock=lock_state)
            if isinstance(result, dict) and result.get("success", True):
                _LOGGER.info("Lock-Status für DIRULE %s auf %s für Gerät %s erfolgreich gesetzt.", rule_key, lock_state, coordinator.device.name)
            else:
                _LOGGER.warning("Setzen des Lock-Status für DIRULE %s auf %s für Gerät %s möglicherweise nicht erfolgreich: %s", rule_key, lock_state, coordinator.device.name, result.get("response", result))
            await coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Fehler beim Setzen des Lock-Status für DIRULE %s für Gerät %s: %s", rule_key, coordinator.device.name, err)
            raise HomeAssistantError(f"Fehler beim Setzen des Lock-Status für DIRULE {rule_key} für Gerät {coordinator.device.name}: {err}")
            
    hass.services.async_register(
        DOMAIN, "set_digital_input_rule_lock_state", async_handle_set_digital_input_rule_lock_state, schema=SET_DIGITAL_INPUT_RULE_LOCK_STATE_SCHEMA
    )

    _LOGGER.info("Services für %s registriert", DOMAIN)