"""Switch Integration für den Violet Pool Controller - IMPROVED DEBUG VERSION."""
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

class VioletSwitch(VioletPoolControllerEntity, SwitchEntity):
    """Repräsentation eines Violet Pool Switches - IMPROVED DEBUG VERSION."""
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
        """Rufe den aktuellen Switch-Zustand ab - IMPROVED DEBUG VERSION."""
        key = self.entity_description.key
        raw_state = self.get_value(key, "")
        
        # DETAILED DEBUG LOGGING
        _LOGGER.info("🔍 SWITCH STATE DEBUG für '%s':", key)
        _LOGGER.info("  Raw state: %s (type: %s)", raw_state, type(raw_state))
        
        if raw_state is None:
            _LOGGER.info("  ❌ State ist None → OFF")
            return False
        
        # Konvertiere zu verschiedenen Formaten für Tests
        state_str = str(raw_state).upper().strip()
        state_int = None
        
        try:
            state_int = int(raw_state) if isinstance(raw_state, (int, float)) or str(raw_state).isdigit() else None
        except (ValueError, TypeError):
            state_int = None
        
        _LOGGER.info("  String format: '%s'", state_str)
        _LOGGER.info("  Integer format: %s", state_int)
        
        # Test 1: Direct integer mapping (most reliable)
        if state_int is not None:
            if state_int in STATE_MAP:
                result = STATE_MAP[state_int]
                _LOGGER.info("  ✅ Integer mapping: %d → %s", state_int, result)
                return result
            else:
                # Fallback für unbekannte Integer-Werte
                # Basierend auf API-Doku: 1,2,3,4 = ON, 0,5,6 = OFF
                result = state_int in [1, 2, 3, 4]
                _LOGGER.info("  ✅ Integer fallback: %d → %s (1,2,3,4=ON)", state_int, result)
                return result
        
        # Test 2: String mapping in STATE_MAP
        if state_str in STATE_MAP:
            result = STATE_MAP[state_str]
            _LOGGER.info("  ✅ String mapping: '%s' → %s", state_str, result)
            return result
        
        # Test 3: Known boolean strings
        boolean_on_states = ["TRUE", "ON", "1", "ACTIVE", "RUNNING", "MANUAL", "MAN"]
        if state_str in boolean_on_states:
            _LOGGER.info("  ✅ Boolean string: '%s' → True", state_str)
            return True
        
        # Test 4: Default für unbekannte States
        _LOGGER.info("  ⚠️ Unbekannter State '%s' → False (default)", state_str)
        return False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes with detailed state information."""
        key = self.entity_description.key
        raw_state = self.get_value(key, "")
        
        # Determine what the state means based on our logic
        current_result = self._get_switch_state()
        
        attributes = {
            "raw_state": str(raw_state),
            "state_type": type(raw_state).__name__,
            "interpreted_as": "ON" if current_result else "OFF",
            "state_logic": self._explain_state_logic(raw_state),
        }
        
        # Zusätzliche Attribute für PUMP
        if key == "PUMP":
            pump_rpm_2 = self.get_value("PUMP_RPM_2", 0)
            attributes.update({
                "pump_runtime": self.get_str_value("PUMP_RUNTIME", "00h 00m 00s"),
                "pump_last_on": self.get_value("PUMP_LAST_ON", 0),
                "pump_last_off": self.get_value("PUMP_LAST_OFF", 0),
                "pump_rpm_2": pump_rpm_2,  # This seems to be the active RPM level
                "pump_state_raw": self.get_value("PUMPSTATE", ""),
            })
        
        # Runtime-Informationen
        runtime_key = f"{key}_RUNTIME"
        if runtime_key in (self.coordinator.data or {}):
            attributes["runtime"] = self.get_str_value(runtime_key, "00h 00m 00s")
        
        return attributes

    def _explain_state_logic(self, raw_state) -> str:
        """Explain how the state was interpreted for debugging."""
        if raw_state is None:
            return "None value → OFF"
        
        try:
            state_int = int(raw_state) if isinstance(raw_state, (int, float)) or str(raw_state).isdigit() else None
            if state_int is not None:
                if state_int in STATE_MAP:
                    return f"Integer {state_int} found in STATE_MAP → {STATE_MAP[state_int]}"
                else:
                    result = state_int in [1, 2, 3, 4]
                    return f"Integer {state_int} not in STATE_MAP, using fallback logic → {result}"
        except (ValueError, TypeError):
            pass
        
        state_str = str(raw_state).upper().strip()
        if state_str in STATE_MAP:
            return f"String '{state_str}' found in STATE_MAP → {STATE_MAP[state_str]}"
        
        return f"String '{state_str}' using default logic"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Schalte den Switch ein."""
        await self._set_switch_state(ACTION_ON, **kwargs)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Schalte den Switch aus."""
        await self._set_switch_state(ACTION_OFF, **kwargs)

    async def _set_switch_state(self, action: str, **kwargs: Any) -> None:
        """Setze den Switch-Zustand mit verbesserter Fehlerbehandlung."""
        key = self.entity_description.key
        
        try:
            _LOGGER.info("🔄 Setze Switch %s auf %s", key, action)
            
            # Für PUMP: Unterstütze erweiterte Parameter
            if key == "PUMP" and action == ACTION_ON:
                speed = kwargs.get("speed", 2)
                duration = kwargs.get("duration", 0)
                
                _LOGGER.info("  PUMP Parameter: speed=%s, duration=%s", speed, duration)
                result = await self.device.api.set_switch_state(
                    key=key, 
                    action=action, 
                    duration=duration,
                    last_value=speed
                )
            else:
                # Standard Switch-Aktion
                result = await self.device.api.set_switch_state(key=key, action=action)
            
            _LOGGER.info("  API Result: %s", result)
            
            if result.get("success", True):
                _LOGGER.info("  ✅ Switch %s erfolgreich auf %s gesetzt", key, action)
                
                # Optimistische State-Aktualisierung
                expected_state = 4 if action == ACTION_ON else 0  # Use state 4 for manual ON
                self.coordinator.data[key] = expected_state
                _LOGGER.info("  📝 Optimistische Update: %s = %s", key, expected_state)
                
                self.async_write_ha_state()
            else:
                error_msg = result.get("response", "Unbekannter Fehler")
                _LOGGER.warning("  ⚠️ Switch %s Aktion %s möglicherweise fehlgeschlagen: %s", 
                              key, action, error_msg)
            
            # Request refresh nach kurzer Verzögerung
            await asyncio.sleep(1.0)  # Longer delay to ensure controller updates
            _LOGGER.info("  🔄 Requesting coordinator refresh...")
            await self.coordinator.async_request_refresh()
            
            # Log the new state after refresh
            new_state = self.coordinator.data.get(key, "UNKNOWN")
            _LOGGER.info("  📊 State after refresh: %s = %s", key, new_state)
            
        except VioletPoolAPIError as err:
            _LOGGER.error("❌ API-Fehler beim Setzen von Switch %s auf %s: %s", key, action, err)
            raise HomeAssistantError(f"Switch-Aktion fehlgeschlagen: {err}") from err
        except Exception as err:
            _LOGGER.error("❌ Unerwarteter Fehler beim Setzen von Switch %s: %s", key, err)
            raise HomeAssistantError(f"Switch-Fehler: {err}") from err

async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Richte Switches für die Config Entry ein - MIT VERBESSERTER DIAGNOSTIK."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    active_features = config_entry.options.get(CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, []))
    entities: list[SwitchEntity] = []

    # Debug-Logging für Setup-Diagnose
    _LOGGER.info("🔍 SWITCH SETUP DEBUG:")
    _LOGGER.info("  Active features: %s", active_features)
    _LOGGER.info("  Coordinator data keys count: %d", len(coordinator.data.keys()) if coordinator.data else 0)
    
    # Spezielle Diagnose für wichtige States
    if coordinator.data:
        for key in ["PUMP", "SOLAR", "HEATER"]:
            if key in coordinator.data:
                value = coordinator.data[key]
                expected_display = "ON" if value in [1, 2, 3, 4] else "OFF"
                _LOGGER.info("  %s: %s → should display as %s", key, value, expected_display)

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
        
        # Create switch if feature is active or no feature requirement
        _LOGGER.debug("Erstelle Switch: %s", description.name)
        entities.append(VioletSwitch(coordinator, config_entry, description))

    if entities:
        async_add_entities(entities)
        _LOGGER.info("✅ %d Switches eingerichtet", len(entities))
        
        # Final state check for key switches
        if coordinator.data:
            for entity in entities:
                key = entity.entity_description.key
                if key in ["PUMP", "SOLAR", "HEATER"] and key in coordinator.data:
                    raw_state = coordinator.data[key]
                    should_be_on = entity._get_switch_state()
                    _LOGGER.info("🎯 %s Switch: raw=%s → display=%s", key, raw_state, "ON" if should_be_on else "OFF")
    else:
        _LOGGER.warning("❌ Keine Switches eingerichtet")