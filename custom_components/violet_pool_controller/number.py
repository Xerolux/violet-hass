"""Number Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, Optional, Final, List
from dataclasses import dataclass

from homeassistant.components.number import (
    NumberEntity,
    NumberMode,
    NumberDeviceClass,
    NumberEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, CONF_ACTIVE_FEATURES
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Konsolidierte Sollwert-Definitionen mit setpoint_fields, indicator_fields und default_value
SETPOINT_DEFINITIONS: Final = [
    {
        "key": "ph_setpoint",
        "name": "pH Sollwert",
        "min_value": 6.8,
        "max_value": 7.8,
        "step": 0.1,
        "icon": "mdi:flask",
        "api_key": "pH",
        "feature_id": "ph_control",
        "parameter": "pH Sollwert",
        "unit_of_measurement": "pH",
        "api_endpoint": "/set_target_value",
        "device_class": NumberDeviceClass.PH,
        "entity_category": EntityCategory.CONFIG,
        "setpoint_fields": ["pH_SETPOINT", "pH_TARGET", "TARGET_PH"],
        "indicator_fields": ["pH_value", "DOS_4_PHM", "DOS_5_PHP"],
        "default_value": 7.2,
    },
    {
        "key": "chlorine_setpoint",
        "name": "Redox Sollwert",
        "min_value": 600,
        "max_value": 850,
        "step": 10,
        "icon": "mdi:flash",
        "api_key": "ORP",
        "feature_id": "chlorine_control",
        "parameter": "Redox Sollwert",
        "unit_of_measurement": "mV",
        "api_endpoint": "/set_target_value",
        "setpoint_fields": ["REDOX_SETPOINT", "ORP_TARGET", "TARGET_ORP", "REDOX_TARGET"],
        "indicator_fields": ["orp_value", "DOS_1_CL", "pot_value"],
        "default_value": 750.0,
    },
    {
        "key": "min_chlorine_level",
        "name": "Min. Chlorgehalt",
        "min_value": 0.1,
        "max_value": 0.5,
        "step": 0.05,
        "icon": "mdi:test-tube",
        "api_key": "MinChlorine",
        "feature_id": "chlorine_control",
        "parameter": "Min. Chlorgehalt",
        "unit_of_measurement": "mg/l",
        "api_endpoint": "/set_target_value",
        "setpoint_fields": ["MIN_CHLORINE_LEVEL"],
        "indicator_fields": ["CHLORINE_LEVEL", "pot_value", "DOS_1_CL"],
        "default_value": 0.2,
    },
    {
        "key": "max_chlorine_level_day",
        "name": "Max. Chlorgehalt Tag",
        "min_value": 0.3,
        "max_value": 0.8,
        "step": 0.05,
        "icon": "mdi:test-tube",
        "api_key": "MaxChlorineDay",
        "feature_id": "chlorine_control",
        "parameter": "Max. Chlorgehalt Tag",
        "unit_of_measurement": "mg/l",
        "api_endpoint": "/set_target_value",
        "setpoint_fields": ["MAX_CHLORINE_LEVEL_DAY"],
        "indicator_fields": ["CHLORINE_LEVEL", "pot_value", "DOS_1_CL"],
        "default_value": 0.5,
    },
    {
        "key": "max_chlorine_level_night",
        "name": "Max. Chlorgehalt Nacht",
        "min_value": 0.5,
        "max_value": 1.2,
        "step": 0.05,
        "icon": "mdi:test-tube",
        "api_key": "MaxChlorineNight",
        "feature_id": "chlorine_control",
        "parameter": "Max. Chlorgehalt Nacht",
        "unit_of_measurement": "mg/l",
        "api_endpoint": "/set_target_value",
        "setpoint_fields": ["MAX_CHLORINE_LEVEL_NIGHT"],
        "indicator_fields": ["CHLORINE_LEVEL", "pot_value", "DOS_1_CL"],
        "default_value": 0.8,
    },
]

@dataclass
class VioletNumberEntityDescription(NumberEntityDescription):
    """Beschreibung der Violet Pool Number-Entities."""
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    parameter: Optional[str] = None
    feature_id: Optional[str] = None

class VioletNumberEntity(VioletPoolControllerEntity, NumberEntity):
    """Repräsentiert einen Sollwert im Violet Pool Controller."""
    entity_description: VioletNumberEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        definition: Dict[str, Any],
    ):
        """Initialisiere die Number-Entity."""
        self._definition = definition
        description = VioletNumberEntityDescription(
            key=definition["key"],
            name=definition["name"],
            icon=definition.get("icon"),
            device_class=definition.get("device_class"),
            native_unit_of_measurement=definition.get("unit_of_measurement"),
            entity_category=definition.get("entity_category"),
            api_key=definition.get("api_key"),
            api_endpoint=definition.get("api_endpoint"),
            parameter=definition.get("parameter"),
            feature_id=definition.get("feature_id"),
        )
        super().__init__(coordinator, config_entry, description)
        self._attr_native_min_value = definition["min_value"]
        self._attr_native_max_value = definition["max_value"]
        self._attr_native_step = definition["step"]
        self._attr_mode = NumberMode.AUTO
        self._attr_native_value = self._get_current_value()
        unit = self.entity_description.native_unit_of_measurement or ""
        _LOGGER.debug(
            "Number-Entity für %s initialisiert mit Wert: %s %s",
            definition["name"],
            self._attr_native_value,
            unit
        )

    def _update_from_coordinator(self) -> None:
        """Aktualisiert den Zustand basierend auf Coordinator-Daten."""
        old_value = self._attr_native_value
        self._attr_native_value = self._get_current_value()
        if old_value != self._attr_native_value:
            _LOGGER.debug(
                "Wert für %s aktualisiert: %s -> %s",
                self.name,
                old_value,
                self._attr_native_value
            )

    def _get_current_value(self) -> Optional[float]:
        """Ermittle den aktuellen Wert aus den Coordinator-Daten.

        Returns:
            Optional[float]: Der aktuelle Wert oder Fallback zum Standardwert.
        """
        setpoint_fields = self._definition.get("setpoint_fields", [])
        for field in setpoint_fields:
            value = self.get_float_value(field, None)
            if value is not None:
                return value
        default = self._definition.get("default_value", self._attr_native_min_value)
        _LOGGER.debug("Verwende Standardwert für %s: %s", self.name, default)
        return default

    async def async_set_native_value(self, value: float) -> None:
        """Setze den neuen Wert im Gerät."""
        try:
            api_key = self.entity_description.api_key
            api_endpoint = self.entity_description.api_endpoint
            if not api_key or not api_endpoint:
                _LOGGER.error(
                    "API-Key oder Endpunkt fehlt für %s",
                    self.entity_id
                )
                return
            if self._attr_native_step:
                value = round(value / self._attr_native_step) * self._attr_native_step
                if self._attr_native_step < 1:
                    value = round(value, 2)
            unit = self.entity_description.native_unit_of_measurement or ""
            _LOGGER.info(
                "Setze Sollwert für %s: %s = %s %s",
                self.name,
                api_key,
                value,
                unit
            )
            command = {"target_type": api_key, "value": value}
            result = await self.device.async_send_command(api_endpoint, command)
            if isinstance(result, dict) and result.get("success", False):
                _LOGGER.debug("Sollwert erfolgreich gesetzt: %s = %s", api_key, value)
            else:
                _LOGGER.warning("Sollwert setzen möglicherweise fehlgeschlagen: %s", result)
            self._attr_native_value = value
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Fehler beim Setzen des Sollwerts: %s", err)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Richte Number-Entities basierend auf dem Config-Entry ein."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    entities: List[VioletNumberEntity] = []
    for definition in SETPOINT_DEFINITIONS:
        feature_id = definition.get("feature_id")
        # Feature-Check ist für Debugging deaktiviert; entferne 'False' zum Aktivieren
        if False and feature_id and feature_id not in active_features:
            _LOGGER.debug(
                "Überspringe %s: Feature %s nicht aktiv",
                definition["name"],
                feature_id
            )
            continue
        setpoint_fields = definition.get("setpoint_fields", [])
        indicator_fields = definition.get("indicator_fields", [])
        if any(field in coordinator.data for field in setpoint_fields + indicator_fields):
            entities.append(VioletNumberEntity(coordinator, config_entry, definition))
            _LOGGER.debug("Number-Entity für %s hinzugefügt", definition["name"])
        else:
            _LOGGER.debug(
                "Überspringe %s: Keine relevanten Daten",
                definition["name"]
            )
    if entities:
        _LOGGER.info("%d Number-Entities hinzugefügt", len(entities))
        async_add_entities(entities)
    else:
        _LOGGER.info("Keine passenden Entities gefunden")
