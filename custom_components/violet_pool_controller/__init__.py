"""Initialisierung der Violet Pool Controller Integration."""
import logging
import asyncio
from typing import Any, Dict, List, Set, Final, Optional, cast

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import aiohttp_client
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
from .api import VioletPoolAPI
from .device import async_setup_device, VioletPoolDataUpdateCoordinator

# Plattformen, die diese Integration unterstützt
PLATFORMS: Final[List[str]] = [
    "sensor", 
    "binary_sensor", 
    "switch", 
    "climate", 
    "cover", 
    "number"
]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Richte die Violet Pool Controller Integration ein (YAML-Konfiguration).
    
    Diese Funktion wird aufgerufen, wenn die Integration über YAML konfiguriert wird,
    was in neueren Home Assistant Versionen nicht mehr empfohlen wird.
    
    Args:
        hass: Die Home Assistant Instanz
        config: Die YAML-Konfiguration
        
    Returns:
        bool: True, wenn das Setup erfolgreich war
    """
    # YAML-Konfiguration bieten wir nicht an, aber wir könnten einen Hinweis geben
    if DOMAIN in config:
        _LOGGER.warning(
            "Die YAML-Konfiguration für %s ist nicht unterstützt. "
            "Bitte nutze stattdessen die UI-Konfiguration (Einstellungen -> Integrationen).",
            DOMAIN
        )
    
    # Domain-Daten initialisieren
    hass.data.setdefault(DOMAIN, {})
    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setze einen Violet Pool Controller via Config Entry auf.
    
    Diese Funktion wird aufgerufen, wenn die Integration über die UI eingerichtet wird.
    
    Args:
        hass: Die Home Assistant Instanz
        entry: Der Config Entry
        
    Returns:
        bool: True, wenn das Setup erfolgreich war
    """
    _LOGGER.info("Setting up Violet Pool Controller integration (entry_id=%s)", entry.entry_id)

    # 1) Hole alle relevanten Konfigurationsfelder

    # Basis-Infos (immer in entry.data, laut config_flow)
    ip_address = entry.data.get(CONF_API_URL, "127.0.0.1")
    use_ssl = entry.data.get(CONF_USE_SSL, True)
    device_id = entry.data.get(CONF_DEVICE_ID, 1)
    username = entry.data.get(CONF_USERNAME) or ""
    password = entry.data.get(CONF_PASSWORD) or ""
    device_name = entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller")

    # Options mit Fallback zu data
    polling_interval = int(
        entry.options.get(
            CONF_POLLING_INTERVAL, 
            entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
        )
    )
    timeout_duration = int(
        entry.options.get(
            CONF_TIMEOUT_DURATION, 
            entry.data.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION)
        )
    )
    retry_attempts = int(
        entry.options.get(
            CONF_RETRY_ATTEMPTS, 
            entry.data.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS)
        )
    )
    
    # Aktive Features
    active_features = entry.options.get(
        CONF_ACTIVE_FEATURES, 
        entry.data.get(CONF_ACTIVE_FEATURES, [])
    )

    # Konfiguration für Logging (ohne sensible Daten)
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
    
    _LOGGER.debug(
        "Final config (entry_id=%s) => %s",
        entry.entry_id,
        sanitized_config,
    )

    # 2) API und Coordinator erstellen
    try:
        # aiohttp Session erstellen
        session = aiohttp_client.async_get_clientsession(hass)

        # API-Instanz erstellen
        api = VioletPoolAPI(
            host=ip_address,
            session=session,
            username=username,
            password=password,
            use_ssl=use_ssl,
            timeout=timeout_duration,
        )

        # Gerät und Coordinator erstellen
        coordinator = await async_setup_device(hass, entry)
        
        if not coordinator:
            _LOGGER.error(
                "Fehler beim Einrichten des Violet Pool Controllers: "
                "Coordinator konnte nicht erstellt werden"
            )
            return False
            
        # Integration-Objekt in hass.data speichern
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = coordinator

        # Plattformen initialisieren
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        # Services registrieren
        register_services(hass)

        # Erfolgsmeldung
        _LOGGER.info(
            "Violet Pool Controller Setup für '%s' (entry_id=%s) abgeschlossen", 
            device_name, 
            entry.entry_id
        )
        
        return True
        
    except Exception as err:
        _LOGGER.exception(
            "Fehler beim Einrichten des Violet Pool Controllers (entry_id=%s): %s",
            entry.entry_id,
            err
        )
        raise HomeAssistantError(
            f"Fehler beim Einrichten des Violet Pool Controllers: {err}"
        ) from err


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entferne einen Violet Pool Controller Config Entry.
    
    Args:
        hass: Die Home Assistant Instanz
        entry: Der Config Entry
        
    Returns:
        bool: True, wenn das Entladen erfolgreich war
    """
    try:
        # Plattformen entladen
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
        
        if unload_ok:
            # Coordinator aus hass.data entfernen
            if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
                coordinator = hass.data[DOMAIN].pop(entry.entry_id)
                
                # Falls weitere Aufräumaktionen für den Coordinator nötig sind
                # (keine in diesem Fall, da async_shutdown in Zukunft automatisch aufgerufen wird)
                
                _LOGGER.info(
                    "Violet Pool Controller '%s' (entry_id=%s) erfolgreich entladen",
                    entry.data.get(CONF_DEVICE_NAME, "Unbekannt"),
                    entry.entry_id
                )
                
        return unload_ok
        
    except Exception as err:
        _LOGGER.exception(
            "Fehler beim Entladen von Violet Pool Controller (entry_id=%s): %s",
            entry.entry_id,
            err
        )
        return False


def register_services(hass: HomeAssistant) -> None:
    """Registriere zusätzliche Services für die Integration.
    
    Args:
        hass: Die Home Assistant Instanz
    """
    # Prüfen, ob Services bereits registriert sind (z.B. bei mehreren Geräten)
    if hass.services.has_service(DOMAIN, "set_temperature_target"):
        _LOGGER.debug("Services für %s sind bereits registriert", DOMAIN)
        return
        
    # Service-Schema für set_temperature_target
    SET_TEMPERATURE_TARGET_SCHEMA = vol.Schema({
        vol.Required("entity_id"): cv.entity_id,
        vol.Required("temperature"): vol.All(vol.Coerce(float), vol.Range(min=20, max=40)),
    })
    
    # Service-Schema für set_ph_target
    SET_PH_TARGET_SCHEMA = vol.Schema({
        vol.Required("entity_id"): cv.entity_id,
        vol.Required("target_value"): vol.All(vol.Coerce(float), vol.Range(min=6.8, max=7.8)),
    })
    
    # Service-Schema für set_chlorine_target
    SET_CHLORINE_TARGET_SCHEMA = vol.Schema({
        vol.Required("entity_id"): cv.entity_id,
        vol.Required("target_value"): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=3.0)),
    })
    
    # Service-Schema für trigger_backwash
    TRIGGER_BACKWASH_SCHEMA = vol.Schema({
        vol.Required("entity_id"): cv.entity_id,
        vol.Optional("duration", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=900)),
    })
    
    # Service-Schema für start_water_analysis
    START_WATER_ANALYSIS_SCHEMA = vol.Schema({
        vol.Optional("entity_id"): cv.entity_id,
    })
    
    # Service-Schema für set_maintenance_mode
    SET_MAINTENANCE_MODE_SCHEMA = vol.Schema({
        vol.Optional("entity_id"): cv.entity_id,
        vol.Optional("enable", default=True): cv.boolean,
    })
    
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
            
        try:
            # Rufe die set_temperature-Methode der Entity auf
            await hass.services.async_call(
                "climate", "set_temperature",
                {"entity_id": entity_id, "temperature": temperature},
                blocking=True
            )
            _LOGGER.info(
                "Zieltemperatur für %s auf %.1f°C gesetzt",
                entity_id,
                temperature
            )
        except Exception as err:
            _LOGGER.error(
                "Fehler beim Setzen der Zieltemperatur für %s: %s",
                entity_id,
                err
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
            
        try:
            # Rufe die set_value-Methode der Entity auf
            await hass.services.async_call(
                "number", "set_value",
                {"entity_id": entity_id, "value": target_value},
                blocking=True
            )
            _LOGGER.info(
                "pH-Sollwert für %s auf %.1f gesetzt",
                entity_id,
                target_value
            )
        except Exception as err:
            _LOGGER.error(
                "Fehler beim Setzen des pH-Sollwerts für %s: %s",
                entity_id,
                err
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
            
        try:
            # Rufe die turn_on-Methode der Entity auf
            await hass.services.async_call(
                "switch", "turn_on",
                {"entity_id": entity_id},
                blocking=True
            )
            
            _LOGGER.info("Rückspülung für %s gestartet", entity_id)
            
            # Wenn eine Dauer angegeben wurde, plane automatische Abschaltung
            if duration > 0:
                _LOGGER.info(
                    "Plane automatische Abschaltung nach %d Sekunden",
                    duration
                )
                
                # Verzögerte Ausschaltung
                async def delayed_turn_off() -> None:
                    """Verzögerte Ausschaltung des Switches."""
                    try:
                        await asyncio.sleep(duration)
                        await hass.services.async_call(
                            "switch", "turn_off",
                            {"entity_id": entity_id},
                            blocking=True
                        )
                        _LOGGER.info(
                            "Rückspülung für %s nach %d Sekunden automatisch beendet",
                            entity_id,
                            duration
                        )
                    except Exception as err:
                        _LOGGER.error(
                            "Fehler bei automatischer Abschaltung von %s: %s",
                            entity_id,
                            err
                        )
                
                # Starte die verzögerte Ausschaltung als Task
                hass.async_create_task(delayed_turn_off())
                
        except Exception as err:
            _LOGGER.error(
                "Fehler beim Starten der Rückspülung für %s: %s",
                entity_id,
                err
            )
    
    # Service zum Starten des Wasseranalyse-Modus
    async def async_handle_start_water_analysis(call: ServiceCall) -> None:
        """Service-Handler zum Starten des Wasseranalyse-Modus."""
        entity_id = call.data.get("entity_id")  # Optional: Spezifische Entity
        
        # Finde den Coordinator basierend auf der Entity-ID oder nutze den ersten
        coordinator = _get_coordinator_for_entity(hass, entity_id)
        
        if not coordinator:
            _LOGGER.error(
                "Kein passender Coordinator für %s gefunden",
                entity_id or "alle Geräte"
            )
            return
        
        try:
            # Starte den Wasseranalyse-Modus über die Device-API
            result = await coordinator.device.async_send_command(
                endpoint="/startWaterAnalysis",
                command={}
            )
            
            # Prüfe das Ergebnis
            if isinstance(result, dict) and result.get("success", False):
                _LOGGER.info("Wasseranalyse erfolgreich gestartet")
            else:
                _LOGGER.warning(
                    "Wasseranalyse möglicherweise nicht erfolgreich gestartet: %s",
                    result
                )
                
            # Daten aktualisieren
            await coordinator.async_request_refresh()
            
        except Exception as err:
            _LOGGER.error("Fehler beim Starten der Wasseranalyse: %s", err)
    
    # Service zum Ein-/Ausschalten des Wartungsmodus
    async def async_handle_set_maintenance_mode(call: ServiceCall) -> None:
        """Service-Handler zum Ein-/Ausschalten des Wartungsmodus."""
        entity_id = call.data.get("entity_id")  # Optional: Spezifische Entity
        enable = call.data.get("enable", True)  # True = aktivieren, False = deaktivieren
        
        # Finde den Coordinator basierend auf der Entity-ID oder nutze den ersten
        coordinator = _get_coordinator_for_entity(hass, entity_id)
        
        if not coordinator:
            _LOGGER.error(
                "Kein passender Coordinator für %s gefunden",
                entity_id or "alle Geräte"
            )
            return
        
        try:
            # Setze den Wartungsmodus über die Device-API
            result = await coordinator.device.async_send_command(
                endpoint="/set_switch",
                command={
                    "id": "MAINTENANCE",
                    "action": "ON" if enable else "OFF",
                    "duration": 0,
                    "value": 0
                }
            )
            
            # Prüfe das Ergebnis
            if isinstance(result, dict) and result.get("success", False):
                _LOGGER.info(
                    "Wartungsmodus erfolgreich auf %s gesetzt",
                    "EIN" if enable else "AUS"
                )
            else:
                _LOGGER.warning(
                    "Wartungsmodus möglicherweise nicht erfolgreich gesetzt: %s",
                    result
                )
                
            # Daten aktualisieren
            await coordinator.async_request_refresh()
            
        except Exception as err:
            _LOGGER.error(
                "Fehler beim Setzen des Wartungsmodus auf %s: %s",
                "EIN" if enable else "AUS",
                err
            )
    
    # Service zum Einstellen des Chlor-Sollwerts
    async def async_handle_set_chlorine_target(call: ServiceCall) -> None:
        """Service-Handler zum Einstellen des Chlor-Sollwerts."""
        entity_id = call.data.get("entity_id")
        target_value = call.data.get("target_value")
        
        # Suche nach der Entity
        entity = hass.states.get(entity_id)
        if not entity:
            _LOGGER.error("Entity nicht gefunden: %s", entity_id)
            return
            
        try:
            # Rufe die set_value-Methode der Entity auf
            await hass.services.async_call(
                "number", "set_value",
                {"entity_id": entity_id, "value": target_value},
                blocking=True
            )
            _LOGGER.info(
                "Chlor-Sollwert für %s auf %.1f mg/l gesetzt",
                entity_id,
                target_value
            )
        except Exception as err:
            _LOGGER.error(
                "Fehler beim Setzen des Chlor-Sollwerts für %s: %s",
                entity_id,
                err
            )
    
    # Registriere die Services mit Schema
    hass.services.async_register(
        DOMAIN, 
        "set_temperature_target", 
        async_handle_set_temperature_target,
        schema=SET_TEMPERATURE_TARGET_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, 
        "set_ph_target", 
        async_handle_set_ph_target,
        schema=SET_PH_TARGET_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, 
        "set_chlorine_target", 
        async_handle_set_chlorine_target,
        schema=SET_CHLORINE_TARGET_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, 
        "trigger_backwash", 
        async_handle_trigger_backwash,
        schema=TRIGGER_BACKWASH_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, 
        "start_water_analysis", 
        async_handle_start_water_analysis,
        schema=START_WATER_ANALYSIS_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, 
        "set_maintenance_mode", 
        async_handle_set_maintenance_mode,
        schema=SET_MAINTENANCE_MODE_SCHEMA
    )
    
    _LOGGER.info("Services für %s registriert", DOMAIN)


def _get_coordinator_for_entity(
    hass: HomeAssistant, 
    entity_id: Optional[str] = None
) -> Optional[VioletPoolDataUpdateCoordinator]:
    """Finde den passenden Coordinator für eine Entity-ID.
    
    Args:
        hass: Die Home Assistant Instanz
        entity_id: Die Entity-ID (optional)
        
    Returns:
        Optional[VioletPoolDataUpdateCoordinator]: Der passende Coordinator oder None
    """
    if DOMAIN not in hass.data or not hass.data[DOMAIN]:
        return None
        
    if not entity_id:
        # Wenn keine Entity-ID angegeben, verwende den ersten Coordinator
        return next(iter(hass.data[DOMAIN].values()), None)
        
    # Extrahiere den Config Entry aus der Entity-ID
    for entry_id, coordinator in hass.data[DOMAIN].items():
        # Prüfe verschiedene Möglichkeiten, wie die Entity-ID zum Coordinator passen könnte
        if (
            entity_id.startswith(f"{DOMAIN}.{entry_id}_") or
            entity_id.endswith(f"_{entry_id}") or
            entry_id in entity_id
        ):
            return coordinator
            
    # Falls kein passender Coordinator gefunden wurde
    return None


@callback
def async_get_device_by_entity_id(
    hass: HomeAssistant, 
    entity_id: str
) -> Optional[Any]:
    """Hilfsfunktion zum Abrufen des Geräts anhand einer Entity-ID.
    
    Args:
        hass: Die Home Assistant Instanz
        entity_id: Die Entity-ID
        
    Returns:
        Optional[Any]: Das Gerät oder None
    """
    coordinator = _get_coordinator_for_entity(hass, entity_id)
    if not coordinator:
        return None
        
    return coordinator.device
