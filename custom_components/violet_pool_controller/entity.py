"""Violet Pool Controller Entity Module."""
import logging
from typing import Any, Dict, Optional, Union, Callable, List, cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityDescription
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_DEVICE_NAME,
    CONF_API_URL,
    CONF_POLLING_INTERVAL,
    CONF_ACTIVE_FEATURES,
)
from .device import VioletPoolDataUpdateCoordinator, VioletPoolControllerDevice

_LOGGER = logging.getLogger(__name__)


class VioletPoolControllerEntity(CoordinatorEntity):
    """Basisklasse für eine Violet Pool Controller Entität."""

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        entity_description: EntityDescription,
    ) -> None:
        """Initialisiere die Entität.
        
        Args:
            coordinator: Der Daten-Koordinator
            config_entry: Die Config Entry des Geräts
            entity_description: Die Beschreibung der Entität
        """
        super().__init__(coordinator)
        
        # Grundlegende Entitätsinformationen
        self.config_entry = config_entry
        self.entity_description = entity_description
        self.coordinator = coordinator  # Typisierter Zugriff auf den Coordinator
        self.device: VioletPoolControllerDevice = coordinator.device  # Zugriff auf Gerät
        
        # Name und ID
        self._attr_has_entity_name = True  # Nutze HA's Entity-Namenskonvention
        self._attr_name = entity_description.name
        self._attr_unique_id = f"{config_entry.entry_id}_{entity_description.key}"
        
        # Zustand und Verfügbarkeit
        self._attr_state = None
        self._attr_available = True  # Initial als verfügbar annehmen
        
        # Konfigurationsdaten für einfachen Zugriff
        self.api_url = config_entry.data.get(CONF_API_URL)
        self.polling_interval = config_entry.data.get(CONF_POLLING_INTERVAL)
        self.active_features = config_entry.options.get(
            CONF_ACTIVE_FEATURES, 
            config_entry.data.get(CONF_ACTIVE_FEATURES, [])
        )
        
        # Eigener Logger für diese Entität
        self._logger = logging.getLogger(f"{DOMAIN}.{self._attr_unique_id}")
        self._logger.info("Initialisiere Entität: %s", self.entity_id)

        # Geräteinformationen vom Geräteobjekt übernehmen
        self._attr_device_info = self.device.device_info

    @property
    def available(self) -> bool:
        """Gibt an, ob die Entität verfügbar ist.
        
        Prüft drei Bedingungen:
        1. Die Entität selbst ist verfügbar
        2. Der Coordinator hat erfolgreiche Aktualisierungen
        3. Das entsprechende Feature ist aktiv (falls zutreffend)
        
        Returns:
            bool: True, wenn die Entität verfügbar ist, sonst False
        """
        feature_available = True
        
        # Prüfe, ob diese Entität ein Feature benötigt
        if hasattr(self.entity_description, "feature_id"):
            feature_id = getattr(self.entity_description, "feature_id")
            feature_available = self.device.is_feature_active(feature_id)
            
        return (
            self._attr_available and 
            self.coordinator.last_update_success and
            feature_available
        )

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Gibt zusätzliche Zustandsattribute zurück.
        
        Returns:
            Dict[str, Any]: Die zusätzlichen Attribute
        """
        attributes = {
            "polling_interval": self.polling_interval,
            "api_url": self.api_url,
            "last_updated": self.coordinator.last_update_success,
        }
        
        # Füge feature_id hinzu, falls vorhanden
        if hasattr(self.entity_description, "feature_id"):
            attributes["feature_id"] = getattr(self.entity_description, "feature_id")
            
        return attributes

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator.
        
        Diese Methode wird automatisch aufgerufen, wenn der Coordinator
        neue Daten hat.
        """
        try:
            if self.coordinator.data:
                self._update_from_coordinator()
                self._attr_available = True
                self._logger.debug(
                    "Aktualisiert %s, neuer Zustand: %s", 
                    self.entity_id, 
                    self._attr_state
                )
            else:
                self._attr_available = False
                self._logger.warning(
                    "Keine Daten vom Coordinator für %s verfügbar.", 
                    self.entity_id
                )
        except Exception as err:
            self._attr_available = False
            self._logger.error(
                "Fehler bei der Aktualisierung von %s: %s", 
                self.entity_id, 
                err
            )
            
        # Aktualisiere die Entität in Home Assistant
        self.async_write_ha_state()

    def _update_from_coordinator(self) -> None:
        """Aktualisiert den Zustand der Entität anhand der Coordinator-Daten.
        
        Diese Methode kann in Unterklassen überschrieben werden, um
        spezifischere Aktualisierungslogik zu implementieren.
        """
        self._update_state_from_key(self.entity_description.key)

    def _update_state_from_key(self, key: str) -> None:
        """Aktualisiert den Zustand der Entität anhand eines Schlüssels.
        
        Args:
            key: Der Schlüssel in den Coordinator-Daten
        """
        if not self.coordinator.data:
            self._attr_available = False
            return
            
        data = self.coordinator.data
        
        try:
            if key in data:
                new_value = data[key]
                if new_value is not None:
                    # Aktualisiere den Zustand
                    self._attr_state = new_value
                    self._attr_available = True
                else:
                    self._logger.warning(
                        "Schlüssel %s hat einen None-Wert in den Daten.", 
                        key
                    )
                    self._attr_available = False
            else:
                # Schlüssel nicht gefunden, spezielle Behandlung für zusammengesetzte Schlüssel
                composite_keys = self._get_composite_keys(key)
                if composite_keys:
                    for composite_key in composite_keys:
                        if composite_key in data:
                            self._attr_state = data[composite_key]
                            self._attr_available = True
                            return
                
                # Kein passender Schlüssel gefunden
                self._logger.warning(
                    "Schlüssel %s nicht in den Daten gefunden: %s",
                    key,
                    list(data.keys())
                )
                self._attr_available = False
        except Exception as err:
            self._logger.error(
                "Fehler beim Aktualisieren von %s mit Schlüssel %s: %s",
                self.entity_id,
                key,
                err
            )
            self._attr_available = False

    def _get_composite_keys(self, key: str) -> List[str]:
        """Erstellt eine Liste alternativer Schlüsselnamen für einen Schlüssel.
        
        Manche Werte können unter verschiedenen Namen in der API vorkommen.
        Diese Methode gibt alternative Schlüssel zurück, nach denen gesucht werden kann.
        
        Args:
            key: Der Primärschlüssel
            
        Returns:
            List[str]: Liste alternativer Schlüsselnamen
        """
        # Mapping von primären zu alternativen Schlüsseln
        key_mappings = {
            "ph_value": ["ph_current", "ph", "ph_level"],
            "orp_value": ["orp_current", "orp", "redox"],
            "temp_value": ["temp_current", "temperature", "water_temp"],
            "water_temp": ["onewire1_value", "temp_value", "temperature"],
            "air_temp": ["onewire2_value", "ambient_temp", "ambient_temperature"],
            "filter_state": ["FILTER_STATE", "FILTER", "filter"],
            "heater_state": ["HEATER_STATE", "HEATER", "heater"],
            "solar_state": ["SOLAR_STATE", "SOLAR", "solar"],
            "cover_state": ["COVER_STATE", "COVER", "cover"],
        }
        
        return key_mappings.get(key, [])
        
    def get_float_value(self, key: str, default: float = 0.0) -> float:
        """Gibt einen Wert als Float zurück.
        
        Args:
            key: Der Schlüssel in den Daten
            default: Der Standardwert, falls der Schlüssel nicht existiert
            
        Returns:
            float: Der Wert als Float oder der Standardwert
        """
        if not self.coordinator.data:
            return default
            
        try:
            value = self.coordinator.data.get(key)
            if value is None:
                # Versuche es mit alternativen Schlüsseln
                for alt_key in self._get_composite_keys(key):
                    alt_value = self.coordinator.data.get(alt_key)
                    if alt_value is not None:
                        value = alt_value
                        break
                        
            if value is None:
                return default
                
            return float(value)
        except (ValueError, TypeError):
            self._logger.warning(
                "Konnte Wert %s nicht in Float umwandeln", 
                value
            )
            return default

    def get_bool_value(self, key: str, default: bool = False) -> bool:
        """Gibt einen Wert als Boolean zurück.
        
        Args:
            key: Der Schlüssel in den Daten
            default: Der Standardwert, falls der Schlüssel nicht existiert
            
        Returns:
            bool: Der Wert als Boolean oder der Standardwert
        """
        if not self.coordinator.data:
            return default
            
        value = self.coordinator.data.get(key)
        if value is None:
            # Versuche es mit alternativen Schlüsseln
            for alt_key in self._get_composite_keys(key):
                alt_value = self.coordinator.data.get(alt_key)
                if alt_value is not None:
                    value = alt_value
                    break
                    
        if value is None:
            return default
            
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ["true", "1", "on", "yes", "active", "an", "ein"]
            
        return default

    def get_int_value(self, key: str, default: int = 0) -> int:
        """Gibt einen Wert als Integer zurück.
        
        Args:
            key: Der Schlüssel in den Daten
            default: Der Standardwert, falls der Schlüssel nicht existiert
            
        Returns:
            int: Der Wert als Integer oder der Standardwert
        """
        if not self.coordinator.data:
            return default
            
        try:
            value = self.coordinator.data.get(key)
            if value is None:
                # Versuche es mit alternativen Schlüsseln
                for alt_key in self._get_composite_keys(key):
                    alt_value = self.coordinator.data.get(alt_key)
                    if alt_value is not None:
                        value = alt_value
                        break
                        
            if value is None:
                return default
                
            return int(float(value))
        except (ValueError, TypeError):
            self._logger.warning(
                "Konnte Wert %s nicht in Integer umwandeln", 
                value
            )
            return default

    def get_str_value(self, key: str, default: str = "") -> str:
        """Gibt einen Wert als String zurück.
        
        Args:
            key: Der Schlüssel in den Daten
            default: Der Standardwert, falls der Schlüssel nicht existiert
            
        Returns:
            str: Der Wert als String oder der Standardwert
        """
        if not self.coordinator.data:
            return default
            
        value = self.coordinator.data.get(key)
        if value is None:
            # Versuche es mit alternativen Schlüsseln
            for alt_key in self._get_composite_keys(key):
                alt_value = self.coordinator.data.get(alt_key)
                if alt_value is not None:
                    value = alt_value
                    break
                    
        if value is None:
            return default
            
        return str(value)