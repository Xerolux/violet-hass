"""Climate Integration für den Violet Pool Controller."""
import logging
from dataclasses import dataclass

from homeassistant.components.climate import (
    ClimateEntity, ClimateEntityFeature, HVACMode, HVACAction
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_ACTIVE_FEATURES
from .api import ACTION_ON, ACTION_OFF, ACTION_AUTO, VioletPoolAPIError
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

HEATER_HVAC_MODES = {
    0: HVACMode.AUTO, 1: HVACMode.AUTO, 2: HVACMode.AUTO, 3: HVACMode.AUTO,
    4: HVACMode.HEAT, 5: HVACMode.AUTO, 6: HVACMode.OFF
}

HEATER_HVAC_ACTIONS = {
    0: HVACAction.IDLE, 1: HVACAction.HEATING, 2: HVACAction.IDLE, 3: HVACAction.HEATING,
    4: HVACAction.HEATING, 5: HVACAction.IDLE, 6: HVACAction.OFF
}

CLIMATE_FEATURE_MAP = {"HEATER": "heating", "SOLAR": "solar"}

WATER_TEMP_SENSORS = ["onewire1_value", "water_temp", "WATER_TEMPERATURE", "temp_value"]

@dataclass
class VioletClimateEntityDescription:
    """Beschreibung der Violet Pool Climate-Entities."""
    key: str
    name: str
    icon: str
    feature_id: str | None = None

class VioletClimateEntity(VioletPoolControllerEntity, ClimateEntity):
    """Repräsentiert Heizungs- oder Solarsteuerung."""
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]
    _attr_min_temp = 20.0
    _attr_max_temp = 35.0
    _attr_target_temperature_step = 0.5

    def __init__(self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry, climate_type: str) -> None:
        """Initialisiere Climate-Entity."""
        name = "Heizung" if climate_type == "HEATER" else "Solarabsorber"
        icon = "mdi:radiator" if climate_type == "HEATER" else "mdi:solar-power"
        self.entity_description = VioletClimateEntityDescription(
            key=climate_type, name=name, icon=icon, feature_id=CLIMATE_FEATURE_MAP.get(climate_type)
        )
        super().__init__(coordinator, config_entry, self.entity_description)
        self.climate_type = climate_type
        self._attr_target_temperature = self._get_target_temperature()
        self._attr_hvac_mode = self._get_hvac_mode()
        _LOGGER.debug("%s initialisiert: Ziel=%.1f°C, Modus=%s", name, self._attr_target_temperature, self._attr_hvac_mode)

    def _get_target_temperature(self) -> float:
        """Hole Zieltemperatur."""
        key = f"{self.climate_type}_TARGET_TEMP"
        return self.get_float_value(key, 28.0)

    def _get_hvac_mode(self) -> str:
        """Ermittle HVAC-Modus."""
        return HEATER_HVAC_MODES.get(self.get_int_value(self.climate_type, 0), HVACMode.OFF)

    @property
    def hvac_action(self) -> str | None:
        """Gib HVAC-Aktion zurück."""
        return HEATER_HVAC_ACTIONS.get(self.get_int_value(self.climate_type, 0), HVACAction.IDLE)

    @property
    def current_temperature(self) -> float | None:
        """Gib Wassertemperatur zurück."""
        for sensor_key in WATER_TEMP_SENSORS:
            if value := self.get_float_value(sensor_key, None):
                return value
        _LOGGER.debug("Keine Wassertemperatur in %s", WATER_TEMP_SENSORS)
        return None

    async def async_set_temperature(self, **kwargs) -> None:
        """Setze Zieltemperatur."""
        if (temperature := kwargs.get("temperature")) is None:
            return

        if not self.min_temp <= temperature <= self.max_temp:
            _LOGGER.warning("Temperatur %.1f außerhalb Bereich (%.1f-%.1f)", temperature, self.min_temp, self.max_temp)
            return

        try:
            _LOGGER.info("Setze %s-Temperatur auf %.1f°C", self.climate_type, temperature)
            result = await self.device.api.set_device_temperature(self.climate_type, temperature)
            if result.get("success", True):
                self._attr_target_temperature = temperature
                self.async_write_ha_state()
                await self.coordinator.async_request_refresh()
            else:
                raise HomeAssistantError(f"Temperatur setzen fehlgeschlagen: {result.get('response', result)}")
        except VioletPoolAPIError as err:
            _LOGGER.error("API-Fehler beim Setzen der Temperatur: %s", err)
            raise HomeAssistantError(f"Temperatur setzen fehlgeschlagen: {err}") from err

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Setze HVAC-Modus."""
        api_action = {HVACMode.HEAT: ACTION_ON, HVACMode.OFF: ACTION_OFF, HVACMode.AUTO: ACTION_AUTO}.get(hvac_mode)
        if not api_action:
            _LOGGER.warning("Nicht unterstützter HVAC-Modus: %s", hvac_mode)
            return

        try:
            _LOGGER.info("Setze %s-Modus auf %s", self.climate_type, hvac_mode)
            result = await self.device.api.set_switch_state(self.climate_type, api_action)
            if result.get("success", True):
                self._attr_hvac_mode = hvac_mode
                self.async_write_ha_state()
                await self.coordinator.async_request_refresh()
            else:
                raise HomeAssistantError(f"HVAC-Modus setzen fehlgeschlagen: {result.get('response', result)}")
        except VioletPoolAPIError as err:
            _LOGGER.error("API-Fehler beim Setzen des HVAC-Modus: %s", err)
            raise HomeAssistantError(f"HVAC-Modus setzen fehlgeschlagen: {err}") from err

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Richte Climate-Entities ein."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, [])
    entities = []

    for climate_type, feature in CLIMATE_FEATURE_MAP.items():
        if feature in active_features and climate_type in coordinator.data:
            _LOGGER.debug("%s-Entity erstellt: Feature '%s' aktiv", climate_type, feature)
            entities.append(VioletClimateEntity(coordinator, config_entry, climate_type))
        else:
            _LOGGER.debug("%s-Entity nicht erstellt: Feature '%s' inaktiv oder Daten fehlen", climate_type, feature)

    if entities:
        async_add_entities(entities)
        _LOGGER.info("%d Climate-Entities hinzugefügt", len(entities))
    else:
        _LOGGER.info("Keine Climate-Entities hinzugefügt")
