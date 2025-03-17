"""Initialisierung der Violet Pool Controller Integration."""
import logging
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

# Home Assistant-Typen und Funktionen
from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_POLLING_INTERVAL,
    CONF_USE_SSL,
    CONF_DEVICE_ID,
    CONF_USERNAME,
    CONF_PASSWORD,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_USE_SSL,
)

# Unsere eigenen Module
from .api import VioletPoolAPI
from .coordinator import VioletDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "switch", "binary_sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setze einen Violet Pool Controller via Config Entry auf."""
    _LOGGER.info("Setting up Violet Pool Controller integration")

    # Konfiguration aus ConfigEntry auslesen
    config: Dict[str, Any] = {
        "ip_address": entry.data[CONF_API_URL],
        "polling_interval": entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL),
        "use_ssl": entry.data.get(CONF_USE_SSL, DEFAULT_USE_SSL),
        "device_id": entry.data.get(CONF_DEVICE_ID, 1),
        "username": entry.data.get(CONF_USERNAME),
        "password": entry.data.get(CONF_PASSWORD),
        "timeout": entry.options.get("timeout", 10),
        "retries": entry.options.get("retries", 3),
    }

    # Aiohttp-Session von Home Assistant besorgen
    session = aiohttp_client.async_get_clientsession(hass)

    # API-Objekt erzeugen, das nur HTTP-Anfragen kapselt
    api = VioletPoolAPI(
        host=config["ip_address"],
        username=config["username"],
        password=config["password"],
        use_ssl=config["use_ssl"],
        timeout=config["timeout"],
    )
    # Session von außen setzen
    api.session = session

    # DataUpdateCoordinator anlegen, der regelmäßig die Daten über die API holt
    coordinator = VioletDataUpdateCoordinator(hass=hass, config=config, api=api)

    try:
        # Erster Datenabruf (kann fehlschlagen, deshalb Exception-Handling)
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Erster Datenabruf fehlgeschlagen: %s", err)
        return False

    # Integration im globalen hass.data speichern
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Plattformen (sensor, switch, binary_sensor) asynchron initialisieren
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    )

    # Beispiel-Service registrieren, mit dem du z.B. die Pumpe schalten könntest
    # (falls du in api.py `set_pump_state` angelegt hast).
    async def async_handle_set_pump_state(call):
        """Service-Handler, um die Pumpe ein- oder auszuschalten."""
        pump_on = call.data.get("pump_on", True)
        try:
            await api.set_pump_state(pump_on)
            # Optional ein Refresh auslösen, damit neue Daten gleich sichtbar werden
            await coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Fehler beim Setzen des Pumpen-Status: %s", err)

    hass.services.async_register(
        DOMAIN, "set_pump_state", async_handle_set_pump_state
    )

    _LOGGER.info("Violet Pool Controller Setup abgeschlossen")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entferne einen Violet Pool Controller Config Entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        _LOGGER.info("Violet Pool Controller (Gerät %s) erfolgreich entladen", entry.entry_id)
    return unload_ok
