"""Number Integration für den Violet Pool Controller."""
import logging

from homeassistant.components.number import (
    NumberEntity, 
    NumberDeviceClass, 
    NumberEntityDescription
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, SETPOINT_DEFINITIONS, CONF_ACTIVE_FEATURES
from .api import VioletPoolAPIError
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class VioletNumber(VioletPoolControllerEntity, NumberEntity):
    """Repräsentation einer Violet Pool Number-Entity (Sollwert)."""

    entity_description: NumberEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: NumberEntityDescription,
        setpoint_config: dict
    ) -> None:
        """
        Initialisiere die Number-Entity.

        Args:
            coordinator: Update Coordinator
            config_entry: Config Entry
            description: Entity Description
            setpoint_config: Sollwert-Konfiguration
        """
        super().__init__(coordinator, config_entry, description)

        # Min/Max/Step Werte setzen
        self._attr_native_min_value = setpoint_config["min_value"]
        self._attr_native_max_value = setpoint_config["max_value"]
        self._attr_native_step = setpoint_config["step"]

        # Zusätzliche Attribute speichern
        self._setpoint_fields = setpoint_config["setpoint_fields"]
        self._indicator_fields = setpoint_config["indicator_fields"]
        self._default_value = setpoint_config["default_value"]
        self._api_key = setpoint_config["api_key"]

        # ✅ FIXED: Lokale Cache-Variable für thread-sichere optimistische Updates
        self._optimistic_value: float | None = None

        _LOGGER.info(
            "Number-Entity initialisiert: %s (Range: %.1f-%.1f, Step: %.1f, API-Key: %s)",
            description.name,
            self._attr_native_min_value,
            self._attr_native_max_value,
            self._attr_native_step,
            self._api_key
        )

    @property
    def native_value(self) -> float | None:
        """
        Gibt den aktuellen Sollwert zurück.

        Versucht den Wert aus verschiedenen möglichen Feldern zu lesen.
        Falls kein Wert gefunden wird, wird der Standardwert zurückgegeben.

        Returns:
            Aktueller Sollwert oder default_value
        """
        # ✅ FIXED: Prüfe zuerst optimistischen Cache
        if self._optimistic_value is not None:
            return self._optimistic_value

        # Versuche Sollwert aus den konfigurierten Feldern zu lesen
        if self._setpoint_fields:
            for field in self._setpoint_fields:
                value = self.get_float_value(field)
                if value is not None:
                    _LOGGER.debug(
                        "Sollwert für %s aus Feld '%s': %.2f",
                        self.entity_description.name,
                        field,
                        value
                    )
                    return value

        # Fallback auf Standardwert
        _LOGGER.debug(
            "Kein Sollwert gefunden für %s, verwende default: %.2f",
            self.entity_description.name,
            self._default_value
        )
        return self._default_value

    @property
    def available(self) -> bool:
        """
        Prüft ob die Entity verfügbar ist.
        
        Entity ist verfügbar wenn mindestens ein Indikator-Feld
        in den Coordinator-Daten vorhanden ist.
        
        Returns:
            True wenn verfügbar
        """
        # Prüfe ob Indikator-Felder verfügbar sind
        if self._indicator_fields:
            for field in self._indicator_fields:
                if field in self.coordinator.data:
                    _LOGGER.debug(
                        "Entity %s verfügbar (Indikator '%s' gefunden)",
                        self.entity_description.name,
                        field
                    )
                    return super().available
            
            _LOGGER.debug(
                "Entity %s nicht verfügbar (keine Indikator-Felder gefunden)",
                self.entity_description.name
            )
        
        return super().available

    async def async_set_native_value(self, value: float) -> None:
        """
        Setzt einen neuen Sollwert.
        
        Verwendet die entsprechende API-Methode basierend auf dem Sollwert-Typ.
        
        Args:
            value: Neuer Sollwert
            
        Raises:
            HomeAssistantError: Bei API-Fehlern
        """
        if not self._api_key:
            _LOGGER.error(
                "Kein API-Key für %s definiert - kann Sollwert nicht setzen",
                self.entity_description.name
            )
            raise HomeAssistantError(
                f"Kein API-Key für {self.entity_description.name} definiert"
            )

        # Validiere Wertebereich
        if value < self._attr_native_min_value or value > self._attr_native_max_value:
            _LOGGER.error(
                "Wert %.2f außerhalb des gültigen Bereichs (%.1f-%.1f) für %s",
                value,
                self._attr_native_min_value,
                self._attr_native_max_value,
                self.entity_description.name
            )
            raise HomeAssistantError(
                f"Wert {value} außerhalb des gültigen Bereichs "
                f"({self._attr_native_min_value}-{self._attr_native_max_value})"
            )

        try:
            unit = self.entity_description.native_unit_of_measurement or ""
            _LOGGER.info(
                "Setze %s auf %.2f%s (vorher: %.2f%s)",
                self.entity_description.name,
                value,
                unit,
                self.native_value or 0,
                unit
            )
            
            # Wähle die passende API-Methode basierend auf dem API-Key
            api_key = self._api_key
            
            if api_key == "pH":
                _LOGGER.debug("Verwende set_ph_target für pH-Wert")
                result = await self.device.api.set_ph_target(value)
            elif api_key == "ORP":
                _LOGGER.debug("Verwende set_orp_target für ORP-Wert")
                result = await self.device.api.set_orp_target(int(value))
            elif api_key == "MinChlorine":
                _LOGGER.debug("Verwende set_min_chlorine_level für Chlor-Wert")
                result = await self.device.api.set_min_chlorine_level(value)
            else:
                _LOGGER.debug("Verwende set_target_value für %s", api_key)
                result = await self.device.api.set_target_value(api_key, value)
            
            # Prüfe Ergebnis
            if result.get("success", True):
                _LOGGER.info(
                    "%s erfolgreich auf %.2f%s gesetzt",
                    self.entity_description.name,
                    value,
                    unit
                )

                # ✅ FIXED: Optimistisches Update mit lokalem Cache (thread-safe)
                self._optimistic_value = value
                _LOGGER.debug("Optimistischer Cache für '%s' auf %.2f gesetzt", self.entity_description.name, value)

                # State sofort aktualisieren
                self.async_write_ha_state()

                # Daten vom Controller neu abrufen und dann Cache zurücksetzen
                await self.coordinator.async_request_refresh()

                # ✅ FIXED: Cache nach erfolgreichem Refresh zurücksetzen
                self._optimistic_value = None
                _LOGGER.debug("Optimistischer Cache für '%s' zurückgesetzt", self.entity_description.name)
            else:
                error_msg = result.get("response", result)
                _LOGGER.warning(
                    "%s setzen möglicherweise fehlgeschlagen: %s",
                    self.entity_description.name,
                    error_msg
                )
                raise HomeAssistantError(
                    f"Sollwert setzen fehlgeschlagen: {error_msg}"
                )
                
        except VioletPoolAPIError as err:
            _LOGGER.error(
                "API-Fehler beim Setzen von %s auf %.2f: %s",
                self.entity_description.name,
                value,
                err
            )
            raise HomeAssistantError(
                f"Sollwert setzen fehlgeschlagen: {err}"
            ) from err
        
        except Exception as err:
            _LOGGER.exception(
                "Unerwarteter Fehler beim Setzen von %s auf %.2f: %s",
                self.entity_description.name,
                value,
                err
            )
            raise HomeAssistantError(
                f"Unerwarteter Fehler: {err}"
            ) from err


async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """
    Richtet Number-Entities für die Config Entry ein.
    
    Erstellt Number-Entities für alle konfigurierten Sollwerte,
    die in den aktiven Features enthalten sind und deren
    Indikator-Felder verfügbar sind.
    
    Args:
        hass: Home Assistant Instanz
        config_entry: Config Entry
        async_add_entities: Callback zum Hinzufügen von Entities
    """
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Aktive Features aus Options oder Data holen
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, 
        config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    
    _LOGGER.debug(
        "Setup Number-Entities für '%s' mit aktiven Features: %s",
        config_entry.title,
        ", ".join(active_features)
    )
    
    entities: list[NumberEntity] = []

    for setpoint_config in SETPOINT_DEFINITIONS:
        setpoint_name = setpoint_config["name"]
        setpoint_key = setpoint_config["key"]
        feature_id = setpoint_config["feature_id"]
        
        # Prüfe ob Feature aktiviert ist
        if feature_id and feature_id not in active_features:
            _LOGGER.debug(
                "Überspringe Number '%s': Feature '%s' nicht aktiv",
                setpoint_name,
                feature_id
            )
            continue
        
        # Prüfe ob Indikator-Felder verfügbar sind
        # (zeigt an, dass dieser Sollwert relevant ist)
        if setpoint_config["indicator_fields"]:
            has_indicators = any(
                field in coordinator.data 
                for field in setpoint_config["indicator_fields"]
            )
            
            if not has_indicators:
                _LOGGER.debug(
                    "Überspringe Number '%s': Keine Indikator-Felder verfügbar (%s)",
                    setpoint_name,
                    ", ".join(setpoint_config["indicator_fields"])
                )
                continue
        
        # Erstelle NumberEntityDescription
        description = NumberEntityDescription(
            key=setpoint_key,
            name=setpoint_name,
            icon=setpoint_config["icon"],
            native_unit_of_measurement=setpoint_config["unit_of_measurement"],
            device_class=setpoint_config["device_class"],
            entity_category=setpoint_config["entity_category"],
        )
        
        _LOGGER.debug(
            "Erstelle Number-Entity für '%s' (Key: %s)",
            setpoint_name,
            setpoint_key
        )
        
        entities.append(
            VioletNumber(coordinator, config_entry, description, setpoint_config)
        )

    # Entities hinzufügen
    if entities:
        async_add_entities(entities)
        entity_names = [e.entity_description.name for e in entities]
        _LOGGER.info(
            "%d Number-Entities für '%s' eingerichtet: %s",
            len(entities),
            config_entry.title,
            ", ".join(entity_names)
        )
    else:
        _LOGGER.info(
            "Keine Number-Entities für '%s' eingerichtet",
            config_entry.title
        )