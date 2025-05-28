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
from homeassistant.exceptions import HomeAssistantError # Import HomeAssistantError

from .const import DOMAIN, CONF_ACTIVE_FEATURES 
from .api import (
    ACTION_ON, ACTION_OFF, ACTION_AUTO,
    VioletPoolAPIError, VioletPoolConnectionError, VioletPoolCommandError # Import API errors
)
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Comments explaining device states for HEATER_HVAC_MODES and HEATER_HVAC_ACTIONS
# Based on typical behavior, actual values may vary based on device manual:
# State 0: Usually AUTO mode, device is IDLE or decided not to heat/cool based on target.
# State 1: Usually AUTO mode, device is actively HEATING/COOLING to reach target.
# State 2: Often an AUTO mode variant, possibly IDLE due to external control (e.g., control rule).
# State 3: Often an AUTO mode variant, possibly HEATING/COOLING due to an overriding rule.
# State 4: Manual ON/HEAT mode, device is actively HEATING.
# State 5: Often an AUTO mode variant, possibly IDLE due to an overriding rule (e.g., emergency off).
# State 6: Manual OFF mode.

HEATER_HVAC_MODES: Final[Dict[int, str]] = {
    0: HVACMode.AUTO,  # e.g., Auto Idle
    1: HVACMode.AUTO,  # e.g., Auto Heating
    2: HVACMode.AUTO,  # e.g., Auto Idle (by rule)
    3: HVACMode.AUTO,  # e.g., Auto Heating (by rule)
    4: HVACMode.HEAT,  # e.g., Manual Heat
    5: HVACMode.AUTO,  # e.g., Auto Idle (by rule)
    6: HVACMode.OFF,   # e.g., Manual Off
}

HEATER_HVAC_ACTIONS: Final[Dict[int, str]] = {
    0: HVACAction.IDLE,    # Auto mode, not actively heating
    1: HVACAction.HEATING, # Auto mode, actively heating
    2: HVACAction.IDLE,    # Auto mode, idle due to rule
    3: HVACAction.HEATING, # Auto mode, heating due to rule
    4: HVACAction.HEATING, # Manual Heat mode, actively heating
    5: HVACAction.IDLE,    # Auto mode, idle due to rule
    6: HVACAction.OFF,     # Manual Off mode
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

    # Removed _update_from_coordinator method as Home Assistant handles updates via coordinator now.
    # State properties will re-calculate on access based on coordinator data.

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
            # Use the new API method
            result = await self.device.api.set_device_temperature(
                device_type=self.climate_type, temperature=temperature
            )
            # Assuming VioletPoolAPI methods raise exceptions on failure or return dict with "success"
            if result.get("success", True): # Assume success if not explicitly false
                self._attr_target_temperature = temperature # Optimistic update
                self.async_write_ha_state()
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("Fehler beim Setzen der Temperatur via API: %s", result.get("response", result))
                raise HomeAssistantError(f"Fehler beim Setzen der Temperatur für {self.name} via API: {result.get('response', result)}")
        except (VioletPoolConnectionError, VioletPoolCommandError) as err:
            _LOGGER.error(f"API-Fehler beim Setzen der Temperatur für {self.name}: {err}")
            raise HomeAssistantError(f"Zieltemperatur für {self.name} setzen fehlgeschlagen: {err}") from err
        except Exception as err:
            _LOGGER.exception(f"Unerwarteter Fehler beim Setzen der Temperatur für {self.name}: {err}")
            raise HomeAssistantError(f"Unerwarteter Fehler beim Setzen der Zieltemperatur für {self.name}: {err}") from err

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Setze den HVAC-Modus.

        Args:
            hvac_mode: "OFF", "HEAT" oder "AUTO".
        """
        try:
            api_action = {
                HVACMode.HEAT: ACTION_ON,
                HVACMode.OFF: ACTION_OFF,
                HVACMode.AUTO: ACTION_AUTO,
            }.get(hvac_mode)

            if api_action is None:
                _LOGGER.warning("Nicht unterstützter HVAC-Modus: %s", hvac_mode)
                return

            _LOGGER.info(
                "Setze %s-Modus auf %s (API Aktion: %s)",
                "Heizung" if self.climate_type == "HEATER" else "Solar",
                hvac_mode,
                api_action
            )
            # Use the new API method
            result = await self.device.api.set_switch_state(
                key=self.climate_type, action=api_action, duration=0, last_value=0
            )
            if result.get("success", True): # Assume success if not explicitly false
                self._attr_hvac_mode = hvac_mode # Optimistic update
                self.async_write_ha_state()
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("Fehler beim Setzen des HVAC-Modus via API: %s", result.get("response", result))
                raise HomeAssistantError(f"Fehler beim Setzen des HVAC-Modus für {self.name} via API: {result.get('response', result)}")
        except (VioletPoolConnectionError, VioletPoolCommandError) as err:
            _LOGGER.error(f"API-Fehler beim Setzen des HVAC-Modus für {self.name} auf {hvac_mode}: {err}")
            raise HomeAssistantError(f"HVAC-Modus für {self.name} auf {hvac_mode} setzen fehlgeschlagen: {err}") from err
        except Exception as err:
            _LOGGER.exception(f"Unerwarteter Fehler beim Setzen des HVAC-Modus für {self.name} auf {hvac_mode}: {err}")
            raise HomeAssistantError(f"Unerwarteter Fehler beim Setzen des HVAC-Modus für {self.name} auf {hvac_mode}: {err}") from err

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
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = coordinator.config_entry.options.get(CONF_ACTIVE_FEATURES, [])
    entities = []

    # Setup HEATER if feature is active and data key exists
    heater_feature = CLIMATE_FEATURE_MAP.get("HEATER")
    if heater_feature and heater_feature in active_features:
        if "HEATER" in coordinator.data:
            _LOGGER.debug("Heizungs-Climate-Entity wird erstellt, da Feature '%s' aktiv und HEATER-Key vorhanden.", heater_feature)
            entities.append(VioletClimateEntity(coordinator, config_entry, "HEATER"))
        else:
            _LOGGER.debug("Heizungs-Climate-Entity nicht erstellt: HEATER-Key nicht in Coordinator-Daten, obwohl Feature '%s' aktiv.", heater_feature)
    elif heater_feature:
        _LOGGER.debug("Heizungs-Climate-Entity nicht erstellt: Feature '%s' nicht in active_features %s.", heater_feature, active_features)


    # Setup SOLAR if feature is active and data key exists
    solar_feature = CLIMATE_FEATURE_MAP.get("SOLAR")
    if solar_feature and solar_feature in active_features:
        if "SOLAR" in coordinator.data:
            _LOGGER.debug("Solar-Climate-Entity wird erstellt, da Feature '%s' aktiv und SOLAR-Key vorhanden.", solar_feature)
            entities.append(VioletClimateEntity(coordinator, config_entry, "SOLAR"))
        else:
            _LOGGER.debug("Solar-Climate-Entity nicht erstellt: SOLAR-Key nicht in Coordinator-Daten, obwohl Feature '%s' aktiv.", solar_feature)
    elif solar_feature:
        _LOGGER.debug("Solar-Climate-Entity nicht erstellt: Feature '%s' nicht in active_features %s.", solar_feature, active_features)


    if entities:
        async_add_entities(entities)
        _LOGGER.info("%d Climate-Entities hinzugefügt", len(entities))
    else:
        _LOGGER.info("Keine Heizungs- oder Solarabsorber-Daten gefunden")