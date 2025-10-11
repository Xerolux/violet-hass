"""Switch Integration für den Violet Pool Controller - OPTIMIZED VERSION."""
import logging
import asyncio
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, SWITCHES, CONF_ACTIVE_FEATURES, ACTION_ON, ACTION_OFF, STATE_MAP
from .api import VioletPoolAPIError
from .entity import VioletPoolControllerEntity
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# State Constants - basierend auf Violet Pool API Dokumentation
STATE_OFF = 0
STATE_AUTO_ON = 1
STATE_MANUAL_ON = 4
STATE_AUTO_OFF = 5
STATE_MANUAL_OFF = 6

# States die als "ON" interpretiert werden
ON_STATES = {1, 2, 3, 4}
# States die als "OFF" interpretiert werden
OFF_STATES = {0, 5, 6}

# Refresh Verzögerung nach State-Änderung (in Sekunden)
REFRESH_DELAY = 0.3


class VioletSwitch(VioletPoolControllerEntity, SwitchEntity):
    """Repräsentation eines Violet Pool Switches - OPTIMIZED VERSION."""
    entity_description: SwitchEntityDescription

    def __init__(
        self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry,
        description: SwitchEntityDescription
    ) -> None:
        """Initialisiere den Switch."""
        super().__init__(coordinator, config_entry, description)
        _LOGGER.debug("Initialisiere Switch: %s (unique_id=%s)", self.entity_id, self._attr_unique_id)

    @property
    def is_on(self) -> bool:
        """Gibt True zurück, wenn der Switch eingeschaltet ist."""
        return self._get_switch_state()

    def _get_switch_state(self) -> bool:
        """Rufe den aktuellen Switch-Zustand ab - OPTIMIZED VERSION."""
        key = self.entity_description.key
        raw_state = self.get_value(key, "")
        
        _LOGGER.debug("Switch state check für %s: raw=%s (type=%s)", 
                     key, raw_state, type(raw_state).__name__)
        
        if raw_state is None:
            _LOGGER.debug("State ist None für %s - returning OFF", key)
            return False
        
        # Versuche Integer-Konvertierung
        state_int = self._convert_to_int(raw_state)
        
        if state_int is not None:
            return self._interpret_int_state(state_int, key)
        
        # Fallback auf String-Interpretation
        return self._interpret_string_state(raw_state, key)

    def _convert_to_int(self, value: Any) -> int | None:
        """Konvertiere Wert zu Integer, wenn möglich."""
        try:
            if isinstance(value, (int, float)):
                return int(value)
            if isinstance(value, str) and value.isdigit():
                return int(value)
        except (ValueError, TypeError):
            pass
        return None

    def _interpret_int_state(self, state_int: int, key: str) -> bool:
        """Interpretiere Integer State-Wert."""
        # Prüfe explizite STATE_MAP Einträge
        if state_int in STATE_MAP:
            result = STATE_MAP[state_int]
            _LOGGER.debug("State %d für %s in STATE_MAP gefunden → %s", state_int, key, result)
            return result
        
        # Prüfe bekannte ON/OFF States
        if state_int in ON_STATES:
            _LOGGER.debug("State %d für %s in ON_STATES → True", state_int, key)
            return True
        
        if state_int in OFF_STATES:
            _LOGGER.debug("State %d für %s in OFF_STATES → False", state_int, key)
            return False
        
        # Unbekannter State - konservativ auf OFF setzen
        _LOGGER.warning("Unbekannter State %d für %s - defaulting to OFF", state_int, key)
        return False

    def _interpret_string_state(self, raw_state: Any, key: str) -> bool:
        """Interpretiere String State-Wert."""
        state_str = str(raw_state).upper().strip()
        
        # Prüfe STATE_MAP für String-Einträge
        if state_str in STATE_MAP:
            result = STATE_MAP[state_str]
            _LOGGER.debug("String '%s' für %s in STATE_MAP → %s", state_str, key, result)
            return result
        
        # Bekannte boolean String-Werte
        boolean_on_states = {"TRUE", "ON", "1", "ACTIVE", "RUNNING", "MANUAL", "MAN"}
        boolean_off_states = {"FALSE", "OFF", "0", "INACTIVE", "STOPPED"}
        
        if state_str in boolean_on_states:
            _LOGGER.debug("String '%s' für %s → ON", state_str, key)
            return True
        
        if state_str in boolean_off_states:
            _LOGGER.debug("String '%s' für %s → OFF", state_str, key)
            return False
        
        # Unbekannter String - defaulting to OFF
        _LOGGER.warning("Unbekannter State '%s' für %s - defaulting to OFF", state_str, key)
        return False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes with detailed state information."""
        key = self.entity_description.key
        raw_state = self.get_value(key, "")
        current_result = self._get_switch_state()
        
        attributes = {
            "raw_state": str(raw_state),
            "state_type": type(raw_state).__name__,
            "interpreted_as": "ON" if current_result else "OFF",
            "state_logic": self._explain_state_logic(raw_state),
        }
        
        # Zusätzliche Attribute für PUMP
        if key == "PUMP":
            attributes.update({
                "pump_runtime": self.get_str_value("PUMP_RUNTIME", "00h 00m 00s"),
                "pump_last_on": self.get_value("PUMP_LAST_ON", 0),
                "pump_last_off": self.get_value("PUMP_LAST_OFF", 0),
                "pump_rpm_2": self.get_value("PUMP_RPM_2", 0),
                "pump_state_raw": self.get_value("PUMPSTATE", ""),
            })
        
        # Runtime-Informationen
        runtime_key = f"{key}_RUNTIME"
        if self.coordinator.data and runtime_key in self.coordinator.data:
            attributes["runtime"] = self.get_str_value(runtime_key, "00h 00m 00s")
        
        return attributes

    def _explain_state_logic(self, raw_state: Any) -> str:
        """Explain how the state was interpreted for debugging."""
        if raw_state is None:
            return "None value → OFF"
        
        state_int = self._convert_to_int(raw_state)
        
        if state_int is not None:
            if state_int in STATE_MAP:
                return f"Integer {state_int} in STATE_MAP → {STATE_MAP[state_int]}"
            elif state_int in ON_STATES:
                return f"Integer {state_int} in ON_STATES → True"
            elif state_int in OFF_STATES:
                return f"Integer {state_int} in OFF_STATES → False"
            else:
                return f"Integer {state_int} unknown → False (default)"
        
        state_str = str(raw_state).upper().strip()
        if state_str in STATE_MAP:
            return f"String '{state_str}' in STATE_MAP → {STATE_MAP[state_str]}"
        
        return f"String '{state_str}' → default logic"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Schalte den Switch ein."""
        await self._set_switch_state(ACTION_ON, **kwargs)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Schalte den Switch aus."""
        await self._set_switch_state(ACTION_OFF, **kwargs)

    async def _set_switch_state(self, action: str, **kwargs: Any) -> None:
        """Setze den Switch-Zustand mit optimierter Fehlerbehandlung."""
        key = self.entity_description.key
        
        try:
            _LOGGER.info("Setze Switch %s auf %s", key, action)
            
            # Für PUMP: Unterstütze erweiterte Parameter
            if key == "PUMP" and action == ACTION_ON:
                speed = self._validate_speed(kwargs.get("speed", 2))
                duration = self._validate_duration(kwargs.get("duration", 0))
                
                _LOGGER.debug("PUMP Parameter: speed=%s, duration=%s", speed, duration)
                result = await self.device.api.set_switch_state(
                    key=key, 
                    action=action, 
                    duration=duration,
                    last_value=speed
                )
            else:
                # Standard Switch-Aktion
                result = await self.device.api.set_switch_state(key=key, action=action)
            
            _LOGGER.debug("API Result: %s", result)
            
            if result.get("success", True):
                _LOGGER.info("Switch %s erfolgreich auf %s gesetzt", key, action)
                
                # Optimistische State-Aktualisierung mit None-Check
                if self.coordinator.data is not None:
                    expected_state = STATE_MANUAL_ON if action == ACTION_ON else STATE_OFF
                    self.coordinator.data[key] = expected_state
                    _LOGGER.debug("Optimistisches Update: %s = %s", key, expected_state)
                    self.async_write_ha_state()
                
                # Asynchroner Refresh ohne Blockierung
                task = asyncio.create_task(self._delayed_refresh(key))
                task.add_done_callback(lambda t: self._handle_refresh_error(t, key))
            else:
                error_msg = result.get("response", "Unbekannter Fehler")
                _LOGGER.warning("Switch %s Aktion %s möglicherweise fehlgeschlagen: %s", 
                              key, action, error_msg)
                # Trotzdem Refresh anfordern, um tatsächlichen State zu holen
                task = asyncio.create_task(self._delayed_refresh(key))
                task.add_done_callback(lambda t: self._handle_refresh_error(t, key))
            
        except VioletPoolAPIError as err:
            _LOGGER.error("API-Fehler beim Setzen von Switch %s auf %s: %s", key, action, err)
            raise HomeAssistantError(f"Switch-Aktion fehlgeschlagen: {err}") from err
        except Exception as err:
            _LOGGER.error("Unerwarteter Fehler beim Setzen von Switch %s: %s", key, err)
            raise HomeAssistantError(f"Switch-Fehler: {err}") from err

    async def _delayed_refresh(self, key: str) -> None:
        """Verzögerter Refresh ohne Blockierung des Hauptthreads."""
        try:
            await asyncio.sleep(REFRESH_DELAY)
            _LOGGER.debug("Requesting coordinator refresh for %s", key)
            await self.coordinator.async_request_refresh()
            
            # Log neuen State nach Refresh
            if self.coordinator.data:
                new_state = self.coordinator.data.get(key, "UNKNOWN")
                _LOGGER.debug("State nach Refresh: %s = %s", key, new_state)
        except Exception as err:
            _LOGGER.error("Fehler beim verzögerten Refresh: %s", err)


    def _handle_refresh_error(self, task: asyncio.Task, key: str) -> None:
        """Handle errors in refresh task without crashing."""
        try:
            if not task.cancelled() and (exc := task.exception()):
                _LOGGER.error(
                    "Refresh task failed for switch %s (key: %s): %s",
                    self.entity_id,
                    key,
                    exc
                )
        except Exception as err:
            _LOGGER.error("Error handling refresh task exception: %s", err)

    def _validate_speed(self, speed: Any) -> int:
        """Validiere und normalisiere Speed-Parameter."""
        try:
            speed_int = int(speed)
            if 1 <= speed_int <= 4:
                return speed_int
            _LOGGER.warning("Ungültiger Speed-Wert %s, verwende Default 2", speed)
            return 2
        except (ValueError, TypeError):
            _LOGGER.warning("Ungültiger Speed-Typ %s, verwende Default 2", type(speed))
            return 2

    def _validate_duration(self, duration: Any) -> int:
        """Validiere und normalisiere Duration-Parameter."""
        try:
            duration_int = int(duration)
            if duration_int >= 0:
                return duration_int
            _LOGGER.warning("Negative Duration %s, verwende 0", duration)
            return 0
        except (ValueError, TypeError):
            _LOGGER.warning("Ungültiger Duration-Typ %s, verwende 0", type(duration))
            return 0


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Richte Switches für die Config Entry ein - OPTIMIZED VERSION."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    entities: list[SwitchEntity] = []

    _LOGGER.info("Switch Setup - Active features: %s", active_features)
    
    if coordinator.data:
        _LOGGER.debug("Coordinator data keys: %d", len(coordinator.data.keys()))
        
        # Diagnose für wichtige States
        for key in ["PUMP", "SOLAR", "HEATER"]:
            if key in coordinator.data:
                value = coordinator.data[key]
                state_int = int(value) if isinstance(value, (int, float)) or str(value).isdigit() else None
                expected = "ON" if state_int in ON_STATES else "OFF" if state_int in OFF_STATES else "UNKNOWN"
                _LOGGER.debug("%s: raw=%s → %s", key, value, expected)

    # Create switch descriptions from SWITCHES constant
    for switch_config in SWITCHES:
        description = SwitchEntityDescription(
            key=switch_config["key"],
            name=switch_config["name"],
            icon=switch_config.get("icon"),
        )
        
        feature_id = switch_config.get("feature_id")
        
        # Check if feature is active
        if feature_id and feature_id not in active_features:
            _LOGGER.debug("Überspringe Switch %s: Feature %s nicht aktiv", description.key, feature_id)
            continue
        
        _LOGGER.debug("Erstelle Switch: %s", description.name)
        entities.append(VioletSwitch(coordinator, config_entry, description))

    if entities:
        async_add_entities(entities)
        _LOGGER.info("✓ %d Switches erfolgreich eingerichtet", len(entities))
        
        # Final state check für key switches
        if coordinator.data:
            for entity in entities:
                key = entity.entity_description.key
                if key in ["PUMP", "SOLAR", "HEATER"] and key in coordinator.data:
                    raw_state = coordinator.data[key]
                    should_be_on = entity._get_switch_state()
                    _LOGGER.debug("Final check %s: raw=%s → display=%s", 
                                key, raw_state, "ON" if should_be_on else "OFF")
    else:
        _LOGGER.warning("⚠ Keine Switches eingerichtet")