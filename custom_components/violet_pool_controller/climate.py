"""Climate Integration für den Violet Pool Controller - FULLY PROTECTED & THREAD-SAFE VERSION."""

import asyncio
import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import VioletPoolAPIError
from .const import ACTION_AUTO, ACTION_OFF, ACTION_ON, CONF_ACTIVE_FEATURES, DOMAIN
from .device import VioletPoolDataUpdateCoordinator
from .entity import VioletPoolControllerEntity

_LOGGER = logging.getLogger(__name__)

# State Constants
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

REFRESH_DELAY = 0.3

# HVAC Mode Mapping
HEATER_HVAC_MODES = {
    STATE_OFF: HVACMode.AUTO,
    STATE_AUTO_HEATING: HVACMode.AUTO,
    STATE_AUTO_IDLE: HVACMode.AUTO,
    STATE_AUTO_ACTIVE: HVACMode.AUTO,
    STATE_MANUAL_ON: HVACMode.HEAT,
    STATE_AUTO_OFF: HVACMode.AUTO,
    STATE_MANUAL_OFF: HVACMode.OFF,
}

HEATER_HVAC_ACTIONS = {
    STATE_OFF: HVACAction.IDLE,
    STATE_AUTO_HEATING: HVACAction.HEATING,
    STATE_AUTO_IDLE: HVACAction.IDLE,
    STATE_AUTO_ACTIVE: HVACAction.HEATING,
    STATE_MANUAL_ON: HVACAction.HEATING,
    STATE_AUTO_OFF: HVACAction.IDLE,
    STATE_MANUAL_OFF: HVACAction.OFF,
}

CLIMATE_FEATURE_MAP = {
    "HEATER": "heating",
    "SOLAR": "solar",
}

WATER_TEMP_SENSORS = [
    "onewire1_value",
    "water_temp",
    "WATER_TEMPERATURE",
    "temp_value",
]


class VioletClimateEntity(VioletPoolControllerEntity, ClimateEntity):
    """Climate Entity - FULLY PROTECTED & THREAD-SAFE VERSION."""

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
        """Initialisiere Climate-Entity - FULLY PROTECTED VERSION."""
        name = "Heizung" if climate_type == "HEATER" else "Solarabsorber"
        icon = "mdi:radiator" if climate_type == "HEATER" else "mdi:solar-power"

        climate_description = ClimateEntityDescription(
            key=climate_type,
            name=name,
            icon=icon,
        )

        super().__init__(coordinator, config_entry, climate_description)
        self.climate_type = climate_type

        # ✅ FIXED: Lokale Cache-Variablen für optimistisches Update
        self._optimistic_target_temp: float | None = None
        self._optimistic_hvac_mode: str | None = None

        self._attr_target_temperature = self._get_target_temperature()
        self._attr_hvac_mode = self._get_hvac_mode()

        _LOGGER.debug(
            "%s initialisiert: Ziel=%.1f°C, Modus=%s",
            name,
            self._attr_target_temperature,
            self._attr_hvac_mode,
        )

    def _get_target_temperature(self) -> float:
        """Hole Zieltemperatur - FULLY PROTECTED VERSION."""
        # ✅ FIXED: Prüfe zuerst optimistischen Cache
        if self._optimistic_target_temp is not None:
            return self._optimistic_target_temp

        # ✅ CRITICAL: None-Check vor Datenzugriff
        if self.coordinator.data is None:
            _LOGGER.debug(
                "Coordinator data is None - returning default target %.1f°C",
                DEFAULT_TARGET_TEMP,
            )
            return DEFAULT_TARGET_TEMP

        key = f"{self.climate_type}_TARGET_TEMP"
        target = self.get_float_value(key, DEFAULT_TARGET_TEMP)
        # get_float_value with a non-None default will always return a float
        assert target is not None

        # Validiere Temperatur
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
        """Ermittle HVAC-Modus - FULLY PROTECTED VERSION."""
        # ✅ FIXED: Prüfe zuerst optimistischen Cache
        if self._optimistic_hvac_mode is not None:
            return self._optimistic_hvac_mode

        # ✅ CRITICAL: None-Check
        if self.coordinator.data is None:
            _LOGGER.debug("Coordinator data is None - returning OFF mode")
            return HVACMode.OFF

        state = self.get_int_value(self.climate_type, STATE_OFF)
        mode = HEATER_HVAC_MODES.get(state, HVACMode.OFF)

        _LOGGER.debug("%s State %d → HVAC Mode %s", self.climate_type, state, mode)
        return mode

    @property
    def hvac_mode(self) -> str:
        """Return current HVAC mode."""
        return self._get_hvac_mode()

    @property
    def hvac_action(self) -> str | None:
        """Gib aktuelle HVAC-Aktion zurück - FULLY PROTECTED VERSION."""
        # ✅ CRITICAL: None-Check
        if self.coordinator.data is None:
            _LOGGER.debug("Coordinator data is None - returning IDLE action")
            return HVACAction.IDLE

        state = self.get_int_value(self.climate_type, STATE_OFF)
        action = HEATER_HVAC_ACTIONS.get(state, HVACAction.IDLE)

        _LOGGER.debug("%s State %d → HVAC Action %s", self.climate_type, state, action)
        return action

    @property
    def current_temperature(self) -> float | None:
        """Gib aktuelle Wassertemperatur zurück - FULLY PROTECTED VERSION."""
        # ✅ CRITICAL: None-Check
        if self.coordinator.data is None:
            _LOGGER.debug("Coordinator data is None - no current temperature available")
            return None

        # Versuche alle bekannten Sensor-Keys
        for sensor_key in WATER_TEMP_SENSORS:
            value = self.get_float_value(sensor_key, None)
            if value is not None:
                _LOGGER.debug("Wassertemperatur von '%s': %.1f°C", sensor_key, value)
                return value

        _LOGGER.debug("Keine Wassertemperatur gefunden in: %s", WATER_TEMP_SENSORS)
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return target temperature."""
        return self._get_target_temperature()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes - FULLY PROTECTED VERSION."""
        # ✅ CRITICAL: None-Check vor Daten-Zugriff
        if self.coordinator.data is None:
            return {
                "state_type": "unavailable",
                "note": "Coordinator data not available",
            }

        state = self.get_int_value(self.climate_type, STATE_OFF)

        attributes = {
            "raw_state": state,
            "hvac_mode_from_state": HEATER_HVAC_MODES.get(state, "unknown"),
            "hvac_action_from_state": HEATER_HVAC_ACTIONS.get(state, "unknown"),
        }

        # ✅ FIXED: Zeige optimistischen Cache-Status
        if self._optimistic_target_temp is not None:
            attributes["optimistic_target"] = self._optimistic_target_temp
            attributes["pending_update"] = True

        # Runtime information mit None-Check
        runtime_key = f"{self.climate_type}_RUNTIME"
        if runtime_key in self.coordinator.data:
            attributes["runtime"] = self.get_str_value(runtime_key, "00h 00m 00s")

        return attributes

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Setze Zieltemperatur - FULLY PROTECTED & THREAD-SAFE VERSION."""
        temperature = kwargs.get("temperature")
        if temperature is None:
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

                # ✅ FIXED: NUR lokale Variablen setzen, KEINE coordinator.data Mutation!
                self._optimistic_target_temp = temperature
                self._attr_target_temperature = temperature
                self.async_write_ha_state()

                _LOGGER.debug(
                    "Optimistisches Update: %.1f°C (lokaler Cache, kein coordinator.data mutiert)",
                    temperature,
                )

                # Asynchroner Refresh holt echte Daten und resettet Cache
                asyncio.create_task(self._delayed_refresh())
            else:
                error_msg = result.get("response", "Unbekannter Fehler")
                _LOGGER.warning("Temperatur setzen fehlgeschlagen: %s", error_msg)
                raise HomeAssistantError(
                    f"Temperatur setzen fehlgeschlagen: {error_msg}"
                )

        except VioletPoolAPIError as err:
            _LOGGER.error("API-Fehler beim Setzen der Temperatur: %s", err)
            raise HomeAssistantError(
                f"Temperatur setzen fehlgeschlagen: {err}"
            ) from err
        except Exception as err:
            _LOGGER.error("Unerwarteter Fehler: %s", err)
            raise HomeAssistantError(f"Temperaturfehler: {err}") from err

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Setze HVAC-Modus - FULLY PROTECTED & THREAD-SAFE VERSION."""
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

                # ✅ FIXED: NUR lokale Variablen setzen, KEINE coordinator.data Mutation!
                self._optimistic_hvac_mode = hvac_mode
                self._attr_hvac_mode = hvac_mode
                self.async_write_ha_state()

                _LOGGER.debug(
                    "Optimistisches Update: %s (lokaler Cache, kein coordinator.data mutiert)",
                    hvac_mode,
                )

                # Asynchroner Refresh holt echte Daten und resettet Cache
                asyncio.create_task(self._delayed_refresh())
            else:
                error_msg = result.get("response", "Unbekannter Fehler")
                _LOGGER.warning("HVAC-Modus setzen fehlgeschlagen: %s", error_msg)
                raise HomeAssistantError(
                    f"HVAC-Modus setzen fehlgeschlagen: {error_msg}"
                )

        except VioletPoolAPIError as err:
            _LOGGER.error("API-Fehler beim Setzen des HVAC-Modus: %s", err)
            raise HomeAssistantError(
                f"HVAC-Modus setzen fehlgeschlagen: {err}"
            ) from err
        except Exception as err:
            _LOGGER.error("Unerwarteter Fehler: %s", err)
            raise HomeAssistantError(f"HVAC-Modusfehler: {err}") from err

    def _validate_temperature(self, temperature: float) -> bool:
        """Validiere Temperatur."""
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
        """Bestimme erwarteten State."""
        action_state_map = {
            ACTION_ON: STATE_MANUAL_ON,
            ACTION_OFF: STATE_MANUAL_OFF,
            ACTION_AUTO: STATE_AUTO_IDLE,
        }
        return action_state_map.get(action, STATE_OFF)

    async def _delayed_refresh(self) -> None:
        """
        Verzögerter Refresh - FULLY PROTECTED & THREAD-SAFE VERSION.

        ✅ FIXED: Resettet optimistische Cache-Werte nach erfolgreichem Refresh.
        """
        try:
            await asyncio.sleep(REFRESH_DELAY)
            _LOGGER.debug("Requesting coordinator refresh for %s", self.climate_type)
            await self.coordinator.async_request_refresh()

            # ✅ FIXED: Reset optimistische Cache-Werte nach Refresh
            if self.coordinator.last_update_success:
                old_optimistic_temp = self._optimistic_target_temp
                old_optimistic_mode = self._optimistic_hvac_mode

                self._optimistic_target_temp = None
                self._optimistic_hvac_mode = None

                if old_optimistic_temp is not None or old_optimistic_mode is not None:
                    _LOGGER.debug(
                        "Optimistische Cache-Werte nach Refresh gelöscht "
                        "(temp: %s, mode: %s)",
                        old_optimistic_temp,
                        old_optimistic_mode,
                    )

            # ✅ CRITICAL: None-Check nach Refresh
            if self.coordinator.data is not None:
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
            else:
                _LOGGER.debug(
                    "Coordinator data is None nach Refresh für %s", self.climate_type
                )
        except Exception as err:
            _LOGGER.error("Fehler beim verzögerten Refresh: %s", err)
            # Bei Fehler auch Cache löschen
            self._optimistic_target_temp = None
            self._optimistic_hvac_mode = None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Richte Climate-Entities ein - FULLY PROTECTED VERSION."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )
    entities = []

    _LOGGER.info("Climate Setup - Active features: %s", active_features)

    # ✅ CRITICAL: None-Check für Diagnose
    if coordinator.data is not None:
        _LOGGER.debug("Coordinator data keys: %d", len(coordinator.data.keys()))
    else:
        _LOGGER.warning("Coordinator data is None bei Climate Setup")

    for climate_type, feature in CLIMATE_FEATURE_MAP.items():
        # Prüfe ob Feature aktiv
        if feature not in active_features:
            _LOGGER.debug(
                "%s-Entity nicht erstellt: Feature '%s' nicht aktiv",
                climate_type,
                feature,
            )
            continue

        # ✅ CRITICAL: None-Check vor Daten-Prüfung
        if coordinator.data is not None:
            if climate_type not in coordinator.data:
                _LOGGER.debug(
                    "%s-Entity nicht erstellt: Keine Daten verfügbar",
                    climate_type,
                )
                continue
        else:
            _LOGGER.debug(
                "%s-Entity wird erstellt trotz fehlender Daten (Coordinator offline?)",
                climate_type,
            )

        _LOGGER.debug("Erstelle %s-Entity: Feature '%s' aktiv", climate_type, feature)
        entities.append(VioletClimateEntity(coordinator, config_entry, climate_type))

    if entities:
        async_add_entities(entities)
        _LOGGER.info(
            "✓ %d Climate-Entities erfolgreich eingerichtet: %s",
            len(entities),
            [e.name for e in entities],
        )
    else:
        _LOGGER.debug(
            "Keine Climate-Entities eingerichtet (keine Features aktiviert oder keine Daten)"
        )
