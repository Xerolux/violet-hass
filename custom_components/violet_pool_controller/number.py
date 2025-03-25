"""Number Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, Optional, Final

from homeassistant.components.number import (
    NumberEntity,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN, 
    CONF_API_URL, 
    CONF_DEVICE_NAME,
    MANUFACTURER,
    INTEGRATION_VERSION,
)

_LOGGER = logging.getLogger(__name__)

# Sollwerte-Definitionen
SETPOINT_DEFINITIONS: Final = [
    {
        "key": "ph_setpoint",
        "name": "pH Sollwert",
        "min_value": 6.8,
        "max_value": 7.8,
        "step": 0.1,
        "icon": "mdi:flask",
        "api_key": "pH-",  # Für API-Aufrufe
        "parameter": "pH Sollwert",  # Parameter-Name in der API
        "unit_of_measurement": "pH",
        "api_endpoint": "setPHTarget",  # Endpunkt für die API
    },
    {
        "key": "chlorine_setpoint",
        "name": "Redox Sollwert",
        "min_value": 600,
        "max_value": 850,
        "step": 10,
        "icon": "mdi:flash",
        "api_key": "Chlor",  # Für API-Aufrufe
        "parameter": "Redox Sollwert",  # Parameter-Name in der API
        "unit_of_measurement": "mV",
        "api_endpoint": "setORPTarget",  # Endpunkt für die API
    },
    {
        "key": "min_chlorine_level",
        "name": "Min. Chlorgehalt",
        "min_value": 0.1,
        "max_value": 0.5,
        "step": 0.05,
        "icon": "mdi:test-tube",
        "api_key": "Chlor",  # Für API-Aufrufe
        "parameter": "Min. Chlorgehalt",  # Parameter-Name in der API
        "unit_of_measurement": "mg/l",
        "api_endpoint": "setMinChlorineLevel",  # Endpunkt für die API
    },
    {
        "key": "max_chlorine_level_day",
        "name": "Max. Chlorgehalt Tag",
        "min_value": 0.3,
        "max_value": 0.8,
        "step": 0.05,
        "icon": "mdi:test-tube",
        "api_key": "Chlor",  # Für API-Aufrufe
        "parameter": "Max. Chlorgehalt Tag",  # Parameter-Name in der API
        "unit_of_measurement": "mg/l",
        "api_endpoint": "setMaxChlorineLevelDay",  # Endpunkt für die API
    },
    {
        "key": "max_chlorine_level_night",
        "name": "Max. Chlorgehalt Nacht",
        "min_value": 0.5,
        "max_value": 1.2,
        "step": 0.05,
        "icon": "mdi:test-tube",
        "api_key": "Chlor",  # Für API-Aufrufe
        "parameter": "Max. Chlorgehalt Nacht",  # Parameter-Name in der API
        "unit_of_measurement": "mg/l",
        "api_endpoint": "setMaxChlorineLevelNight",  # Endpunkt für die API
    },
]


class VioletNumberEntity(CoordinatorEntity, NumberEntity):
    """Repräsentiert einen Sollwert im Violet Pool Controller."""

    def __init__(
        self,
        coordinator,
        config_entry: ConfigEntry,
        definition: Dict[str, Any],
    ):
        """Initialisiere die Number-Entity."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._definition = definition
        device_name = config_entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        
        self._attr_name = f"{device_name} {definition['name']}"
        self._attr_unique_id = f"{config_entry.entry_id}_{definition['key']}"
        self._attr_icon = definition.get("icon")
        self._attr_native_min_value = definition.get("min_value")
        self._attr_native_max_value = definition.get("max_value")
        self._attr_native_step = definition.get("step")
        self._attr_mode = NumberMode.AUTO  # oder NumberMode.SLIDER
        
        if "unit_of_measurement" in definition:
            self._attr_native_unit_of_measurement = definition["unit_of_measurement"]
        
        # Tatsächlicher Wert kommt aus der API, hier setzen wir nur einen Standard
        self._attr_native_value = self._get_current_value()
        
        self.ip_address = config_entry.data.get(CONF_API_URL, "Unknown IP")
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"{device_name} ({self.ip_address})",
            "manufacturer": MANUFACTURER,
            "model": f"Violet Model X (v{INTEGRATION_VERSION})",
            "sw_version": coordinator.data.get("fw", INTEGRATION_VERSION),
            "configuration_url": f"http://{self.ip_address}",
        }

    def _get_current_value(self) -> Optional[float]:
        """Ermittle den aktuellen Wert aus den Coordinator-Daten."""
        key = self._definition["key"]
        
        # Mapping der Keys zu den tatsächlichen API-Datenfeldern
        key_to_data_field = {
            "ph_setpoint": "pH_SETPOINT",
            "chlorine_setpoint": "REDOX_SETPOINT",
            "min_chlorine_level": "MIN_CHLORINE_LEVEL",
            "max_chlorine_level_day": "MAX_CHLORINE_LEVEL_DAY",
            "max_chlorine_level_night": "MAX_CHLORINE_LEVEL_NIGHT",
        }
        
        # Default-Werte für den Fall, dass die Daten nicht verfügbar sind
        default_values = {
            "ph_setpoint": 7.2,
            "chlorine_setpoint": 750,
            "min_chlorine_level": 0.2,
            "max_chlorine_level_day": 0.5,
            "max_chlorine_level_night": 0.8,
        }
        
        # Versuche den Wert aus den Koordinator-Daten zu bekommen
        data_field = key_to_data_field.get(key)
        if data_field and data_field in self.coordinator.data:
            try:
                return float(self.coordinator.data[data_field])
            except (ValueError, TypeError) as err:
                _LOGGER.warning(f"Konnte Wert für {key} nicht umwandeln: {err}")
        
        # Fallback zu Default-Wert
        _LOGGER.debug(f"Verwende Standard-Wert für {key}: {default_values.get(key)}")
        return default_values.get(key, self._attr_native_min_value)

    async def async_set_native_value(self, value: float) -> None:
        """Setze den neuen Wert im Gerät."""
        try:
            api_key = self._definition.get("api_key")
            parameter = self._definition.get("parameter")
            api_endpoint = self._definition.get("api_endpoint")
            
            if not api_key or not parameter or not api_endpoint:
                _LOGGER.error("Fehler: API-Key, Parameter oder Endpunkt nicht definiert")
                return
                
            _LOGGER.info(
                "Setze Sollwert für %s (%s): %s = %f",
                self.name,
                api_key,
                parameter,
                value
            )
            
            # Konstruiere die API-Anfrage basierend auf dem Sollwert-Typ
            # Verschiedene Endpunkte erfordern unterschiedliche Parameter
            
            # Allgemeine Implementation für Sollwert-Änderungen
            # Jeder Endpunkt kann andere Parameter erwarten, daher müssen wir anpassen
            
            if api_endpoint == "setPHTarget":
                # pH-Sollwert setzen
                await self._set_ph_target(value)
            elif api_endpoint == "setORPTarget":
                # Redox-Sollwert setzen
                await self._set_orp_target(value)
            elif api_endpoint in ["setMinChlorineLevel", "setMaxChlorineLevelDay", "setMaxChlorineLevelNight"]:
                # Chlor-Sollwerte setzen
                await self._set_chlorine_target(api_endpoint, value)
            else:
                # Generischer Ansatz für andere Parameter
                await self._set_generic_parameter(api_key, parameter, value)
            
            # Aktualisiere den lokalen Wert ohne auf den Coordinator zu warten
            self._attr_native_value = value
            self.async_write_ha_state()
            
            # Aktualisiere die Daten vom Gerät
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Fehler beim Setzen des Sollwerts: %s", err)
    
    async def _set_ph_target(self, value: float) -> None:
        """Setze den pH-Sollwert über die API."""
        try:
            # Verwendung des in der API implementierten Services
            protocol = "https" if self.coordinator.api.use_ssl else "http"
            url = f"{protocol}://{self.coordinator.api.host}/setPHTarget?{value}"
            
            auth = None
            if self.coordinator.api.username and self.coordinator.api.password:
                from aiohttp import BasicAuth
                auth = BasicAuth(self.coordinator.api.username, self.coordinator.api.password)
            
            async with self.coordinator.api.session.get(
                url, auth=auth, ssl=self.coordinator.api.use_ssl
            ) as response:
                response.raise_for_status()
                response_text = await response.text()
                _LOGGER.debug(f"pH-Sollwert gesetzt. API-Antwort: {response_text}")
                return response_text
        except Exception as err:
            _LOGGER.error(f"Fehler beim Setzen des pH-Sollwerts: {err}")
            raise
    
    async def _set_orp_target(self, value: float) -> None:
        """Setze den Redox-Sollwert über die API."""
        try:
            # Verwendung des in der API implementierten Services
            protocol = "https" if self.coordinator.api.use_ssl else "http"
            url = f"{protocol}://{self.coordinator.api.host}/setORPTarget?{value}"
            
            auth = None
            if self.coordinator.api.username and self.coordinator.api.password:
                from aiohttp import BasicAuth
                auth = BasicAuth(self.coordinator.api.username, self.coordinator.api.password)
            
            async with self.coordinator.api.session.get(
                url, auth=auth, ssl=self.coordinator.api.use_ssl
            ) as response:
                response.raise_for_status()
                response_text = await response.text()
                _LOGGER.debug(f"Redox-Sollwert gesetzt. API-Antwort: {response_text}")
                return response_text
        except Exception as err:
            _LOGGER.error(f"Fehler beim Setzen des Redox-Sollwerts: {err}")
            raise
    
    async def _set_chlorine_target(self, endpoint: str, value: float) -> None:
        """Setze Chlor-bezogene Sollwerte über die API."""
        try:
            # Verwendung des in der API implementierten Services
            protocol = "https" if self.coordinator.api.use_ssl else "http"
            url = f"{protocol}://{self.coordinator.api.host}/{endpoint}?{value}"
            
            auth = None
            if self.coordinator.api.username and self.coordinator.api.password:
                from aiohttp import BasicAuth
                auth = BasicAuth(self.coordinator.api.username, self.coordinator.api.password)
            
            async with self.coordinator.api.session.get(
                url, auth=auth, ssl=self.coordinator.api.use_ssl
            ) as response:
                response.raise_for_status()
                response_text = await response.text()
                _LOGGER.debug(f"Chlor-Parameter gesetzt. API-Antwort: {response_text}")
                return response_text
        except Exception as err:
            _LOGGER.error(f"Fehler beim Setzen des Chlor-Parameters: {err}")
            raise
    
    async def _set_generic_parameter(self, api_key: str, parameter: str, value: float) -> None:
        """Generischer Ansatz zum Setzen von Parametern über die API."""
        try:
            # Verwendung der dosingParameters-Methode als Fallback
            # Diese Methode muss in api.py implementiert sein
            if hasattr(self.coordinator.api, 'set_dosing_parameters'):
                await self.coordinator.api.set_dosing_parameters(
                    dosing_type=api_key,
                    parameter_name=parameter,
                    value=value
                )
            else:
                _LOGGER.error("Die Methode set_dosing_parameters ist nicht in der API implementiert")
        except Exception as err:
            _LOGGER.error(f"Fehler beim Setzen des Parameters {parameter}: {err}")
            raise


async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
):
    """Richte Number-Entities basierend auf dem Config-Entry ein."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Überprüfe, ob die API Dosierungsfunktionen unterstützt
    # Dies ist eine detailliertere Prüfung basierend auf den API-Daten
    has_dosing_functions = False
    
    # Prüfe verschiedene Indikatoren für Dosierungsfunktionen
    dosing_indicators = [
        "DOS_1_CL", "DOS_4_PHM", "DOS_5_PHP", "pH_SETPOINT", "REDOX_SETPOINT",
        "MIN_CHLORINE_LEVEL", "MAX_CHLORINE_LEVEL_DAY", "MAX_CHLORINE_LEVEL_NIGHT"
    ]
    
    for indicator in dosing_indicators:
        if indicator in coordinator.data:
            has_dosing_functions = True
            break
    
    if not has_dosing_functions:
        _LOGGER.info("Keine Dosierungsfunktionen in den API-Daten gefunden, Number-Entities werden nicht hinzugefügt")
        return
    
    # Erstelle Number-Entities für alle Definitionen
    entities = []
    for definition in SETPOINT_DEFINITIONS:
        # Spezifischere Prüfung für jede Definition
        # Prüfe, ob relevante Daten in der API vorhanden sind
        key_to_check = {
            "ph_setpoint": ["pH_value", "pH_SETPOINT"],
            "chlorine_setpoint": ["orp_value", "REDOX_SETPOINT"],
            "min_chlorine_level": ["CHLORINE_LEVEL", "MIN_CHLORINE_LEVEL"],
            "max_chlorine_level_day": ["CHLORINE_LEVEL", "MAX_CHLORINE_LEVEL_DAY"],
            "max_chlorine_level_night": ["CHLORINE_LEVEL", "MAX_CHLORINE_LEVEL_NIGHT"],
        }
        
        # Wenn mindestens ein relevanter Indikator vorhanden ist, füge die Entity hinzu
        should_add = False
        for indicator in key_to_check.get(definition["key"], []):
            if indicator in coordinator.data:
                should_add = True
                break
        
        if should_add:
            entities.append(VioletNumberEntity(coordinator, config_entry, definition))
            _LOGGER.debug(f"Number-Entity für {definition['name']} hinzugefügt")
        else:
            _LOGGER.debug(f"Number-Entity für {definition['name']} wird übersprungen (keine relevanten Daten)")
    
    if entities:
        _LOGGER.info(f"{len(entities)} Number-Entities für Sollwerte hinzugefügt")
        async_add_entities(entities)
    else:
        _LOGGER.warning("Keine passenden Sollwert-Entities in den API-Daten gefunden")
