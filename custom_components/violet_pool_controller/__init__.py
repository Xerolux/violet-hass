"""Initialisierung der Violet Pool Controller Integration."""
import logging
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

# Home Assistant-Typen und Funktionen
from .const import DOMAIN
from .coordinator import VioletDataUpdateCoordinator
from .api import VioletPoolAPI

# Diese Keys kommen aus unserem config_flow / OptionsFlow
CONF_API_URL = "base_ip"         # IP / Host
CONF_USE_SSL = "use_ssl"
CONF_DEVICE_ID = "device_id"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_DEVICE_NAME = "device_name"

CONF_POLLING_INTERVAL = "polling_interval"
CONF_TIMEOUT_DURATION = "timeout_duration"
CONF_RETRY_ATTEMPTS = "retry_attempts"

DEFAULT_POLLING_INTERVAL = 60
DEFAULT_TIMEOUT_DURATION = 10
DEFAULT_RETRY_ATTEMPTS = 3

PLATFORMS = ["sensor", "switch", "binary_sensor"]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setze einen Violet Pool Controller via Config Entry auf."""
    _LOGGER.info("Setting up Violet Pool Controller integration (entry_id=%s)", entry.entry_id)

    # 1) Zuerst alle relevanten Felder holen:
    #
    #    - IP, SSL, Username, Password, Device-ID, Device-Name
    #      kommen laut unserem Beispiel aus `entry.data`.
    #    - polling_interval, timeout_duration, retry_attempts
    #      können nachträglich über das OptionsFlow geändert werden => zuerst in `entry.options` gucken.

    # Basis-Infos (immer in entry.data, laut config_flow)
    ip_address = entry.data.get(CONF_API_URL, "127.0.0.1")
    use_ssl = entry.data.get(CONF_USE_SSL, True)
    device_id = entry.data.get(CONF_DEVICE_ID, 1)
    username = entry.data.get(CONF_USERNAME) or ""
    password = entry.data.get(CONF_PASSWORD) or ""
    device_name = entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller")

    # Options mit Fallback zu data
    polling_interval = int(
        entry.options.get(CONF_POLLING_INTERVAL, entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL))
    )
    timeout_duration = int(
        entry.options.get(CONF_TIMEOUT_DURATION, entry.data.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION))
    )
    retry_attempts = int(
        entry.options.get(CONF_RETRY_ATTEMPTS, entry.data.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS))
    )

    # 2) Erstelle ein Dictionary, das alle nötigen Werte bündelt
    config: Dict[str, Any] = {
        "ip_address": ip_address,
        "use_ssl": use_ssl,
        "device_id": device_id,
        "username": username,
        "password": password,
        "device_name": device_name,
        "polling_interval": polling_interval,
        "timeout": timeout_duration,
        "retries": retry_attempts,
    }

    sanitized_config = config.copy()
    sanitized_config["password"] = "****"
    _LOGGER.debug(
        "Final config (entry_id=%s) => %s",
        entry.entry_id,
        sanitized_config,
    )

    # 3) API und Coordinator erstellen
    session = aiohttp_client.async_get_clientsession(hass)

    api = VioletPoolAPI(
        host=config["ip_address"],
        username=config["username"],
        password=config["password"],
        use_ssl=config["use_ssl"],
        timeout=config["timeout"],
    )
    api.session = session

    coordinator = VioletDataUpdateCoordinator(
        hass=hass,
        config=config,
        api=api
    )

    # 4) Erster Datenabruf
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Erster Datenabruf fehlgeschlagen: %s", err)
        return False

    # 5) Integration-Objekt in hass.data speichern
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # 6) Plattformen initialisieren
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    )

    # 7) Beispiel-Service registrieren, z.B. Pumpe schalten
    async def async_handle_set_pump_state(call):
        """Service-Handler, um die Pumpe ein- oder auszuschalten."""
        pump_on = call.data.get("pump_on", True)
        try:
            await api.set_pump_state(pump_on)
            # Anschließend manuell refreshen
            await coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error("Fehler beim Setzen des Pumpen-Status: %s", e)

    hass.services.async_register(
        DOMAIN, "set_pump_state", async_handle_set_pump_state
    )

    _LOGGER.info("Violet Pool Controller Setup für '%s' (entry_id=%s) abgeschlossen", device_name, entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entferne einen Violet Pool Controller Config Entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        _LOGGER.info("Violet Pool Controller (Gerät %s) erfolgreich entladen", entry.entry_id)
    return unload_ok
