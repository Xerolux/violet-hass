import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
import async_timeout
import aiohttp

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
    API_READINGS
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Violet Pool Controller from a config entry."""

    # Konfigurationsdaten aus dem Config Entry abrufen
    config = {
        "ip_address": entry.data[CONF_API_URL],
        "polling_interval": entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL),
        "use_ssl": entry.data.get(CONF_USE_SSL, DEFAULT_USE_SSL),
        "device_id": entry.data.get(CONF_DEVICE_ID, 1),
        "username": entry.data.get(CONF_USERNAME),
        "password": entry.data.get(CONF_PASSWORD)
    }

    # Konfigurationsdaten protokollieren
    _LOGGER.info(f"Einrichtung des Violet Pool Controllers mit Konfiguration: {config}")

    # Gemeinsame aiohttp Session erhalten
    session = aiohttp_client.async_get_clientsession(hass)

    # Erstellen eines Coordinators für Datenaktualisierungen
    coordinator = VioletDataUpdateCoordinator(
        hass,
        config=config,
        session=session,
    )

    # Vor dem ersten Datenabruf protokollieren
    _LOGGER.debug("Erster Datenabruf für Violet Pool Controller wird durchgeführt")

    try:
        # Sicherstellen, dass der erste Datenabruf während der Einrichtung erfolgt
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error(f"Erster Datenabruf fehlgeschlagen: {err}")
        return False

    # Speichern des Coordinators in hass.data für den Zugriff durch Plattformdateien
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Weiterleitung der Einrichtung an Plattformen (z.B. Schalter)
    await hass.config_entries.async_forward_entry_setups(entry, ["switch", "sensor", "binary_sensor"])

    _LOGGER.info("Einrichtung des Violet Pool Controllers erfolgreich abgeschlossen")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entladen eines Config Entries."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["switch", "sensor", "binary_sensor"]
    )

    # Entfernen des Coordinators aus hass.data
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    _LOGGER.info(f"Violet Pool Controller (Gerät {entry.entry_id}) erfolgreich entladen")
    return unload_ok


class VioletDataUpdateCoordinator(DataUpdateCoordinator):
    """Klasse zum Verwalten des Abrufs von Violet Pool Controller Daten."""

    def __init__(self, hass, config, session):
        """Initialisierung des Coordinators."""
        self.ip_address = config["ip_address"]
        self.username = config["username"]
        self.password = config["password"]
        self.session = session
        self.use_ssl = config["use_ssl"]
        self.device_id = config["device_id"]

        _LOGGER.info(f"Initialisierung des Daten-Coordinators für Gerät {self.device_id} (IP: {self.ip_address}, SSL: {self.use_ssl})")

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.device_id}",
            update_interval=timedelta(seconds=config["polling_interval"]),
        )

    async def _async_update_data(self):
        """Abrufen von Daten von der Violet Pool Controller API."""
        try:
            protocol = "https" if self.use_ssl else "http"
            url = f"{protocol}://{self.ip_address}{API_READINGS}"
            _LOGGER.debug(f"Abrufen von Daten von: {url}")

            auth = aiohttp.BasicAuth(self.username, self.password)

            async with async_timeout.timeout(10):
                async with self.session.get(url, auth=auth, ssl=self.use_ssl) as response:
                    response.raise_for_status()
                    data = await response.json()
                    _LOGGER.debug(f"Daten empfangen: {data}")
                    return data
        except Exception as err:
            _LOGGER.error(f"Fehler beim Abrufen von Daten von {self.ip_address}: {err}")
            raise UpdateFailed(f"Fehler beim Abrufen von Daten: {err}")
