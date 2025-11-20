"""Violet Pool Controller Integration - IMPROVED VERSION."""
import logging
from typing import Any

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client

from .const import (
    DOMAIN, CONF_API_URL, CONF_USE_SSL, CONF_DEVICE_ID, CONF_USERNAME, CONF_PASSWORD,
    CONF_DEVICE_NAME, CONF_CONTROLLER_NAME, CONF_POLLING_INTERVAL, CONF_TIMEOUT_DURATION,
    CONF_RETRY_ATTEMPTS, CONF_ACTIVE_FEATURES, DEFAULT_POLLING_INTERVAL, DEFAULT_TIMEOUT_DURATION,
    DEFAULT_RETRY_ATTEMPTS, DEFAULT_CONTROLLER_NAME
)

_LOGGER = logging.getLogger(__name__)

# Platforms die geladen werden sollen
PLATFORMS: list[Platform] = [
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


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
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
        
        # Platforms laden
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        
        # Services registrieren (nur einmal für die gesamte Integration)
        from .services import async_register_services
        await async_register_services(hass)
        
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
                hass.data[DOMAIN].pop(entry.entry_id)
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

def _extract_config(entry: ConfigEntry) -> dict[str, Any]:
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
        "controller_name": entry.data.get(CONF_CONTROLLER_NAME, DEFAULT_CONTROLLER_NAME),
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


def _validate_config(config: dict[str, Any]) -> bool:
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
