"""Violet Pool Controller Integration - IMPROVED VERSION."""

from __future__ import annotations

import logging
from typing import Any

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers import aiohttp_client

from .const import (
    CONF_ACTIVE_FEATURES,
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_PASSWORD,
    CONF_POLLING_INTERVAL,
    CONF_RETRY_ATTEMPTS,
    CONF_TIMEOUT_DURATION,
    CONF_USE_SSL,
    CONF_USERNAME,
    DEFAULT_CONTROLLER_NAME,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_TIMEOUT_DURATION,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

# Platforms to be loaded
PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.SELECT,
    Platform.CLIMATE,
    Platform.COVER,
    Platform.NUMBER,
]

# YAML configuration is deprecated
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


# =============================================================================
# SETUP FUNCTIONS
# =============================================================================


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old config entry.

    Args:
        hass: The Home Assistant instance.
        config_entry: The config entry to migrate.

    Returns:
        True if migration was successful, False otherwise.
    """
    _LOGGER.debug("Migrating config entry from version %s", config_entry.version)

    if config_entry.version == 1:
        # Version 1 requires no migration
        _LOGGER.debug("Config entry already at version 1, no migration needed")
        return True

    # Add future migrations here
    _LOGGER.warning("Unknown config entry version: %s", config_entry.version)
    return False


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up integration via YAML (deprecated).

    Args:
        hass: The Home Assistant instance.
        config: The configuration dictionary.

    Returns:
        True.
    """
    if DOMAIN in config:
        _LOGGER.warning(
            "YAML configuration for %s is deprecated and will be removed in a future version. "
            "Please use the UI to configure the integration.",
            DOMAIN,
        )

    # Initialize domain data if not present
    hass.data.setdefault(DOMAIN, {})

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Violet Pool Controller from a config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry.

    Returns:
        True if setup was successful.

    Raises:
        ConfigEntryNotReady: If the controller is not ready.
        HomeAssistantError: If the configuration is invalid.
    """
    _LOGGER.info(
        "Setting up Violet Pool Controller (entry_id=%s, controller=%s)",
        entry.entry_id,
        entry.data.get(
            CONF_CONTROLLER_NAME, entry.data.get(CONF_DEVICE_NAME, "Unknown")
        ),
    )

    # Lazy imports to avoid blocking the event loop
    from .api import VioletPoolAPI
    from .device import async_setup_device

    # Extract configuration
    config = _extract_config(entry)

    # Validate configuration
    if not _validate_config(config):
        raise HomeAssistantError("Invalid configuration")

    try:
        # Create API instance
        api = VioletPoolAPI(
            host=config["ip_address"],
            session=aiohttp_client.async_get_clientsession(hass),
            username=config["username"],
            password=config["password"],
            use_ssl=config["use_ssl"],
            timeout=config["timeout_duration"],
            max_retries=config["retry_attempts"],
        )

        # Set up device and coordinator
        coordinator = await async_setup_device(hass, entry, api)

        if not coordinator:
            _LOGGER.error("Failed to set up coordinator for %s", config["device_name"])
            raise ConfigEntryNotReady("Coordinator setup failed")

        # Store coordinator in hass.data
        hass.data[DOMAIN][entry.entry_id] = coordinator

        # Load platforms
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        # Register services (only once for the entire integration)
        from .services import async_register_services

        await async_register_services(hass)

        _LOGGER.info(
            "Setup completed successfully for '%s' (entry_id=%s)",
            config["device_name"],
            entry.entry_id,
        )

        return True

    except ConfigEntryNotReady:
        # Re-raise ConfigEntryNotReady to allow Home Assistant to handle retries
        _LOGGER.warning(
            "Setup for '%s' is not ready yet, will be retried automatically",
            config["device_name"],
        )
        raise

    except Exception as err:
        _LOGGER.exception(
            "Unexpected error during setup (entry_id=%s): %s", entry.entry_id, err
        )
        raise ConfigEntryNotReady(f"Setup error: {err}") from err


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry to unload.

    Returns:
        True if unload was successful, False otherwise.
    """
    device_name = entry.data.get(CONF_DEVICE_NAME, "Unknown")
    _LOGGER.info("Unloading '%s' (entry_id=%s)", device_name, entry.entry_id)

    try:
        # Unload platforms
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

        if unload_ok:
            # Remove coordinator from hass.data
            if entry.entry_id in hass.data.get(DOMAIN, {}):
                hass.data[DOMAIN].pop(entry.entry_id)
                _LOGGER.debug("Coordinator removed for entry_id=%s", entry.entry_id)

            _LOGGER.info(
                "Successfully unloaded '%s' (entry_id=%s)", device_name, entry.entry_id
            )
        else:
            _LOGGER.warning(
                "Failed to unload platforms for '%s' (entry_id=%s)",
                device_name,
                entry.entry_id,
            )

        return unload_ok

    except Exception as err:
        _LOGGER.exception(
            "Error during unload of '%s' (entry_id=%s): %s",
            device_name,
            entry.entry_id,
            err,
        )
        return False


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _extract_config(entry: ConfigEntry) -> dict[str, Any]:
    """Extract and normalize configuration from a ConfigEntry.

    This function retrieves configuration values from the ConfigEntry's data and options,
    providing default values for missing optional settings. It also handles legacy
    configuration keys for backward compatibility.

    Args:
        entry: The Home Assistant ConfigEntry.

    Returns:
        A dictionary containing the extracted and normalized configuration.

    Raises:
        HomeAssistantError: If the IP address (host) is missing from the configuration.
    """
    # Extract IP address with fallbacks for legacy keys
    ip_address = (
        entry.data.get(CONF_API_URL)
        or entry.data.get("host")
        or entry.data.get("base_ip")
    )

    if not ip_address:
        _LOGGER.error("Required IP address is missing from the configuration.")
        raise HomeAssistantError("No IP address found in config entry")

    # Build the configuration dictionary with defaults
    return {
        "ip_address": ip_address.strip(),
        "use_ssl": entry.data.get(CONF_USE_SSL, True),
        "device_id": entry.data.get(CONF_DEVICE_ID, 1),
        "username": entry.data.get(CONF_USERNAME, ""),
        "password": entry.data.get(CONF_PASSWORD, ""),
        "device_name": entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller"),
        "controller_name": entry.data.get(
            CONF_CONTROLLER_NAME, DEFAULT_CONTROLLER_NAME
        ),
        "polling_interval": entry.options.get(
            CONF_POLLING_INTERVAL,
            entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL),
        ),
        "timeout_duration": entry.options.get(
            CONF_TIMEOUT_DURATION,
            entry.data.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION),
        ),
        "retry_attempts": entry.options.get(
            CONF_RETRY_ATTEMPTS,
            entry.data.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS),
        ),
        "active_features": entry.options.get(
            CONF_ACTIVE_FEATURES, entry.data.get(CONF_ACTIVE_FEATURES, [])
        ),
    }


def _validate_config(config: dict[str, Any]) -> bool:
    """Validate the extracted configuration.

    This function checks for the presence of required keys and ensures that numeric
    values are within their acceptable ranges.

    Args:
        config: The configuration dictionary to validate.

    Returns:
        True if the configuration is valid, False otherwise.
    """
    required_keys = ["ip_address", "device_name"]

    for key in required_keys:
        if not config.get(key):
            _LOGGER.error("Missing required configuration key: %s", key)
            return False

    # Validate numeric ranges
    if not 5 <= config["polling_interval"] <= 300:
        _LOGGER.error(
            "Invalid polling_interval: %s (must be between 5 and 300)",
            config["polling_interval"],
        )
        return False

    if not 5 <= config["timeout_duration"] <= 60:
        _LOGGER.error(
            "Invalid timeout_duration: %s (must be between 5 and 60)",
            config["timeout_duration"],
        )
        return False

    if not 1 <= config["retry_attempts"] <= 10:
        _LOGGER.error(
            "Invalid retry_attempts: %s (must be between 1 and 10)",
            config["retry_attempts"],
        )
        return False

    _LOGGER.debug("Configuration validated successfully.")
    return True
