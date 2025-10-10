"""Climate Integration für den Violet Pool Controller - OPTIMIZED VERSION."""
import logging
import asyncio
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    HVACAction,
    ClimateEntityDescription,
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

# Heater/Solar State Constants (basierend auf Violet Pool API)
STATE_OFF = 0
STATE_AUTO_HEATING = 1
STATE_AUTO_IDLE = 2
STATE_AUTO_ACTIVE = 3
STATE_MANUAL_ON = 4
STATE_AUTO_OFF = 5
STATE_MANUAL_OFF = 6

# Temperature limits
DEFAULT_MIN_TEMP = 20.0
DEFAULT_MAX_TEMP = 35.0
DEFAULT_TARGET_TEMP = 28.0
TEMP_STEP = 0.5

# Refresh delay after state change
REFRESH_DELAY = 0.3

# HVAC Mode Mapping - basierend auf State-Werten
HEATER_HVAC_MODES = {
    STATE_OFF: HVACMode.AUTO,
    STATE_AUTO_HEATING: HVACMode.AUTO,
    STATE_AUTO_IDLE: HVACMode.AUTO,
    STATE_AUTO_ACTIVE: HVACMode.AUTO,
    STATE_MANUAL_ON: HVACMode.HEAT,
    STATE_AUTO_OFF: HVACMode.AUTO,
    STATE_MANUAL_OFF: HVACMode.OFF,
}

# HVAC Action Mapping
HEATER_HVAC_ACTIONS = {
    STATE_OFF: HVACAction.IDLE,
    STATE_AUTO_HEATING: HVACAction.HEATING,
    STATE_AUTO_IDLE: HVACAction.IDLE,
    STATE_AUTO_ACTIVE: HVACAction.HEATING,
    STATE_MANUAL_ON: HVACAction.HEATING,
    STATE_AUTO_OFF: HVACAction.IDLE,
    STATE_MANUAL_OFF: HVACAction.OFF,
}

# Climate Feature Mapping
CLIMATE_FEATURE_MAP = {
    "HEATER": "heating",
    "SOLAR": "solar",
}

# Possible water temperature sensor keys (in order of preference)
WATER_TEMP_SENSORS = [
    "onewire1_value",
    "water_temp",
    "WATER_TEMPERATURE",
    "temp_value",
]


class VioletClimateEntity(VioletPoolControllerEntity, ClimateEntity):
    """Repräsentiert Heizungs- oder Solarsteuerung - OPTIMIZED VERSION."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]
    _attr_min_temp = DEFAULT_MIN_TEMP
    _attr_max_temp = DEFAULT_MAX_TEMP
    _attr_target_temperature_step = TEMP_STEP

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        climate_type: str,
    ) -> None:
        """Initialisiere Climate-Entity - OPTIMIZED VERSION."""
        name = "Heizung" if climate_type == "HEATER" else "Solarabsorber"
        icon = "mdi:radiator" if climate_type == "HEATER" else "mdi:solar-power"

        # Use proper ClimateEntityDescription
        climate_description = ClimateEntityDescription(
            key=climate_type,
            name=name,
            icon=icon,
        )

        super().__init__(coordinator, config_entry, climate_description)
        self.climate_type = climate_type
        self._attr_target_temperature = self._get_target_temperature()
        self._attr_hvac_mode = self._get_hvac_mode()
        
        _LOGGER.debug(
            "%s initialisiert: Ziel=%.1f°C, Modus=%s",
            name,
            self._attr_target_temperature,
            self._attr_hvac_mode,
        )

    def _get_target_temperature(self) -> float:
        """Hole Zieltemperatur mit Fallback."""
        key = f"{self.climate_type}_TARGET_TEMP"
        target = self.get_float_value(key, DEFAULT_TARGET_TEMP)
        
        # Validiere Temperatur innerhalb der Grenzen
        if not self.min_temp <= target <= self.max_temp:
            _LOGGER.warning(
                "Zieltemperatur %.1f°C außerhalb Bereich (%.1f-%.1f°C), verwende %.1f°C",
                target,
                self.min_temp,
                self.max_temp,
                DEFAULT_TARGET_TEMP,
            )
            return DEFAULT_TARGET_TEMP
        
        return target

    def _get_hvac_mode(self) -> str:
        """Ermittle HVAC-Modus basierend auf State."""
        state = self.get_int_value(self.climate_type, STATE_OFF)
        mode = HEATER_HVAC_MODES.get(state, HVACMode.OFF)
        
        _LOGGER.debug(
            "%s State %d → HVAC Mode %s",
            self.climate_type,
            state,
            mode,
        )
        
        return mode

    @property
    def hvac_mode(self) -> str:
        """Return current HVAC mode."""
        return self._get_hvac_mode()

    @property
    def hvac_action(self) -> str | None:
        """Gib aktuelle HVAC-Aktion zurück."""
        state = self.get_int_value(self.climate_type, STATE_OFF)
        action = HEATER_HVAC_ACTIONS.get(state, HVACAction.IDLE)
        
        _LOGGER.debug(
            "%s State %d → HVAC Action %s",
            self.climate_type,
            state,
            action,
        )
        
        return action

    @property
    def current_temperature(self) -> float | None:
        """Gib aktuelle Wassertemperatur zurück."""
        # Versuche alle bekannten Sensor-Keys
        for sensor_key in WATER_TEMP_SENSORS:
            if value := self.get_float_value(sensor_key, None):
                _LOGGER.debug("Wassertemperatur von '%s': %.1f°C", sensor_key, value)
                return value
        
        _LOGGER.debug(
            "Keine Wassertemperatur gefunden in Sensors: %s",
            WATER_TEMP_SENSORS,
        )
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return target temperature."""
        return self._get_target_temperature()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        state = self.get_int_value(self.climate_type, STATE_OFF)
        
        attributes = {
            "raw_state": state,
            "hvac_mode_from_state": HEATER_HVAC_MODES.get(state, "unknown"),
            "hvac_action_from_state": HEATER_HVAC_ACTIONS.get(state, "unknown"),
        }
        
        # Runtime information
        runtime_key = f"{self.climate_type}_RUNTIME"
        if self.coordinator.data and runtime_key in self.coordinator.data:
            attributes["runtime"] = self.get_str_value(runtime_key, "00h 00m 00s")
        
        return attributes

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Setze Zieltemperatur - OPTIMIZED VERSION."""
        if (temperature := kwargs.get("temperature")) is None:
            _LOGGER.warning("Keine Temperatur in kwargs angegeben")
            return

        # Validiere Temperaturbereich
        if not self._validate_temperature(temperature):
            return

        try:
            _LOGGER.info(
                "Setze %s-Temperatur auf %.1f°C",
                self.climate_type,
                temperature,
            )
            
            result = await self.device.api.set_device_temperature(
                self.climate_type, temperature
            )
            
            if result.get("success", True):
                _LOGGER.debug("Temperatur erfolgreich gesetzt: %s", result)
                
                # Optimistisches Update mit None-Check
                if self.coordinator.data is not None:
                    target_key = f"{self.climate_type}_TARGET_TEMP"
                    self.coordinator.data[target_key] = temperature
                    self._attr_target_temperature = temperature
                    self.async_write_ha_state()
                
                # Asynchroner Refresh
                asyncio.create_task(self._delayed_refresh())
            else:
                error_msg = result.get("response", "Unbekannter Fehler")
                _LOGGER.warning(
                    "Temperatur setzen möglicherweise fehlgeschlagen: %s",
                    error_msg,
                )
                raise HomeAssistantError(f"Temperatur setzen fehlgeschlagen: {error_msg}")
                
        except VioletPoolAPIError as err:
            _LOGGER.error("API-Fehler beim Setzen der Temperatur: %s", err)
            raise HomeAssistantError(f"Temperatur setzen fehlgeschlagen: {err}") from err
        except Exception as err:
            _LOGGER.error("Unerwarteter Fehler beim Setzen der Temperatur: %s", err)
            raise HomeAssistantError(f"Temperaturfehler: {err}") from err

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Setze HVAC-Modus - OPTIMIZED VERSION."""
        # Map HVAC mode to API action
        mode_action_map = {
            HVACMode.HEAT: ACTION_ON,
            HVACMode.OFF: ACTION_OFF,
            HVACMode.AUTO: ACTION_AUTO,
        }
        
        api_action = mode_action_map.get(hvac_mode)
        
        if not api_action:
            _LOGGER.warning("Nicht unterstützter HVAC-Modus: %s", hvac_mode)
            return

        try:
            _LOGGER.info(
                "Setze %s-Modus auf %s (API-Action: %s)",
                self.climate_type,
                hvac_mode,
                api_action,
            )
            
            result = await self.device.api.set_switch_state(
                self.climate_type, api_action
            )
            
            if result.get("success", True):
                _LOGGER.debug("HVAC-Modus erfolgreich gesetzt: %s", result)
                
                # Optimistisches Update mit None-Check
                if self.coordinator.data is not None:
                    # Bestimme erwarteten State basierend auf Aktion
                    expected_state = self._get_expected_state(api_action)
                    self.coordinator.data[self.climate_type] = expected_state
                    self._attr_hvac_mode = hvac_mode
                    self.async_write_ha_state()
                
                # Asynchroner Refresh
                asyncio.create_task(self._delayed_refresh())
            else:
                error_msg = result.get("response", "Unbekannter Fehler")
                _LOGGER.warning(
                    "HVAC-Modus setzen möglicherweise fehlgeschlagen: %s",
                    error_msg,
                )
                raise HomeAssistantError(f"HVAC-Modus setzen fehlgeschlagen: {error_msg}")
                
        except VioletPoolAPIError as err:
            _LOGGER.error("API-Fehler beim Setzen des HVAC-Modus: %s", err)
            raise HomeAssistantError(f"HVAC-Modus setzen fehlgeschlagen: {err}") from err
        except Exception as err:
            _LOGGER.error("Unerwarteter Fehler beim Setzen des HVAC-Modus: %s", err)
            raise HomeAssistantError(f"HVAC-Modusfehler: {err}") from err

    def _validate_temperature(self, temperature: float) -> bool:
        """Validiere Temperatur innerhalb der erlaubten Grenzen."""
        if not self.min_temp <= temperature <= self.max_temp:
            _LOGGER.warning(
                "Temperatur %.1f°C außerhalb erlaubtem Bereich (%.1f-%.1f°C)",
                temperature,
                self.min_temp,
                self.max_temp,
            )
            return False
        return True

    def _get_expected_state(self, action: str) -> int:
        """Bestimme erwarteten State basierend auf Aktion."""
        action_state_map = {
            ACTION_ON: STATE_MANUAL_ON,
            ACTION_OFF: STATE_MANUAL_OFF,
            ACTION_AUTO: STATE_AUTO_IDLE,
        }
        return action_state_map.get(action, STATE_OFF)

    async def _delayed_refresh(self) -> None:
        """Verzögerter Refresh ohne Blockierung des Hauptthreads."""
        try:
            await asyncio.sleep(REFRESH_DELAY)
            _LOGGER.debug("Requesting coordinator refresh for %s", self.climate_type)
            await self.coordinator.async_request_refresh()
            
            # Log neuen State nach Refresh
            if self.coordinator.data:
                new_state = self.coordinator.data.get(self.climate_type, "UNKNOWN")
                new_temp = self.coordinator.data.get(
                    f"{self.climate_type}_TARGET_TEMP", "UNKNOWN"
                )
                _LOGGER.debug(
                    "State nach Refresh: %s=%s, Target=%s",
                    self.climate_type,
                    new_state,
                    new_temp,
                )
        except Exception as err:
            _LOGGER.error("Fehler beim verzögerten Refresh: %s", err)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Richte Climate-Entities ein - OPTIMIZED VERSION."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    entities = []

    _LOGGER.info("Climate Setup - Active features: %s", active_features)

    # Diagnose für verfügbare Daten
    if coordinator.data:
        _LOGGER.debug(
            "Coordinator data keys: %d",
            len(coordinator.data.keys()),
        )

    for climate_type, feature in CLIMATE_FEATURE_MAP.items():
        # Prüfe ob Feature aktiv ist
        if feature not in active_features:
            _LOGGER.debug(
                "%s-Entity nicht erstellt: Feature '%s' nicht aktiv",
                climate_type,
                feature,
            )
            continue
        
        # Prüfe ob Daten verfügbar sind
        if coordinator.data and climate_type not in coordinator.data:
            _LOGGER.debug(
                "%s-Entity nicht erstellt: Keine Daten verfügbar",
                climate_type,
            )
            continue
        
        _LOGGER.debug(
            "Erstelle %s-Entity: Feature '%s' aktiv",
            climate_type,
            feature,
        )
        entities.append(VioletClimateEntity(coordinator, config_entry, climate_type))

    if entities:
        async_add_entities(entities)
        _LOGGER.info(
            "✓ %d Climate-Entities erfolgreich eingerichtet: %s",
            len(entities),
            [e.name for e in entities],
        )
    else:
        _LOGGER.warning("⚠ Keine Climate-Entities eingerichtet")