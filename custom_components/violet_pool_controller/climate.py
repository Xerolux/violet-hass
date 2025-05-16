"""Climate Integration für den Violet Pool Controller."""
import logging
from typing import Any, Dict, List, Optional, Final, ClassVar
from dataclasses import dataclass

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    HVACAction,
    ClimateEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_ACTIVE_FEATURES
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

HEATER_HVAC_MODES: Final[Dict[int, str]] = {
    0: HVACMode.AUTO,
    1: HVACMode.AUTO,
    2: HVACMode.AUTO,
    3: HVACMode.AUTO,
    4: HVACMode.HEAT,
    5: HVACMode.AUTO,
    6: HVACMode.OFF,
}

HEATER_HVAC_ACTIONS: Final[Dict[int, str]] = {
    0: HVACAction.IDLE,
    1: HVACAction.HEATING,
    2: HVACAction.IDLE,
    3: HVACAction.HEATING,
    4: HVACAction.HEATING,
    5: HVACAction.IDLE,
    6: HVACAction.OFF,
}

CLIMATE_FEATURE_MAP: Final[Dict[str, str]] = {
    "HEATER": "heating",
    "SOLAR": "solar",
}

WATER_TEMP_SENSORS: Final[List[str]] = [
    "onewire1_value",
    "water_temp",
    "WATER_TEMPERATURE",
    "temp_value",
]

@dataclass
class VioletClimateEntityDescription(ClimateEntityDescription):
    """Beschreibung der Violet Pool Climate-Entities."""
    feature_id: Optional[str] = None

class VioletClimateEntity(VioletPoolControllerEntity, ClimateEntity):
    """Repräsentiert die Heizungs- oder Absorbersteuerung des Violet Pool Controllers."""
    _attr_temperature_unit: ClassVar[str] = UnitOfTemperature.CELSIUS
    _attr_supported_features: ClassVar[int] = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_hvac_modes: ClassVar[List[str]] = [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]
    _attr_min_temp: ClassVar[float] = 20.0
    _attr_max_temp: ClassVar[float] = 35.0
    _attr_target_temperature_step: ClassVar[float] = 0.5

    entity_description: VioletClimateEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        climate_type: str,
    ) -> None:
        """Initialisiere die Climate-Entity.

        Args:
            coordinator: Daten-Koordinator.
            config_entry: Config Entry.
            climate_type: "HEATER" oder "SOLAR".
        """
        self.climate_type = climate_type
        name = "Heizung" if climate_type == "HEATER" else "Solarabsorber"
        icon = "mdi:radiator" if climate_type == "HEATER" else "mdi:solar-power"
        feature_id = CLIMATE_FEATURE_MAP.get(climate_type)

        self.entity_description = VioletClimateEntityDescription(
            key=climate_type,
            name=name,
            icon=icon,
            feature_id=feature_id,
        )
        super().__init__(coordinator=coordinator, config_entry=config_entry, entity_description=self.entity_description)
        self._attr_target_temperature = self._get_target_temperature()
        self._attr_hvac_mode = self._get_hvac_mode()
        _LOGGER.debug(
            "Climate-Entität für %s initialisiert mit Target: %.1f°C, Modus: %s",
            self.climate_type,
            self._attr_target_temperature,
            self._attr_hvac_mode
        )

    def _get_target_temperature(self) -> float:
        """Hole die Zieltemperatur aus den Coordinator-Daten."""
        key = "HEATER_TARGET_TEMP" if self.climate_type == "HEATER" else "SOLAR_TARGET_TEMP"
        return self.get_float_value(key, 28.0)

    def _get_hvac_mode(self) -> str:
        """Ermittle den aktuellen HVAC-Modus."""
        state = self.get_int_value(self.climate_type, 0)
        return HEATER_HVAC_MODES.get(state, HVACMode.OFF)

    def _update_from_coordinator(self) -> None:
        """Aktualisiere den Zustand der Climate-Entity."""
        self._attr_target_temperature = self._get_target_temperature()
        self._attr_hvac_mode = self._get_hvac_mode()

    @property
    def hvac_action(self) -> Optional[str]:
        """Gib die aktuelle HVAC-Aktion zurück."""
        state = self.get_int_value(self.climate_type, 0)
        return HEATER_HVAC_ACTIONS.get(state, HVACAction.IDLE)

    @property
    def current_temperature(self) -> Optional[float]:
        """Gib die aktuelle Wassertemperatur zurück."""
        for sensor_key in WATER_TEMP_SENSORS:
            value = self.get_float_value(sensor_key, None)
            if value is not None:
                return value
        _LOGGER.debug("Keine Wassertemperatur gefunden in %s", WATER_TEMP_SENSORS)
        return None

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Setze die Zieltemperatur.

        Args:
            **kwargs: Enthält ATTR_TEMPERATURE.
        """
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        if not (self.min_temp <= temperature <= self.max_temp):
            _LOGGER.warning(
                "Angeforderte Temperatur %.1f außerhalb des Bereichs (%.1f-%.1f)",
                temperature, self.min_temp, self.max_temp
            )
            return

        try:
            # Kein Runden, um genaue Werte zu übernehmen
            _LOGGER.info(
                "Setze %s Zieltemperatur auf %.1f°C",
                "Heizung" if self.climate_type == "HEATER" else "Solar",
                temperature
            )
            command = {"type": self.climate_type, "temperature": temperature}
            result = await self.device.async_send_command("/set_temperature", command)
            if isinstance(result, dict) and result.get("success", False):
                self._attr_target_temperature = temperature
                self.async_write_ha_state()
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("Fehler beim Setzen der Temperatur: %s", result)
        except Exception as err:
            _LOGGER.error("Fehler beim Setzen der Temperatur: %s", err)

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Setze den HVAC-Modus.

        Args:
            hvac_mode: "OFF", "HEAT" oder "AUTO".
        """
        try:
            action = {
                HVACMode.HEAT: "ON",
                HVACMode.OFF: "OFF",
                HVACMode.AUTO: "AUTO"
            }.get(hvac_mode)

            if action is None:
                _LOGGER.warning("Nicht unterstützter HVAC-Modus: %s", hvac_mode)
                return

            _LOGGER.info(
                "Setze %s-Modus auf %s",
                "Heizung" if self.climate_type == "HEATER" else "Solar",
                action
            )
            command = {"id": self.climate_type, "action": action, "duration": 0}
            result = await self.device.async_send_command("/set_switch", command)
            if isinstance(result, dict) and result.get("success", False):
                self._attr_hvac_mode = hvac_mode
                self.async_write_ha_state()
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("Fehler beim Setzen des HVAC-Modus: %s", result)
        except Exception as err:
            _LOGGER.error("Fehler beim Setzen des HVAC-Modus: %s", err)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Richte Climate-Entities ein.

    Args:
        hass: Home Assistant Instanz.
        config_entry: Config Entry.
        async_add_entities: Callback zum Hinzufügen von Entities.
    """
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []

    if "HEATER" in coordinator.data:
        entities.append(VioletClimateEntity(coordinator, config_entry, "HEATER"))
    if "SOLAR" in coordinator.data:
        entities.append(VioletClimateEntity(coordinator, config_entry, "SOLAR"))

    if entities:
        async_add_entities(entities)
        _LOGGER.info("%d Climate-Entities hinzugefügt", len(entities))
    else:
        _LOGGER.info("Keine Heizungs- oder Solarabsorber-Daten gefunden")