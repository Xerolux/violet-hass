"""Violet Pool Controller Integration."""
import logging
import asyncio
from typing import Any, Dict
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import Platform, ATTR_DEVICE_ID
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client, entity_registry
from .const import (
    DOMAIN, CONF_API_URL, CONF_USE_SSL, CONF_DEVICE_ID, CONF_USERNAME, CONF_PASSWORD,
    CONF_DEVICE_NAME, CONF_POLLING_INTERVAL, CONF_TIMEOUT_DURATION, CONF_RETRY_ATTEMPTS,
    CONF_ACTIVE_FEATURES, DEFAULT_POLLING_INTERVAL, DEFAULT_TIMEOUT_DURATION, DEFAULT_RETRY_ATTEMPTS,
    ACTION_ALLON, ACTION_ALLAUTO, ACTION_ALLOFF
)
from .api import VioletPoolAPI
from .device import async_setup_device

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SWITCH, Platform.CLIMATE, Platform.COVER, Platform.NUMBER]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old config entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)
    return config_entry.version == 1  # No migration needed for version 1

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up integration via YAML (deprecated)."""
    if DOMAIN in config:
        _LOGGER.warning("YAML configuration for %s is deprecated. Use UI configuration.", DOMAIN)
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration from config entry."""
    _LOGGER.info("Setting up Violet Pool Controller (entry_id=%s)", entry.entry_id)

    config = {
        "ip_address": entry.data.get(CONF_API_URL, entry.data.get("host", entry.data.get("base_ip", "127.0.0.1"))),
        "use_ssl": entry.data.get(CONF_USE_SSL, True),
        "device_id": entry.data.get(CONF_DEVICE_ID, 1),
        "username": entry.data.get(CONF_USERNAME, ""),
        "password": entry.data.get(CONF_PASSWORD, ""),
        "device_name": entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller"),
        "polling_interval": entry.options.get(CONF_POLLING_INTERVAL, entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)),
        "timeout_duration": entry.options.get(CONF_TIMEOUT_DURATION, entry.data.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION)),
        "retry_attempts": entry.options.get(CONF_RETRY_ATTEMPTS, entry.data.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS)),
        "active_features": entry.options.get(CONF_ACTIVE_FEATURES, entry.data.get(CONF_ACTIVE_FEATURES, [])),
    }

    try:
        api = VioletPoolAPI(
            host=config["ip_address"],
            session=aiohttp_client.async_get_clientsession(hass),
            username=config["username"],
            password=config["password"],
            use_ssl=config["use_ssl"],
            timeout=config["timeout_duration"],
        )
        coordinator = await async_setup_device(hass, entry, api)
        if not coordinator:
            _LOGGER.error("Failed to set up coordinator")
            return False
        hass.data[DOMAIN][entry.entry_id] = coordinator
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        await register_services(hass)
        _LOGGER.info("Setup completed for '%s' (entry_id=%s)", config["device_name"], entry.entry_id)
        return True
    except Exception as err:
        _LOGGER.exception("Setup error (entry_id=%s): %s", entry.entry_id, err)
        raise HomeAssistantError(f"Setup error: {err}") from err

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload integration."""
    try:
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
        if unload_ok and entry.entry_id in hass.data.get(DOMAIN, {}):
            hass.data[DOMAIN].pop(entry.entry_id)
            _LOGGER.info("Unloaded '%s' (entry_id=%s)", entry.data.get(CONF_DEVICE_NAME, "Unknown"), entry.entry_id)
        return unload_ok
    except Exception as err:
        _LOGGER.exception("Unload error (entry_id=%s): %s", entry.entry_id, err)
        return False

async def register_services(hass: HomeAssistant) -> None:
    """Register integration services."""
    if hass.services.has_service(DOMAIN, "set_temperature_target"):
        return

    SERVICE_SCHEMAS = {
        "set_temperature_target": vol.Schema({
            vol.Required("entity_ids"): cv.entity_ids,
            vol.Required("temperature"): vol.All(vol.Coerce(float), vol.Range(min=20, max=40)),
        }),
        "set_ph_target": vol.Schema({
            vol.Required("entity_ids"): cv.entity_ids,
            vol.Required("target_value"): vol.All(vol.Coerce(float), vol.Range(min=6.8, max=7.8)),
        }),
        "set_chlorine_target": vol.Schema({
            vol.Required("entity_ids"): cv.entity_ids,
            vol.Required("target_value"): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=3.0)),
        }),
        "trigger_backwash": vol.Schema({
            vol.Required("entity_ids"): cv.entity_ids,
            vol.Optional("duration", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=900)),
        }),
        "start_water_analysis": vol.Schema({
            vol.Required("entity_ids"): cv.entity_ids,
        }),
        "set_maintenance_mode": vol.Schema({
            vol.Required("entity_ids"): cv.entity_ids,
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

    async def handle_service(call: ServiceCall, service_name: str, action: str, params: Dict[str, Any]) -> None:
        """Generic service handler."""
        registry = entity_registry.async_get(hass)
        coordinators = set()
        for entity_id in call.data.get("entity_ids", []):
            entity_entry = registry.async_get(entity_id)
            if entity_entry and entity_entry.config_entry_id in hass.data[DOMAIN]:
                coordinators.add(hass.data[DOMAIN][entity_entry.config_entry_id])
        
        for coordinator in coordinators:
            try:
                result = await getattr(coordinator.device.api, action)(**params)
                if isinstance(result, dict) and result.get("success", True):
                    _LOGGER.info("%s successful for %s", service_name, coordinator.device.name)
                else:
                    _LOGGER.warning("%s possibly failed for %s: %s", service_name, coordinator.device.name, result.get("response", result))
                await coordinator.async_request_refresh()
            except Exception as err:
                _LOGGER.error("Error in %s for %s: %s", service_name, coordinator.device.name, err)
                raise HomeAssistantError(f"Error in {service_name} for {coordinator.device.name}: {err}")

    async def async_handle_set_temperature_target(call: ServiceCall) -> None:
        """Set target temperature."""
        for entity_id in call.data.get("entity_ids", []):
            if not hass.states.get(entity_id):
                _LOGGER.error("Entity not found: %s", entity_id)
                continue
            try:
                await hass.services.async_call(
                    "climate", "set_temperature",
                    {"entity_id": entity_id, "temperature": call.data["temperature"]},
                    blocking=True,
                )
                _LOGGER.info("Set temperature for %s to %.1f°C", entity_id, call.data["temperature"])
            except Exception as err:
                _LOGGER.error("Error setting temperature for %s: %s", entity_id, err)
                raise HomeAssistantError(f"Error setting temperature for {entity_id}: {err}")

    async def async_handle_set_ph_target(call: ServiceCall) -> None:
        """Set pH target."""
        for entity_id in call.data.get("entity_ids", []):
            if not hass.states.get(entity_id):
                _LOGGER.error("Entity not found: %s", entity_id)
                continue
            try:
                await hass.services.async_call(
                    "number", "set_value",
                    {"entity_id": entity_id, "value": call.data["target_value"]},
                    blocking=True,
                )
                _LOGGER.info("Set pH target for %s to %.1f", entity_id, call.data["target_value"])
            except Exception as err:
                _LOGGER.error("Error setting pH target for %s: %s", entity_id, err)
                raise HomeAssistantError(f"Error setting pH target for {entity_id}: {err}")

    async def async_handle_set_chlorine_target(call: ServiceCall) -> None:
        """Set chlorine target."""
        for entity_id in call.data.get("entity_ids", []):
            if not hass.states.get(entity_id):
                _LOGGER.error("Entity not found: %s", entity_id)
                continue
            try:
                await hass.services.async_call(
                    "number", "set_value",
                    {"entity_id": entity_id, "value": call.data["target_value"]},
                    blocking=True,
                )
                _LOGGER.info("Set chlorine target for %s to %.1f mg/l", entity_id, call.data["target_value"])
            except Exception as err:
                _LOGGER.error("Error setting chlorine target for %s: %s", entity_id, err)
                raise HomeAssistantError(f"Error setting chlorine target for {entity_id}: {err}")

    async def async_handle_trigger_backwash(call: ServiceCall) -> None:
        """Trigger backwash."""
        for entity_id in call.data.get("entity_ids", []):
            if not hass.states.get(entity_id):
                _LOGGER.error("Entity not found: %s", entity_id)
                continue
            try:
                await hass.services.async_call("switch", "turn_on", {"entity_id": entity_id}, blocking=True)
                _LOGGER.info("Started backwash for %s", entity_id)
                if call.data.get("duration", 0) > 0:
                    hass.async_create_task(delayed_turn_off(hass, entity_id, call.data["duration"]))
            except Exception as err:
                _LOGGER.error("Error triggering backwash for %s: %s", entity_id, err)
                raise HomeAssistantError(f"Error triggering backwash for {entity_id}: {err}")

    async def delayed_turn_off(hass: HomeAssistant, entity_id: str, duration: int) -> None:
        """Turn off switch after delay."""
        await asyncio.sleep(duration)
        try:
            await hass.services.async_call("switch", "turn_off", {"entity_id": entity_id}, blocking=True)
            _LOGGER.info("Backwash for %s stopped after %d seconds", entity_id, duration)
        except Exception as err:
            _LOGGER.error("Error stopping backwash for %s: %s", entity_id, err)

    # Service registrations with proper handlers
    hass.services.async_register(
        DOMAIN, "set_temperature_target", 
        async_handle_set_temperature_target, 
        schema=SERVICE_SCHEMAS["set_temperature_target"]
    )
    hass.services.async_register(
        DOMAIN, "set_ph_target", 
        async_handle_set_ph_target, 
        schema=SERVICE_SCHEMAS["set_ph_target"]
    )
    hass.services.async_register(
        DOMAIN, "set_chlorine_target", 
        async_handle_set_chlorine_target, 
        schema=SERVICE_SCHEMAS["set_chlorine_target"]
    )
    hass.services.async_register(
        DOMAIN, "trigger_backwash", 
        async_handle_trigger_backwash, 
        schema=SERVICE_SCHEMAS["trigger_backwash"]
    )
    hass.services.async_register(
        DOMAIN, "start_water_analysis",
        lambda call: handle_service(call, "Water analysis", "start_water_analysis", {}),
        schema=SERVICE_SCHEMAS["start_water_analysis"]
    )
    hass.services.async_register(
        DOMAIN, "set_maintenance_mode",
        lambda call: handle_service(call, "Maintenance mode", "set_maintenance_mode", {"enabled": call.data["enable"]}),
        schema=SERVICE_SCHEMAS["set_maintenance_mode"]
    )
    hass.services.async_register(
        DOMAIN, "set_all_dmx_scenes_mode",
        lambda call: handle_service(call, "DMX scenes mode", "set_all_dmx_scenes", {"action": call.data["dmx_mode"]}),
        schema=SERVICE_SCHEMAS["set_all_dmx_scenes_mode"]
    )
    hass.services.async_register(
        DOMAIN, "set_digital_input_rule_lock_state",
        lambda call: handle_service(call, "DIRULE lock state", "set_digital_input_rule_lock", {"rule_key": call.data["rule_key"], "lock": call.data["lock_state"]}),
        schema=SERVICE_SCHEMAS["set_digital_input_rule_lock_state"]
    )
    hass.services.async_register(
        DOMAIN, "trigger_digital_input_rule",
        lambda call: handle_service(call, "DIRULE trigger", "trigger_digital_input_rule", {"rule_key": call.data["rule_key"]}),
        schema=SERVICE_SCHEMAS["trigger_digital_input_rule"]
    )
    
    _LOGGER.info("Services for %s registered", DOMAIN)
