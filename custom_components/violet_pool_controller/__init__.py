"""Initialisierung der Violet Pool Controller Integration."""
import logging
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
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

# Plattformen, die diese Integration unterstützt
PLATFORMS = ["sensor", "switch", "binary_sensor", "cover", "number", "climate"]

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

    # 7) Services registrieren
    register_services(hass)

    _LOGGER.info("Violet Pool Controller Setup für '%s' (entry_id=%s) abgeschlossen", device_name, entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entferne einen Violet Pool Controller Config Entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        _LOGGER.info("Violet Pool Controller (Gerät %s) erfolgreich entladen", entry.entry_id)
    return unload_ok


def register_services(hass: HomeAssistant) -> None:
    """Registriere zusätzliche Services für die Integration."""
    
    # Service zum Einstellen der Solltemperatur
    async def async_handle_set_temperature_target(call: ServiceCall) -> None:
        """Service-Handler zum Einstellen der Solltemperatur."""
        entity_id = call.data.get("entity_id")
        temperature = call.data.get("temperature")
        
        # Suche nach der Entity
        entity = hass.states.get(entity_id)
        if not entity:
            _LOGGER.error("Entity nicht gefunden: %s", entity_id)
            return
            
        # Rufe die set_temperature-Methode der Entity auf
        await hass.services.async_call(
            "climate", "set_temperature",
            {"entity_id": entity_id, "temperature": temperature},
            blocking=True
        )
    
    # Service zum Einstellen des pH-Sollwerts
    async def async_handle_set_ph_target(call: ServiceCall) -> None:
        """Service-Handler zum Einstellen des pH-Sollwerts."""
        entity_id = call.data.get("entity_id")
        target_value = call.data.get("target_value")
        
        # Suche nach der Entity
        entity = hass.states.get(entity_id)
        if not entity:
            _LOGGER.error("Entity nicht gefunden: %s", entity_id)
            return
            
        # Rufe die set_value-Methode der Entity auf
        await hass.services.async_call(
            "number", "set_value",
            {"entity_id": entity_id, "value": target_value},
            blocking=True
        )
    
    # Service zum Auslösen einer Rückspülung
    async def async_handle_trigger_backwash(call: ServiceCall) -> None:
        """Service-Handler zum Auslösen einer Rückspülung."""
        entity_id = call.data.get("entity_id")
        duration = call.data.get("duration", 0)  # Optional: Dauer in Sekunden
        
        # Suche nach der Entity
        entity = hass.states.get(entity_id)
        if not entity:
            _LOGGER.error("Entity nicht gefunden: %s", entity_id)
            return
            
        # Rufe die turn_on-Methode der Entity auf
        await hass.services.async_call(
            "switch", "turn_on",
            {"entity_id": entity_id},
            blocking=True
        )
        
        # Wenn eine Dauer angegeben wurde, plane automatische Abschaltung
        if duration > 0:
            _LOGGER.info("Plane automatische Abschaltung nach %d Sekunden", duration)
            coordinator = None
            
            # Finde den richtigen Coordinator für die Entity
            for entry_id, coord in hass.data[DOMAIN].items():
                # Prüfe, ob die Entity zu diesem Coordinator gehört
                if entity_id.startswith(f"switch.{entry_id}") or entity_id.endswith(f"_{entry_id}"):
                    coordinator = coord
                    break
            
            if coordinator:
                import asyncio
                # Warte die angegebene Zeit
                await asyncio.sleep(duration)
                # Schalte die Entity aus
                await hass.services.async_call(
                    "switch", "turn_off",
                    {"entity_id": entity_id},
                    blocking=True
                )
    
    # Neuer Service: Wasseranalyse-Modus starten
    async def async_handle_start_water_analysis(call: ServiceCall) -> None:
        """Service-Handler zum Starten des Wasseranalyse-Modus."""
        entity_id = call.data.get("entity_id")  # Optional: Spezifische Entity für die Wasseranalyse
        
        # Finde den richtigen Coordinator
        coordinator = None
        for entry_id, coord in hass.data[DOMAIN].items():
            if entity_id:
                # Wenn entity_id angegeben, suche den passenden Coordinator
                if entity_id.startswith(f"sensor.{entry_id}") or entity_id.endswith(f"_{entry_id}"):
                    coordinator = coord
                    break
            else:
                # Wenn keine entity_id angegeben, verwende den ersten Coordinator
                coordinator = coord
                break
        
        if not coordinator:
            _LOGGER.error("Kein passender Coordinator gefunden")
            return
        
        try:
            # Starte den Wasseranalyse-Modus über die API
            # Da dieser API-Endpunkt möglicherweise nicht dokumentiert ist, ist dies ein Beispiel
            protocol = "https" if coordinator.api.use_ssl else "http"
            url = f"{protocol}://{coordinator.api.host}/startWaterAnalysis"
            
            auth = None
            if coordinator.api.username and coordinator.api.password:
                from aiohttp import BasicAuth
                auth = BasicAuth(coordinator.api.username, coordinator.api.password)
            
            async with coordinator.api.session.get(url, auth=auth, ssl=coordinator.api.use_ssl) as response:
                response.raise_for_status()
                response_text = await response.text()
                _LOGGER.info("Wasseranalyse gestartet. Antwort: %s", response_text)
                
            # Daten aktualisieren
            await coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Fehler beim Starten der Wasseranalyse: %s", err)
    
    # Neuer Service: Wartungsmodus ein-/ausschalten
    async def async_handle_set_maintenance_mode(call: ServiceCall) -> None:
        """Service-Handler zum Ein-/Ausschalten des Wartungsmodus."""
        entity_id = call.data.get("entity_id")  # Optional: Spezifische Entity
        enable = call.data.get("enable", True)  # True = aktivieren, False = deaktivieren
        
        # Finde den richtigen Coordinator
        coordinator = None
        for entry_id, coord in hass.data[DOMAIN].items():
            if entity_id:
                # Wenn entity_id angegeben, suche den passenden Coordinator
                if entity_id.startswith(f"switch.{entry_id}") or entity_id.endswith(f"_{entry_id}"):
                    coordinator = coord
                    break
            else:
                # Wenn keine entity_id angegeben, verwende den ersten Coordinator
                coordinator = coord
                break
        
        if not coordinator:
            _LOGGER.error("Kein passender Coordinator gefunden")
            return
        
        try:
            # Setze den Wartungsmodus über die API
            action = "ON" if enable else "OFF"
            await coordinator.api.set_switch_state
