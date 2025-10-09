"""Violet Pool Controller Integration - IMPROVED VERSION."""
import logging
import asyncio
from typing import Any, Dict, List

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import Platform, ATTR_DEVICE_ID, ATTR_ENTITY_ID
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client, entity_registry as er

from .const import (
    DOMAIN, CONF_API_URL, CONF_USE_SSL, CONF_DEVICE_ID, CONF_USERNAME, CONF_PASSWORD,
    CONF_DEVICE_NAME, CONF_POLLING_INTERVAL, CONF_TIMEOUT_DURATION, CONF_RETRY_ATTEMPTS,
    CONF_ACTIVE_FEATURES, DEFAULT_POLLING_INTERVAL, DEFAULT_TIMEOUT_DURATION, 
    DEFAULT_RETRY_ATTEMPTS, ACTION_ALLON, ACTION_ALLAUTO, ACTION_ALLOFF
)

_LOGGER = logging.getLogger(__name__)

# Platforms die geladen werden sollen
PLATFORMS: List[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.CLIMATE,
    Platform.COVER,
    Platform.NUMBER,
]

# YAML-Konfiguration ist deprecated
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


# =============================================================================
# SETUP FUNCTIONS
# =============================================================================

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old config entry."""
    _LOGGER.debug("Migrating config entry from version %s", config_entry.version)
    
    if config_entry.version == 1:
        # Version 1 braucht keine Migration
        _LOGGER.debug("Config entry already at version 1, no migration needed")
        return True
    
    # Zukuenftige Migrationen hier hinzufuegen
    _LOGGER.warning("Unknown config entry version: %s", config_entry.version)
    return False


async def async_setup(hass: HomeAssistant, config: Dict[str, Any]) -> bool:
    """Set up integration via YAML (deprecated)."""
    if DOMAIN in config:
        _LOGGER.warning(
            "YAML configuration for %s is deprecated and will be removed in a future version. "
            "Please use the UI to configure the integration.",
            DOMAIN
        )
    
    # Initialisiere Domain-Daten wenn nicht vorhanden
    hass.data.setdefault(DOMAIN, {})
    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Violet Pool Controller from a config entry - IMPROVED VERSION."""
    _LOGGER.info(
        "Setting up Violet Pool Controller (entry_id=%s, device=%s)",
        entry.entry_id,
        entry.data.get(CONF_DEVICE_NAME, "Unknown")
    )

    # Lazy imports to avoid blocking the event loop
    from .api import VioletPoolAPI
    from .device import async_setup_device

    # Extrahiere Konfiguration
    config = _extract_config(entry)
    
    # Validiere Konfiguration
    if not _validate_config(config):
        raise HomeAssistantError("Invalid configuration")

    try:
        # API-Instanz erstellen
        api = VioletPoolAPI(
            host=config["ip_address"],
            session=aiohttp_client.async_get_clientsession(hass),
            username=config["username"],
            password=config["password"],
            use_ssl=config["use_ssl"],
            timeout=config["timeout_duration"],
            max_retries=config["retry_attempts"]
        )
        
        # Device und Coordinator einrichten
        coordinator = await async_setup_device(hass, entry, api)
        
        if not coordinator:
            _LOGGER.error("Failed to set up coordinator for %s", config["device_name"])
            raise HomeAssistantError("Coordinator setup failed")
        
        # Coordinator in hass.data speichern
        hass.data[DOMAIN][entry.entry_id] = coordinator
        
        # Platforms laden - Alternative Methode um Blocking-Warning zu vermeiden
        # Methode 1: Standard (empfohlen fuer neuere HA Versionen)
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        
        # Methode 2: Falls Blocking-Warnings weiterhin auftreten, diese verwenden:
        # for platform in PLATFORMS:
        #     hass.async_create_task(
        #         hass.config_entries.async_forward_entry_setup(entry, platform)
        #     )
        # await asyncio.sleep(0)  # Kurze Pause damit Tasks starten koennen
        
        # Services registrieren
        await async_register_all_services(hass)
        
        _LOGGER.info(
            "Setup completed successfully for '%s' (entry_id=%s)",
            config["device_name"],
            entry.entry_id
        )
        
        return True
        
    except Exception as err:
        _LOGGER.exception(
            "Unexpected error during setup (entry_id=%s): %s",
            entry.entry_id,
            err
        )
        raise HomeAssistantError(f"Setup error: {err}") from err


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry - IMPROVED VERSION."""
    device_name = entry.data.get(CONF_DEVICE_NAME, "Unknown")
    _LOGGER.info("Unloading '%s' (entry_id=%s)", device_name, entry.entry_id)
    
    try:
        # Platforms entladen
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
        
        if unload_ok:
            # Coordinator aus hass.data entfernen
            if entry.entry_id in hass.data.get(DOMAIN, {}):
                coordinator = hass.data[DOMAIN].pop(entry.entry_id)
                _LOGGER.debug("Coordinator removed for entry_id=%s", entry.entry_id)
            
            _LOGGER.info("Successfully unloaded '%s' (entry_id=%s)", device_name, entry.entry_id)
        else:
            _LOGGER.warning("Failed to unload platforms for '%s' (entry_id=%s)", device_name, entry.entry_id)
        
        return unload_ok
        
    except Exception as err:
        _LOGGER.exception(
            "Error during unload of '%s' (entry_id=%s): %s",
            device_name,
            entry.entry_id,
            err
        )
        return False


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _extract_config(entry: ConfigEntry) -> Dict[str, Any]:
    """Extract configuration from config entry - NEW."""
    # IP-Adresse mit Fallbacks extrahieren
    ip_address = (
        entry.data.get(CONF_API_URL) or
        entry.data.get("host") or
        entry.data.get("base_ip")
    )
    
    if not ip_address:
        raise HomeAssistantError("No IP address found in config entry")
    
    return {
        "ip_address": ip_address.strip(),
        "use_ssl": entry.data.get(CONF_USE_SSL, True),
        "device_id": entry.data.get(CONF_DEVICE_ID, 1),
        "username": entry.data.get(CONF_USERNAME, ""),
        "password": entry.data.get(CONF_PASSWORD, ""),
        "device_name": entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller"),
        "polling_interval": entry.options.get(
            CONF_POLLING_INTERVAL,
            entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
        ),
        "timeout_duration": entry.options.get(
            CONF_TIMEOUT_DURATION,
            entry.data.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION)
        ),
        "retry_attempts": entry.options.get(
            CONF_RETRY_ATTEMPTS,
            entry.data.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS)
        ),
        "active_features": entry.options.get(
            CONF_ACTIVE_FEATURES,
            entry.data.get(CONF_ACTIVE_FEATURES, [])
        ),
    }


def _validate_config(config: Dict[str, Any]) -> bool:
    """Validate extracted configuration - NEW."""
    required_keys = ["ip_address", "device_name"]
    
    for key in required_keys:
        if not config.get(key):
            _LOGGER.error("Missing required config key: %s", key)
            return False
    
    # Validiere numerische Werte
    if not 5 <= config["polling_interval"] <= 300:
        _LOGGER.error("Invalid polling_interval: %s (must be 5-300)", config["polling_interval"])
        return False
    
    if not 5 <= config["timeout_duration"] <= 60:
        _LOGGER.error("Invalid timeout_duration: %s (must be 5-60)", config["timeout_duration"])
        return False
    
    if not 1 <= config["retry_attempts"] <= 10:
        _LOGGER.error("Invalid retry_attempts: %s (must be 1-10)", config["retry_attempts"])
        return False
    
    return True


# =============================================================================
# SERVICE REGISTRATION - VEREINFACHTE VERSION
# =============================================================================

async def async_register_all_services(hass: HomeAssistant) -> None:
    """Register all integration services - ASYNC VERSION."""
    # Pruefe ob Services bereits registriert sind
    if hass.services.has_service(DOMAIN, "set_temperature_target"):
        _LOGGER.debug("Services already registered, skipping")
        return
    
    _LOGGER.info("Registering services for %s", DOMAIN)
    
    # Service-Schemas definieren
    SERVICE_SCHEMAS = {
        "set_temperature_target": vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
            vol.Required("temperature"): vol.All(
                vol.Coerce(float),
                vol.Range(min=20, max=40)
            ),
        }),
        "set_ph_target": vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
            vol.Required("target_value"): vol.All(
                vol.Coerce(float),
                vol.Range(min=6.8, max=7.8)
            ),
        }),
        "set_chlorine_target": vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
            vol.Required("target_value"): vol.All(
                vol.Coerce(float),
                vol.Range(min=0.1, max=3.0)
            ),
        }),
        "trigger_backwash": vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
            vol.Optional("duration", default=0): vol.All(
                vol.Coerce(int),
                vol.Range(min=0, max=900)
            ),
        }),
        "start_water_analysis": vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        }),
        "set_maintenance_mode": vol.Schema({
            vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
            vol.Optional("enable", default=True): cv.boolean,
        }),
        "set_all_dmx_scenes_mode": vol.Schema({
            vol.Required(ATTR_DEVICE_ID): cv.string,
            vol.Required("dmx_mode"): vol.In([ACTION_ALLON, ACTION_ALLAUTO, ACTION_ALLOFF]),
        }),
        "set_digital_input_rule_lock_state": vol.Schema({
            vol.Required(ATTR_DEVICE_ID): cv.string,
            vol.Required("rule_key"): cv.string,
            vol.Required("lock_state"): cv.boolean,
        }),
        "trigger_digital_input_rule": vol.Schema({
            vol.Required(ATTR_DEVICE_ID): cv.string,
            vol.Required("rule_key"): cv.string,
        }),
    }
    
    # Service-Handler registrieren
    hass.services.async_register(
        DOMAIN,
        "set_temperature_target",
        _async_handle_set_temperature_target,
        schema=SERVICE_SCHEMAS["set_temperature_target"]
    )
    
    hass.services.async_register(
        DOMAIN,
        "set_ph_target",
        _async_handle_set_ph_target,
        schema=SERVICE_SCHEMAS["set_ph_target"]
    )
    
    hass.services.async_register(
        DOMAIN,
        "set_chlorine_target",
        _async_handle_set_chlorine_target,
        schema=SERVICE_SCHEMAS["set_chlorine_target"]
    )
    
    hass.services.async_register(
        DOMAIN,
        "trigger_backwash",
        _async_handle_trigger_backwash,
        schema=SERVICE_SCHEMAS["trigger_backwash"]
    )
    
    hass.services.async_register(
        DOMAIN,
        "start_water_analysis",
        _async_handle_start_water_analysis,
        schema=SERVICE_SCHEMAS["start_water_analysis"]
    )
    
    hass.services.async_register(
        DOMAIN,
        "set_maintenance_mode",
        _async_handle_set_maintenance_mode,
        schema=SERVICE_SCHEMAS["set_maintenance_mode"]
    )
    
    hass.services.async_register(
        DOMAIN,
        "set_all_dmx_scenes_mode",
        _async_handle_set_dmx_scenes_mode,
        schema=SERVICE_SCHEMAS["set_all_dmx_scenes_mode"]
    )
    
    hass.services.async_register(
        DOMAIN,
        "set_digital_input_rule_lock_state",
        _async_handle_dirule_lock,
        schema=SERVICE_SCHEMAS["set_digital_input_rule_lock_state"]
    )
    
    hass.services.async_register(
        DOMAIN,
        "trigger_digital_input_rule",
        _async_handle_dirule_trigger,
        schema=SERVICE_SCHEMAS["trigger_digital_input_rule"]
    )
    
    # Versuche zusaetzliche erweiterte Services zu laden (falls vorhanden)
    try:
        from .services import async_register_services
        await async_register_services(hass)
    except ImportError:
        _LOGGER.debug("No additional services module found")
    
    _LOGGER.info("Successfully registered %d basic services", len(SERVICE_SCHEMAS))


# =============================================================================
# SERVICE HANDLERS - DIREKT ALS ASYNC FUNKTIONEN
# =============================================================================

async def _async_handle_set_temperature_target(call: ServiceCall) -> None:
    """Handle set temperature target service."""
    hass = call.hass
    entity_ids = call.data[ATTR_ENTITY_ID]
    temperature = call.data["temperature"]
    
    _LOGGER.info("Setting temperature target to %.1f°C for: %s", temperature, entity_ids)
    
    for entity_id in entity_ids:
        try:
            await hass.services.async_call(
                "climate",
                "set_temperature",
                {ATTR_ENTITY_ID: entity_id, "temperature": temperature},
                blocking=True
            )
        except Exception as err:
            _LOGGER.error("Failed to set temperature for %s: %s", entity_id, err)


async def _async_handle_set_ph_target(call: ServiceCall) -> None:
    """Handle set pH target service."""
    hass = call.hass
    entity_ids = call.data[ATTR_ENTITY_ID]
    target_value = call.data["target_value"]
    
    _LOGGER.info("Setting pH target to %.2f for: %s", target_value, entity_ids)
    
    for entity_id in entity_ids:
        try:
            await hass.services.async_call(
                "number",
                "set_value",
                {ATTR_ENTITY_ID: entity_id, "value": target_value},
                blocking=True
            )
        except Exception as err:
            _LOGGER.error("Failed to set pH for %s: %s", entity_id, err)


async def _async_handle_set_chlorine_target(call: ServiceCall) -> None:
    """Handle set chlorine target service."""
    hass = call.hass
    entity_ids = call.data[ATTR_ENTITY_ID]
    target_value = call.data["target_value"]
    
    _LOGGER.info("Setting chlorine target to %.2f mg/l for: %s", target_value, entity_ids)
    
    for entity_id in entity_ids:
        try:
            await hass.services.async_call(
                "number",
                "set_value",
                {ATTR_ENTITY_ID: entity_id, "value": target_value},
                blocking=True
            )
        except Exception as err:
            _LOGGER.error("Failed to set chlorine for %s: %s", entity_id, err)


async def _async_handle_trigger_backwash(call: ServiceCall) -> None:
    """Handle trigger backwash service."""
    hass = call.hass
    entity_ids = call.data[ATTR_ENTITY_ID]
    duration = call.data.get("duration", 0)
    
    _LOGGER.info("Triggering backwash for: %s (duration: %ds)", entity_ids, duration)
    
    for entity_id in entity_ids:
        try:
            # Backwash einschalten
            await hass.services.async_call(
                "switch",
                "turn_on",
                {ATTR_ENTITY_ID: entity_id},
                blocking=True
            )
            
            _LOGGER.info("Backwash started for %s", entity_id)
            
            # Wenn Duration gesetzt, automatisch wieder ausschalten
            if duration > 0:
                await asyncio.sleep(duration)
                
                await hass.services.async_call(
                    "switch",
                    "turn_off",
                    {ATTR_ENTITY_ID: entity_id},
                    blocking=True
                )
                
                _LOGGER.info("Backwash stopped for %s after %ds", entity_id, duration)
                
        except Exception as err:
            _LOGGER.error("Failed to trigger backwash for %s: %s", entity_id, err)


async def _async_handle_start_water_analysis(call: ServiceCall) -> None:
    """Handle start water analysis service."""
    _LOGGER.info("Starting water analysis")
    _LOGGER.warning("Water analysis service not fully implemented yet")


async def _async_handle_set_maintenance_mode(call: ServiceCall) -> None:
    """Handle set maintenance mode service."""
    entity_ids = call.data[ATTR_ENTITY_ID]
    enable = call.data.get("enable", True)
    
    action = "enable" if enable else "disable"
    _LOGGER.info("Maintenance mode %s for: %s", action, entity_ids)
    _LOGGER.warning("Maintenance mode service not fully implemented yet")


async def _async_handle_set_dmx_scenes_mode(call: ServiceCall) -> None:
    """Handle set DMX scenes mode service."""
    device_id = call.data[ATTR_DEVICE_ID]
    dmx_mode = call.data["dmx_mode"]
    
    _LOGGER.info("Setting DMX scenes mode to %s for device %s", dmx_mode, device_id)
    _LOGGER.warning("DMX scenes service not fully implemented yet")


async def _async_handle_dirule_lock(call: ServiceCall) -> None:
    """Handle digital input rule lock state service."""
    device_id = call.data[ATTR_DEVICE_ID]
    rule_key = call.data["rule_key"]
    lock_state = call.data["lock_state"]
    
    action = "lock" if lock_state else "unlock"
    _LOGGER.info("Digital input rule %s %s for device %s", rule_key, action, device_id)
    _LOGGER.warning("DIRULE lock service not fully implemented yet")


async def _async_handle_dirule_trigger(call: ServiceCall) -> None:
    """Handle trigger digital input rule service."""
    device_id = call.data[ATTR_DEVICE_ID]
    rule_key = call.data["rule_key"]
    
    _LOGGER.info("Triggering digital input rule %s for device %s", rule_key, device_id)
    _LOGGER.warning("DIRULE trigger service not fully implemented yet")