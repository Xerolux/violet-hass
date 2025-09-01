import logging
import asyncio
from typing import Any, Dict, List, Set, Optional, Union
from datetime import datetime, timedelta
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import entity_registry, device_registry
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
import homeassistant.helpers.config_validation as cv
from homeassistant.const import ATTR_DEVICE_ID, ATTR_ENTITY_ID

from .const import (
    DOMAIN, ACTION_AUTO, ACTION_ON, ACTION_OFF, ACTION_MAN, ACTION_PUSH, ACTION_COLOR,
    ACTION_ALLON, ACTION_ALLOFF, ACTION_ALLAUTO, ACTION_LOCK, ACTION_UNLOCK,
    DEVICE_PARAMETERS, DEVICE_VALIDATION_RULES, ENHANCED_SERVICES, 
    get_device_state_info, get_device_mode_from_state, is_device_activity_detected,
    build_api_request, validate_device_parameter, VioletState, SWITCH_FUNCTIONS,
    DOSING_FUNCTIONS, COVER_FUNCTIONS, PV_SURPLUS_CONFIG, ERROR_CODES
)
from .api import VioletPoolAPIError
from .device import VioletPoolDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS AND DEVICE MAPPINGS
# ═══════════════════════════════════════════════════════════════════════════════

# Entity ID to Device Key Mapping
ENTITY_DEVICE_MAPPING = {
    "pump": "PUMP",
    "heater": "HEATER", 
    "solar": "SOLAR",
    "light": "LIGHT",
    "ph_plus": "DOS_5_PHP",
    "ph_minus": "DOS_4_PHM", 
    "chlorine": "DOS_1_CL",
    "flocculant": "DOS_6_FLOC",
    "backwash": "BACKWASH",
    "pv_surplus": "PVSURPLUS"
}

# Dosing Type Mapping
DOSING_TYPE_MAPPING = {
    "pH-": "DOS_4_PHM",
    "pH+": "DOS_5_PHP",
    "Chlor": "DOS_1_CL", 
    "Flockmittel": "DOS_6_FLOC"
}

# Temperature Profiles
TEMPERATURE_PROFILES = {
    "eco_profile": 26.0,
    "comfort_profile": 28.0,
    "party_profile": 30.0,
    "night_profile": 24.0
}

# Chemical Target Profiles
CHEMICAL_PROFILES = {
    "optimal": {"pH": 7.2, "orp": 700, "chlorine": 1.0},
    "sensitive_skin": {"pH": 7.1, "orp": 680, "chlorine": 0.6},
    "high_usage": {"pH": 7.3, "orp": 750, "chlorine": 1.5},
    "minimal_chemicals": {"pH": 7.2, "orp": 650, "chlorine": 0.4}
}

# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE SCHEMAS - COMPLETE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Enhanced Services with 3-State Support
ENHANCED_SERVICE_SCHEMAS = {
    # 1. Advanced Switch Control with 3-State Support
    "set_device_mode": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("mode"): vol.In(["auto", "manual_on", "manual_off", "force_off"]),
        vol.Optional("duration", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=86400)),
        vol.Optional("speed", default=2): vol.All(vol.Coerce(int), vol.Range(min=1, max=3)),
        vol.Optional("restore_after", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=86400)),
    }),
    
    # 2. Intelligent Pump Control with Speed Management
    "control_pump_advanced": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("action"): vol.In(["speed_control", "force_off", "eco_mode", "boost_mode", "auto_schedule"]),
        vol.Optional("speed", default=2): vol.All(vol.Coerce(int), vol.Range(min=1, max=3)),
        vol.Optional("duration", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=86400)),
        vol.Optional("force_off_duration", default=600): vol.All(vol.Coerce(int), vol.Range(min=60, max=3600)),
    }),
    
    # 3. Enhanced Dosing Control with Safety Features
    "smart_dosing": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("dosing_type"): vol.In(["pH-", "pH+", "Chlor", "Flockmittel"]),
        vol.Required("action"): vol.In(["manual_dose", "auto_calibrate", "safety_stop", "schedule"]),
        vol.Optional("duration", default=30): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
        vol.Optional("safety_override", default=False): cv.boolean,
        vol.Optional("target_value"): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=10.0)),
    }),
    
    # 4. PV Surplus with Advanced Control
    "manage_pv_surplus": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("mode"): vol.In(["activate", "deactivate", "schedule", "smart_control"]),
        vol.Optional("pump_speed", default=2): vol.All(vol.Coerce(int), vol.Range(min=1, max=3)),
        vol.Optional("priority_override", default=False): cv.boolean,
        vol.Optional("weather_dependent", default=True): cv.boolean,
    }),
    
    # 5. Extension Relay Timer Control
    "control_extension_relay": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("action"): vol.In(["timer_on", "timer_off", "pulse", "schedule"]),
        vol.Optional("duration", default=3600): vol.All(vol.Coerce(int), vol.Range(min=60, max=86400)),
        vol.Optional("pulse_duration", default=1): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
        vol.Optional("repeat_count", default=1): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
    }),
    
    # 6. Digital Input Rule Management  
    "manage_digital_rules": vol.Schema({
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required("rule_key"): vol.In([f"DIRULE_{i}" for i in range(1, 8)]),
        vol.Required("action"): vol.In(["trigger", "lock", "unlock", "schedule", "disable"]),
        vol.Optional("delay", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=3600)),
    }),
    
    # 7. DMX Scene Advanced Control
    "control_dmx_scenes": vol.Schema({
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required("action"): vol.In(["all_on", "all_off", "all_auto", "sequence", "random", "party_mode"]),
        vol.Optional("scene_selection"): vol.All(cv.ensure_list, [vol.In([f"DMX_SCENE{i}" for i in range(1, 13)])]),
        vol.Optional("sequence_delay", default=2): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
    }),
    
    # 8. Temperature Control with Profiles
    "manage_temperature": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("action"): vol.In(["set_target", "eco_profile", "comfort_profile", "party_profile", "night_profile"]),
        vol.Optional("temperature"): vol.All(vol.Coerce(float), vol.Range(min=20.0, max=40.0)),
        vol.Optional("profile_duration", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=86400)),
    }),
    
    # 9. Water Analysis and Testing
    "advanced_water_analysis": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("analysis_type"): vol.In(["quick_test", "full_analysis", "calibration", "trend_analysis"]),
        vol.Optional("include_sensors"): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional("save_results", default=True): cv.boolean,
    }),
    
    # 10. System Maintenance and Diagnostics
    "system_maintenance": vol.Schema({
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required("maintenance_type"): vol.In(["enable", "disable", "diagnostic", "reset_errors", "backup_config"]),
        vol.Optional("diagnostic_level"): vol.In(["basic", "extended", "full"]),
        vol.Optional("reset_scope"): vol.In(["errors_only", "runtime_counters", "all_data"]),
    }),
}

# Legacy Service Schemas (for backward compatibility)
LEGACY_SERVICE_SCHEMAS = {
    "turn_auto": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional("auto_delay", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=86400)),
        vol.Optional("last_value", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=3)),
    }),
    
    "set_pv_surplus": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional("pump_speed", default=2): vol.All(vol.Coerce(int), vol.Range(min=1, max=3)),
        vol.Optional("active", default=True): cv.boolean,
    }),
    
    "manual_dosing": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("duration_seconds"): vol.All(vol.Coerce(int), vol.Range(min=1, max=3600)),
        vol.Optional("dosing_type"): vol.In(["pH-", "pH+", "Chlor", "Flockmittel"]),
    }),
    
    "set_light_color_pulse": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional("pulse_count", default=1): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
        vol.Optional("pulse_interval", default=500): vol.All(vol.Coerce(int), vol.Range(min=100, max=2000)),
    }),
    
    "set_extension_timer": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("duration"): vol.All(vol.Coerce(int), vol.Range(min=60, max=86400)),
        vol.Optional("auto_off", default=True): cv.boolean,
    }),
    
    "force_device_off": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional("lock_duration", default=600): vol.All(vol.Coerce(int), vol.Range(min=60, max=3600)),
        vol.Optional("reason", default="manual"): cv.string,
    }),
}

# Smart Service Schemas (AI-powered pool management)
SMART_SERVICE_SCHEMAS = {
    "smart_pool_optimization": vol.Schema({
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required("optimization_mode"): vol.In(["energy_saving", "water_quality", "balanced", "custom"]),
        vol.Optional("duration_hours", default=24): vol.All(vol.Coerce(int), vol.Range(min=1, max=168)),
        vol.Optional("weather_integration", default=True): cv.boolean,
        vol.Optional("user_preferences", default=dict): vol.Schema({
            vol.Optional("max_energy_usage"): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=100.0)),
            vol.Optional("preferred_temp_range"): vol.All(cv.ensure_list, [vol.All(vol.Coerce(float), vol.Range(min=20.0, max=40.0))]),
            vol.Optional("eco_mode_hours"): vol.All(cv.ensure_list, [vol.All(vol.Coerce(int), vol.Range(min=0, max=23))]),
        }),
    }),
    
    "adaptive_chemical_balancing": vol.Schema({
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required("target_profile"): vol.In(["optimal", "sensitive_skin", "high_usage", "minimal_chemicals"]),
        vol.Optional("adjustment_speed"): vol.In(["conservative", "normal", "aggressive"]),
        vol.Optional("monitoring_duration", default=72): vol.All(vol.Coerce(int), vol.Range(min=6, max=168)),
    }),
    
    "seasonal_pool_preparation": vol.Schema({
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required("season_mode"): vol.In(["spring_startup", "summer_maintenance", "autumn_preparation", "winter_shutdown"]),
        vol.Optional("preparation_steps"): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional("schedule_execution", default=True): cv.boolean,
    }),
}

# Combined schema registry
ALL_SERVICE_SCHEMAS = {
    **ENHANCED_SERVICE_SCHEMAS,
    **LEGACY_SERVICE_SCHEMAS, 
    **SMART_SERVICE_SCHEMAS
}

# ═══════════════════════════════════════════════════════════════════════════════
# VIOLET SERVICE MANAGER - INTELLIGENT POOL CONTROL
# ═══════════════════════════════════════════════════════════════════════════════

class VioletServiceManager:
    """Intelligent service manager for pool control operations."""
    
    def __init__(self, hass: HomeAssistant):
        self.hass = hass
        self._active_schedules: Dict[str, Dict] = {}
        self._safety_locks: Dict[str, datetime] = {}
        self._optimization_profiles: Dict[str, Dict] = {}
        
    async def get_coordinators_for_entities(self, entity_ids: List[str]) -> Set[VioletPoolDataUpdateCoordinator]:
        """Get coordinators for given entity IDs with validation."""
        registry = entity_registry.async_get(self.hass)
        coordinators = set()
        
        for entity_id in entity_ids:
            entity_entry = registry.async_get(entity_id)
            if not entity_entry:
                _LOGGER.warning("Entity not found in registry: %s", entity_id)
                continue
                
            if entity_entry.config_entry_id not in self.hass.data.get(DOMAIN, {}):
                _LOGGER.warning("Config entry not found for entity: %s", entity_id)
                continue
                
            coordinator = self.hass.data[DOMAIN][entity_entry.config_entry_id]
            if isinstance(coordinator, VioletPoolDataUpdateCoordinator):
                coordinators.add(coordinator)
            else:
                _LOGGER.warning("Invalid coordinator type for entity: %s", entity_id)
        
        return coordinators
    
    async def get_coordinator_for_device(self, device_id: str) -> Optional[VioletPoolDataUpdateCoordinator]:
        """Get coordinator for device ID."""
        device_reg = device_registry.async_get(self.hass)
        device_entry = device_reg.async_get(device_id)
        
        if not device_entry:
            _LOGGER.warning("Device not found: %s", device_id)
            return None
            
        for config_entry_id in device_entry.config_entries:
            if config_entry_id in self.hass.data.get(DOMAIN, {}):
                coordinator = self.hass.data[DOMAIN][config_entry_id]
                if isinstance(coordinator, VioletPoolDataUpdateCoordinator):
                    return coordinator
                    
        return None
    
    def extract_device_key_from_entity_id(self, entity_id: str) -> str:
        """Extract device key from entity ID."""
        entity_name = entity_id.split(".")[-1]
        if entity_name.startswith(f"{DOMAIN}_"):
            entity_name = entity_name[len(f"{DOMAIN}_"):]
        
        # Check direct mapping first
        for key, device_key in ENTITY_DEVICE_MAPPING.items():
            if key in entity_name.lower():
                return device_key
        
        # Fallback to uppercase conversion
        return entity_name.upper()
    
    def check_safety_lock(self, device_key: str) -> bool:
        """Check if device has an active safety lock."""
        if device_key in self._safety_locks:
            lock_time = self._safety_locks[device_key]
            if datetime.now() < lock_time:
                return True
            else:
                del self._safety_locks[device_key]
        return False
    
    def set_safety_lock(self, device_key: str, duration_seconds: int) -> None:
        """Set safety lock for device."""
        self._safety_locks[device_key] = datetime.now() + timedelta(seconds=duration_seconds)
        _LOGGER.info("Safety lock set for %s for %d seconds", device_key, duration_seconds)
    
    def get_remaining_safety_time(self, device_key: str) -> int:
        """Get remaining safety lock time in seconds."""
        if device_key in self._safety_locks:
            remaining = (self._safety_locks[device_key] - datetime.now()).total_seconds()
            return max(0, int(remaining))
        return 0
    
    async def validate_dosing_safety(self, coordinator: VioletPoolDataUpdateCoordinator, 
                                   device_key: str, duration: int) -> Dict[str, Any]:
        """Validate dosing operation for safety."""
        if device_key not in DEVICE_PARAMETERS:
            return {"valid": False, "error": "Unknown dosing device"}
        
        device_config = DEVICE_PARAMETERS[device_key]
        safety_interval = device_config.get("safety_interval", 300)
        max_duration = device_config.get("max_dosing_duration", 300)
        
        # Check safety lock
        if self.check_safety_lock(device_key):
            remaining = self.get_remaining_safety_time(device_key)
            return {"valid": False, "error": f"Safety interval active. {remaining}s remaining"}
        
        # Check maximum duration
        if duration > max_duration:
            return {"valid": False, "error": f"Duration {duration}s exceeds maximum {max_duration}s"}
        
        # Check current device state
        current_state = coordinator.data.get(device_key, "")
        state_info = get_device_state_info(current_state, device_key)
        
        if state_info.get("active"):
            return {"valid": False, "error": f"Device {device_key} is already active"}
        
        # Check chemical tank level
        remaining_key = f"{device_key}_REMAINING_RANGE"
        remaining = coordinator.data.get(remaining_key)
        if remaining and str(remaining).lower() in ["empty", "low", "0"]:
            return {"valid": False, "error": f"Chemical tank for {device_key} is empty or low"}
        
        return {"valid": True, "safety_interval": safety_interval}

# ═══════════════════════════════════════════════════════════════════════════════
# ENHANCED SERVICE HANDLERS - 10 SERVICES
# ═══════════════════════════════════════════════════════════════════════════════

class VioletEnhancedServiceHandlers:
    """Enhanced service handlers with 3-state support."""
    
    def __init__(self, service_manager: VioletServiceManager):
        self.manager = service_manager
        self.hass = service_manager.hass
    
    async def handle_set_device_mode(self, call: ServiceCall) -> None:
        """Enhanced device mode control with 3-state support."""
        entity_ids = call.data["entity_id"]
        mode = call.data["mode"]
        duration = call.data.get("duration", 0)
        speed = call.data.get("speed", 2)
        restore_after = call.data.get("restore_after", 0)
        
        coordinators = await self.manager.get_coordinators_for_entities(entity_ids)
        if not coordinators:
            raise HomeAssistantError("No valid coordinators found for entities")
        
        for coordinator in coordinators:
            for entity_id in entity_ids:
                device_key = self.manager.extract_device_key_from_entity_id(entity_id)
                
                if device_key not in SWITCH_FUNCTIONS:
                    _LOGGER.warning("Unknown device key: %s for entity: %s", device_key, entity_id)
                    continue
                
                if self.manager.check_safety_lock(device_key):
                    remaining = self.manager.get_remaining_safety_time(device_key)
                    _LOGGER.warning("Device %s is safety locked (%ds remaining)", device_key, remaining)
                    continue
                
                try:
                    action_map = {
                        "auto": ACTION_AUTO,
                        "manual_on": ACTION_ON,
                        "manual_off": ACTION_OFF,
                        "force_off": ACTION_OFF
                    }
                    
                    action = action_map[mode]
                    
                    # Build API parameters
                    api_params = {"key": device_key, "action": action}
                    if duration > 0:
                        api_params["duration"] = duration
                    if device_key == "PUMP" and action == ACTION_ON and speed:
                        api_params["last_value"] = speed
                    
                    result = await coordinator.device.api.set_switch_state(**api_params)
                    
                    if result.get("success", True):
                        _LOGGER.info("Extension timer %s set for %d seconds", device_key, duration)
                    else:
                        _LOGGER.warning("Extension timer possibly failed: %s", result.get("response", result))
                        
                except VioletPoolAPIError as err:
                    _LOGGER.error("Error with extension timer: %s", err)
                    raise HomeAssistantError(f"Extension timer failed: {err}") from err
            
            await coordinator.async_request_refresh()
    
    async def handle_force_device_off(self, call: ServiceCall) -> None:
        """Legacy force device off service."""
        coordinators = await self.manager.get_coordinators_for_entities(call.data["entity_id"])
        lock_duration = call.data.get("lock_duration", 600)
        reason = call.data.get("reason", "manual")
        
        for coordinator in coordinators:
            for entity_id in call.data["entity_id"]:
                device_key = self.manager.extract_device_key_from_entity_id(entity_id)
                
                try:
                    result = await coordinator.device.api.set_switch_state(
                        key=device_key, action=ACTION_OFF, duration=lock_duration
                    )
                    
                    if result.get("success", True):
                        _LOGGER.info("Device %s forced off for %d seconds (reason: %s)", device_key, lock_duration, reason)
                        self.manager.set_safety_lock(device_key, lock_duration)
                    else:
                        _LOGGER.warning("Force off for %s possibly failed: %s", device_key, result.get("response", result))
                        
                except VioletPoolAPIError as err:
                    _LOGGER.error("Error forcing device off: %s", err)
                    raise HomeAssistantError(f"Force off failed: {err}") from err
            
            await coordinator.async_request_refresh()

# ═══════════════════════════════════════════════════════════════════════════════
# SMART SERVICE HANDLERS - 3 AI-POWERED SERVICES
# ═══════════════════════════════════════════════════════════════════════════════

class VioletSmartServiceHandlers:
    """Smart service handlers with AI-powered pool management."""
    
    def __init__(self, service_manager: VioletServiceManager):
        self.manager = service_manager
        self.hass = service_manager.hass
    
    async def handle_smart_pool_optimization(self, call: ServiceCall) -> None:
        """Smart pool optimization with energy and water quality balancing."""
        device_id = call.data["device_id"]
        optimization_mode = call.data["optimization_mode"]
        duration_hours = call.data.get("duration_hours", 24)
        weather_integration = call.data.get("weather_integration", True)
        user_preferences = call.data.get("user_preferences", {})
        
        coordinator = await self.manager.get_coordinator_for_device(device_id)
        if not coordinator:
            raise HomeAssistantError(f"Device not found: {device_id}")
        
        try:
            optimization_plan = self._generate_optimization_plan(
                coordinator.data, optimization_mode, user_preferences
            )
            
            # Execute optimization steps
            for step in optimization_plan["steps"]:
                device_key = step["device"]
                action = step["action"]
                params = step.get("params", {})
                
                if device_key == "PUMP":
                    result = await coordinator.device.api.set_switch_state(
                        key=device_key, action=action, 
                        duration=params.get("duration", 0),
                        last_value=params.get("speed", 2)
                    )
                elif device_key in ["HEATER", "SOLAR"]:
                    if "temperature" in params:
                        result = await coordinator.device.api.set_device_temperature(
                            device_key, params["temperature"]
                        )
                    else:
                        result = await coordinator.device.api.set_switch_state(
                            key=device_key, action=action
                        )
                elif device_key.startswith("DOS_"):
                    if action == ACTION_MAN:
                        dosing_type = self._get_dosing_type_from_key(device_key)
                        result = await coordinator.device.api.manual_dosing(
                            dosing_type, params.get("duration", 30)
                        )
                    else:
                        result = await coordinator.device.api.set_switch_state(
                            key=device_key, action=action
                        )
                else:
                    result = await coordinator.device.api.set_switch_state(
                        key=device_key, action=action, duration=params.get("duration", 0)
                    )
                
                if not result.get("success", True):
                    _LOGGER.warning("Optimization step failed for %s: %s", device_key, result.get("response", result))
                
                await asyncio.sleep(2)  # Brief delay between steps
            
            _LOGGER.info("Smart pool optimization %s completed", optimization_mode)
            
            await coordinator.async_request_refresh()
        except VioletPoolAPIError as err:
            _LOGGER.error("API error in smart pool optimization: %s", err)
            raise HomeAssistantError(f"Smart pool optimization failed: {err}") from err
    
    def _generate_optimization_plan(self, data: Dict, mode: str, preferences: Dict) -> Dict:
        """Generate optimization plan based on current conditions and mode."""
        plan = {"mode": mode, "steps": []}
        
        if mode == "energy_saving":
            # Energy saving optimization
            plan["steps"] = [
                {"device": "PUMP", "action": ACTION_ON, "params": {"speed": 1, "duration": 14400}},  # 4h eco speed
                {"device": "HEATER", "action": ACTION_AUTO},
                {"device": "SOLAR", "action": ACTION_ON},  # Prioritize solar
            ]
        elif mode == "water_quality":
            # Water quality optimization
            ph_value = data.get("pH_value", 7.2)
            orp_value = data.get("orp_value", 700)
            
            if ph_value < 7.0:
                plan["steps"].append({"device": "DOS_5_PHP", "action": ACTION_MAN, "params": {"duration": 30}})
            elif ph_value > 7.4:
                plan["steps"].append({"device": "DOS_4_PHM", "action": ACTION_MAN, "params": {"duration": 30}})
            
            if orp_value < 650:
                plan["steps"].append({"device": "DOS_1_CL", "action": ACTION_MAN, "params": {"duration": 60}})
            
            plan["steps"].extend([
                {"device": "PUMP", "action": ACTION_ON, "params": {"speed": 3, "duration": 7200}},  # 2h boost
                {"device": "BACKWASH", "action": ACTION_AUTO},
            ])
        elif mode == "balanced":
            # Balanced optimization
            plan["steps"] = [
                {"device": "PUMP", "action": ACTION_ON, "params": {"speed": 2, "duration": 10800}},  # 3h normal
                {"device": "HEATER", "action": ACTION_AUTO},
                {"device": "SOLAR", "action": ACTION_AUTO},
                {"device": "DOS_1_CL", "action": ACTION_AUTO},
                {"device": "DOS_4_PHM", "action": ACTION_AUTO},
                {"device": "DOS_5_PHP", "action": ACTION_AUTO},
            ]
        elif mode == "custom":
            # Custom optimization based on preferences
            max_energy = preferences.get("max_energy_usage", 50.0)
            preferred_temp = preferences.get("preferred_temp_range", [28.0, 30.0])
            
            pump_speed = 1 if max_energy < 30 else 2 if max_energy < 70 else 3
            plan["steps"] = [
                {"device": "PUMP", "action": ACTION_ON, "params": {"speed": pump_speed}},
                {"device": "HEATER", "action": ACTION_AUTO, "params": {"temperature": preferred_temp[0]}},
            ]
        
        return plan
    
    def _get_dosing_type_from_key(self, device_key: str) -> str:
        """Get dosing type from device key."""
        dosing_map = {
            "DOS_1_CL": "Chlor",
            "DOS_4_PHM": "pH-", 
            "DOS_5_PHP": "pH+",
            "DOS_6_FLOC": "Flockmittel"
        }
        return dosing_map.get(device_key, "Chlor")
    
    async def handle_adaptive_chemical_balancing(self, call: ServiceCall) -> None:
        """Adaptive chemical balancing with intelligent adjustments."""
        device_id = call.data["device_id"]
        target_profile = call.data["target_profile"]
        adjustment_speed = call.data.get("adjustment_speed", "normal")
        monitoring_duration = call.data.get("monitoring_duration", 72)
        
        coordinator = await self.manager.get_coordinator_for_device(device_id)
        if not coordinator:
            raise HomeAssistantError(f"Device not found: {device_id}")
        
        try:
            # Get target values from profiles
            target_values = CHEMICAL_PROFILES.get(target_profile, CHEMICAL_PROFILES["optimal"])
            
            # Get current values
            current_ph = coordinator.data.get("pH_value", 7.2)
            current_orp = coordinator.data.get("orp_value", 700)
            current_chlorine = coordinator.data.get("pot_value", 1.0)
            
            # Calculate adjustments
            adjustments = []
            
            ph_diff = target_values["pH"] - current_ph
            if abs(ph_diff) > 0.1:
                if ph_diff > 0:
                    dosing_duration = min(60, abs(ph_diff) * 30)
                    adjustments.append({"device": "DOS_5_PHP", "action": ACTION_MAN, "duration": dosing_duration})
                else:
                    dosing_duration = min(60, abs(ph_diff) * 30)
                    adjustments.append({"device": "DOS_4_PHM", "action": ACTION_MAN, "duration": dosing_duration})
            
            orp_diff = target_values["orp"] - current_orp
            if abs(orp_diff) > 50:
                if orp_diff > 0:
                    dosing_duration = min(120, abs(orp_diff) / 10)
                    adjustments.append({"device": "DOS_1_CL", "action": ACTION_MAN, "duration": dosing_duration})
            
            # Execute adjustments with safety checks
            for adjustment in adjustments:
                device_key = adjustment["device"]
                safety_check = await self.manager.validate_dosing_safety(coordinator, device_key, adjustment["duration"])
                
                if safety_check["valid"]:
                    result = await coordinator.device.api.set_switch_state(
                        key=device_key, action=adjustment["action"], duration=adjustment["duration"]
                    )
                    if result.get("success", True):
                        _LOGGER.info("Chemical adjustment for %s executed", device_key)
                        self.manager.set_safety_lock(device_key, safety_check["safety_interval"])
                    else:
                        _LOGGER.warning("Chemical adjustment failed: %s", result.get("response", result))
                else:
                    _LOGGER.warning("Skipping adjustment for %s: %s", device_key, safety_check["error"])
            
            _LOGGER.info("Adaptive chemical balancing %s completed", target_profile)
            
            await coordinator.async_request_refresh()
        except VioletPoolAPIError as err:
            _LOGGER.error("API error in adaptive chemical balancing: %s", err)
            raise HomeAssistantError(f"Chemical balancing failed: {err}") from err
    
    async def handle_seasonal_pool_preparation(self, call: ServiceCall) -> None:
        """Seasonal pool preparation and maintenance."""
        device_id = call.data["device_id"]
        season_mode = call.data["season_mode"]
        preparation_steps = call.data.get("preparation_steps", [])
        schedule_execution = call.data.get("schedule_execution", True)
        
        coordinator = await self.manager.get_coordinator_for_device(device_id)
        if not coordinator:
            raise HomeAssistantError(f"Device not found: {device_id}")
        
        try:
            # Define seasonal preparation sequences
            seasonal_sequences = {
                "spring_startup": [
                    {"device": "PUMP", "action": ACTION_ON, "params": {"speed": 3, "duration": 7200}},  # 2h full clean
                    {"device": "BACKWASH", "action": ACTION_ON, "params": {"duration": 300}},  # 5min backwash
                    {"device": "DOS_1_CL", "action": ACTION_MAN, "params": {"duration": 120}},  # Initial chlorination
                    {"device": "HEATER", "action": ACTION_AUTO},
                    {"device": "SOLAR", "action": ACTION_AUTO},
                ],
                "summer_maintenance": [
                    {"device": "PUMP", "action": ACTION_ON, "params": {"speed": 2, "duration": 14400}},  # 4h daily
                    {"device": "DOS_1_CL", "action": ACTION_AUTO},
                    {"device": "DOS_4_PHM", "action": ACTION_AUTO},
                    {"device": "DOS_5_PHP", "action": ACTION_AUTO},
                    {"device": "SOLAR", "action": ACTION_ON},
                ],
                "autumn_preparation": [
                    {"device": "PUMP", "action": ACTION_ON, "params": {"speed": 1, "duration": 10800}},  # 3h reduced
                    {"device": "HEATER", "action": ACTION_AUTO},
                    {"device": "SOLAR", "action": ACTION_OFF},
                    {"device": "DOS_6_FLOC", "action": ACTION_MAN, "params": {"duration": 180}},  # Flocculation
                ],
                "winter_shutdown": [
                    {"device": "PUMP", "action": ACTION_OFF, "params": {"duration": 86400}},  # 24h off
                    {"device": "HEATER", "action": ACTION_OFF, "params": {"duration": 86400}},
                    {"device": "SOLAR", "action": ACTION_OFF, "params": {"duration": 86400}},
                    {"device": "DOS_1_CL", "action": ACTION_OFF, "params": {"duration": 86400}},
                    {"device": "DOS_4_PHM", "action": ACTION_OFF, "params": {"duration": 86400}},
                    {"device": "DOS_5_PHP", "action": ACTION_OFF, "params": {"duration": 86400}},
                ]
            }
            
            sequence = seasonal_sequences.get(season_mode, [])
            
            if schedule_execution:
                # Execute sequence immediately
                for step in sequence:
                    device_key = step["device"]
                    action = step["action"]
                    params = step.get("params", {})
                    
                    if device_key in coordinator.data:
                        result = await coordinator.device.api.set_switch_state(
                            key=device_key, action=action,
                            duration=params.get("duration", 0),
                            last_value=params.get("speed", 0)
                        )
                        
                        if result.get("success", True):
                            _LOGGER.info("Seasonal step executed: %s %s", device_key, action)
                        else:
                            _LOGGER.warning("Seasonal step failed: %s", result.get("response", result))
                    
                    await asyncio.sleep(5)  # Delay between steps
            
            _LOGGER.info("Seasonal pool preparation %s completed", season_mode)
            
            await coordinator.async_request_refresh()
        except VioletPoolAPIError as err:
            _LOGGER.error("API error in seasonal preparation: %s", err)
            raise HomeAssistantError(f"Seasonal preparation failed: {err}") from err

# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE REGISTRATION FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

async def async_register_enhanced_services(hass: HomeAssistant) -> None:
    """Register all enhanced services for Violet Pool Controller."""
    if hass.services.has_service(DOMAIN, "set_device_mode"):
        _LOGGER.debug("Enhanced services already registered")
        return
    
    try:
        # Initialize service manager and handlers
        service_manager = VioletServiceManager(hass)
        enhanced_handlers = VioletEnhancedServiceHandlers(service_manager)
        legacy_handlers = VioletLegacyServiceHandlers(service_manager)
        smart_handlers = VioletSmartServiceHandlers(service_manager)
        
        # Register Enhanced Services (10 services)
        hass.services.async_register(
            DOMAIN, "set_device_mode", enhanced_handlers.handle_set_device_mode,
            schema=ENHANCED_SERVICE_SCHEMAS["set_device_mode"]
        )
        
        hass.services.async_register(
            DOMAIN, "control_pump_advanced", enhanced_handlers.handle_control_pump_advanced,
            schema=ENHANCED_SERVICE_SCHEMAS["control_pump_advanced"]
        )
        
        hass.services.async_register(
            DOMAIN, "smart_dosing", enhanced_handlers.handle_smart_dosing,
            schema=ENHANCED_SERVICE_SCHEMAS["smart_dosing"]
        )
        
        hass.services.async_register(
            DOMAIN, "manage_pv_surplus", enhanced_handlers.handle_manage_pv_surplus,
            schema=ENHANCED_SERVICE_SCHEMAS["manage_pv_surplus"]
        )
        
        hass.services.async_register(
            DOMAIN, "control_extension_relay", enhanced_handlers.handle_control_extension_relay,
            schema=ENHANCED_SERVICE_SCHEMAS["control_extension_relay"]
        )
        
        hass.services.async_register(
            DOMAIN, "manage_digital_rules", enhanced_handlers.handle_manage_digital_rules,
            schema=ENHANCED_SERVICE_SCHEMAS["manage_digital_rules"]
        )
        
        hass.services.async_register(
            DOMAIN, "control_dmx_scenes", enhanced_handlers.handle_control_dmx_scenes,
            schema=ENHANCED_SERVICE_SCHEMAS["control_dmx_scenes"]
        )
        
        hass.services.async_register(
            DOMAIN, "manage_temperature", enhanced_handlers.handle_manage_temperature,
            schema=ENHANCED_SERVICE_SCHEMAS["manage_temperature"]
        )
        
        hass.services.async_register(
            DOMAIN, "advanced_water_analysis", enhanced_handlers.handle_advanced_water_analysis,
            schema=ENHANCED_SERVICE_SCHEMAS["advanced_water_analysis"]
        )
        
        hass.services.async_register(
            DOMAIN, "system_maintenance", enhanced_handlers.handle_system_maintenance,
            schema=ENHANCED_SERVICE_SCHEMAS["system_maintenance"]
        )
        
        # Register Legacy Services (6 services)
        hass.services.async_register(
            DOMAIN, "turn_auto", legacy_handlers.handle_turn_auto,
            schema=LEGACY_SERVICE_SCHEMAS["turn_auto"]
        )
        
        hass.services.async_register(
            DOMAIN, "set_pv_surplus", legacy_handlers.handle_set_pv_surplus,
            schema=LEGACY_SERVICE_SCHEMAS["set_pv_surplus"]
        )
        
        hass.services.async_register(
            DOMAIN, "manual_dosing", legacy_handlers.handle_manual_dosing,
            schema=LEGACY_SERVICE_SCHEMAS["manual_dosing"]
        )
        
        hass.services.async_register(
            DOMAIN, "set_light_color_pulse", legacy_handlers.handle_set_light_color_pulse,
            schema=LEGACY_SERVICE_SCHEMAS["set_light_color_pulse"]
        )
        
        hass.services.async_register(
            DOMAIN, "set_extension_timer", legacy_handlers.handle_set_extension_timer,
            schema=LEGACY_SERVICE_SCHEMAS["set_extension_timer"]
        )
        
        hass.services.async_register(
            DOMAIN, "force_device_off", legacy_handlers.handle_force_device_off,
            schema=LEGACY_SERVICE_SCHEMAS["force_device_off"]
        )
        
        # Register Smart Services (3 services)
        hass.services.async_register(
            DOMAIN, "smart_pool_optimization", smart_handlers.handle_smart_pool_optimization,
            schema=SMART_SERVICE_SCHEMAS["smart_pool_optimization"]
        )
        
        hass.services.async_register(
            DOMAIN, "adaptive_chemical_balancing", smart_handlers.handle_adaptive_chemical_balancing,
            schema=SMART_SERVICE_SCHEMAS["adaptive_chemical_balancing"]
        )
        
        hass.services.async_register(
            DOMAIN, "seasonal_pool_preparation", smart_handlers.handle_seasonal_pool_preparation,
            schema=SMART_SERVICE_SCHEMAS["seasonal_pool_preparation"]
        )
        
        _LOGGER.info("Enhanced services registered successfully: %d enhanced + %d legacy + %d smart services", 
                    len(ENHANCED_SERVICE_SCHEMAS), len(LEGACY_SERVICE_SCHEMAS), len(SMART_SERVICE_SCHEMAS))
        
    except Exception as err:
        _LOGGER.error("Failed to register services: %s", err)
        raise HomeAssistantError(f"Service registration failed: {err}") from err

# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE CLEANUP AND UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def async_unregister_services(hass: HomeAssistant) -> None:
    """Unregister all Violet Pool Controller services."""
    services_to_remove = list(ALL_SERVICE_SCHEMAS.keys())
    
    for service_name in services_to_remove:
        if hass.services.has_service(DOMAIN, service_name):
            hass.services.async_remove(DOMAIN, service_name)
            _LOGGER.debug("Service %s unregistered", service_name)
    
    _LOGGER.info("All Violet Pool Controller services unregistered")

def get_service_call_validation_errors(call: ServiceCall, schema: vol.Schema) -> List[str]:
    """Validate service call and return list of errors."""
    errors = []
    
    try:
        schema(call.data)
    except vol.Invalid as err:
        if hasattr(err, 'error_message'):
            errors.append(str(err.error_message))
        else:
            errors.append(str(err))
    except Exception as err:
        errors.append(f"Validation error: {err}")
    
    return errors

def is_service_available(hass: HomeAssistant, service_name: str) -> bool:
    """Check if a specific service is available."""
    return hass.services.has_service(DOMAIN, service_name)

def get_available_services(hass: HomeAssistant) -> Dict[str, List[str]]:
    """Get list of available services grouped by category."""
    available = {"enhanced": [], "legacy": [], "smart": []}
    
    for service_name in ENHANCED_SERVICE_SCHEMAS:
        if hass.services.has_service(DOMAIN, service_name):
            available["enhanced"].append(service_name)
    
    for service_name in LEGACY_SERVICE_SCHEMAS:
        if hass.services.has_service(DOMAIN, service_name):
            available["legacy"].append(service_name)
    
    for service_name in SMART_SERVICE_SCHEMAS:
        if hass.services.has_service(DOMAIN, service_name):
            available["smart"].append(service_name)
    
    return available

# ═══════════════════════════════════════════════════════════════════════════════
# ERROR HANDLING AND LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

def log_service_execution(service_name: str, entity_ids: List[str], parameters: Dict[str, Any]) -> None:
    """Log service execution for debugging."""
    _LOGGER.debug(
        "Executing service %s for entities %s with parameters: %s",
        service_name,
        ', '.join(entity_ids),
        {k: v for k, v in parameters.items() if k not in ['entity_id']}
    )

def handle_service_error(service_name: str, error: Exception, entity_id: str = None) -> None:
    """Handle and log service errors uniformly."""
    error_msg = f"Service {service_name} failed"
    if entity_id:
        error_msg += f" for entity {entity_id}"
    error_msg += f": {error}"
    
    if isinstance(error, VioletPoolAPIError):
        _LOGGER.error("%s (API Error)", error_msg)
    elif isinstance(error, HomeAssistantError):
        _LOGGER.error("%s (HA Error)", error_msg)
    else:
        _LOGGER.error("%s (Unexpected Error)", error_msg)

# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE DOCUMENTATION AND METADATA
# ═══════════════════════════════════════════════════════════════════════════════

SERVICE_DESCRIPTIONS = {
    # Enhanced Services
    "set_device_mode": "Advanced device mode control with 3-state support (auto, manual_on, manual_off, force_off)",
    "control_pump_advanced": "Intelligent pump control with speed management and eco/boost modes",
    "smart_dosing": "Enhanced dosing control with safety features and auto-calibration",
    "manage_pv_surplus": "Advanced PV surplus management with weather integration",
    "control_extension_relay": "Extension relay timer control with pulse and scheduling features",
    "manage_digital_rules": "Digital input rule management with scheduling and locking",
    "control_dmx_scenes": "Advanced DMX scene control with sequences and party modes",
    "manage_temperature": "Temperature control with comfort profiles and scheduling",
    "advanced_water_analysis": "Comprehensive water analysis with trend monitoring",
    "system_maintenance": "System maintenance, diagnostics, and configuration backup",
    
    # Legacy Services
    "turn_auto": "Turn device to AUTO mode (legacy compatibility)",
    "set_pv_surplus": "Set PV surplus mode (legacy compatibility)",
    "manual_dosing": "Manual chemical dosing (legacy compatibility)",
    "set_light_color_pulse": "Light color pulse control (legacy compatibility)",
    "set_extension_timer": "Extension relay timer (legacy compatibility)",
    "force_device_off": "Force device off with safety lock (legacy compatibility)",
    
    # Smart Services
    "smart_pool_optimization": "AI-powered pool optimization for energy and water quality",
    "adaptive_chemical_balancing": "Adaptive chemical balancing with intelligent adjustments",
    "seasonal_pool_preparation": "Seasonal pool preparation and maintenance automation"
}

def get_service_info(service_name: str) -> Dict[str, Any]:
    """Get comprehensive information about a service."""
    if service_name not in ALL_SERVICE_SCHEMAS:
        return {"error": f"Service {service_name} not found"}
    
    schema = ALL_SERVICE_SCHEMAS[service_name]
    description = SERVICE_DESCRIPTIONS.get(service_name, "No description available")
    
    # Determine category
    category = "unknown"
    if service_name in ENHANCED_SERVICE_SCHEMAS:
        category = "enhanced"
    elif service_name in LEGACY_SERVICE_SCHEMAS:
        category = "legacy"
    elif service_name in SMART_SERVICE_SCHEMAS:
        category = "smart"
    
    # Extract required and optional fields from schema
    required_fields = []
    optional_fields = []
    
    if hasattr(schema, 'schema'):
        for field, validator in schema.schema.items():
            field_name = str(field).replace('Required(', '').replace('Optional(', '').replace(')', '').strip("'\"")
            if 'Required(' in str(field):
                required_fields.append(field_name)
            else:
                optional_fields.append(field_name)
    
    return {
        "name": service_name,
        "description": description,
        "category": category,
        "required_fields": required_fields,
        "optional_fields": optional_fields,
        "schema": schema
    }

# ═══════════════════════════════════════════════════════════════════════════════
# PERFORMANCE MONITORING
# ═══════════════════════════════════════════════════════════════════════════════

class ServicePerformanceMonitor:
    """Monitor service performance and execution times."""
    
    def __init__(self):
        self._execution_times: Dict[str, List[float]] = {}
        self._error_counts: Dict[str, int] = {}
        self._success_counts: Dict[str, int] = {}
    
    def record_execution(self, service_name: str, execution_time: float, success: bool = True) -> None:
        """Record service execution time and result."""
        if service_name not in self._execution_times:
            self._execution_times[service_name] = []
        
        self._execution_times[service_name].append(execution_time)
        
        # Keep only last 100 executions
        if len(self._execution_times[service_name]) > 100:
            self._execution_times[service_name] = self._execution_times[service_name][-100:]
        
        if success:
            self._success_counts[service_name] = self._success_counts.get(service_name, 0) + 1
        else:
            self._error_counts[service_name] = self._error_counts.get(service_name, 0) + 1
    
    def get_performance_stats(self, service_name: str = None) -> Dict[str, Any]:
        """Get performance statistics for service(s)."""
        if service_name:
            if service_name not in self._execution_times:
                return {"error": f"No data for service {service_name}"}
            
            times = self._execution_times[service_name]
            return {
                "service": service_name,
                "avg_execution_time": sum(times) / len(times) if times else 0,
                "min_execution_time": min(times) if times else 0,
                "max_execution_time": max(times) if times else 0,
                "total_executions": len(times),
                "success_count": self._success_counts.get(service_name, 0),
                "error_count": self._error_counts.get(service_name, 0)
            }
        else:
            # Return stats for all services
            for svc_name in self._execution_times.keys():
                all_stats[svc_name] = self.get_performance_stats(svc_name)
            return all_stats

# Global performance monitor instance
_performance_monitor = ServicePerformanceMonitor()

# ═══════════════════════════════════════════════════════════════════════════════
# FINAL EXPORTS AND MODULE COMPLETION
# ═══════════════════════════════════════════════════════════════════════════════

# Export all public classes, functions and constants
__all__ = [
    # Core Classes
    "VioletServiceManager",
    "VioletEnhancedServiceHandlers",
    "VioletLegacyServiceHandlers", 
    "VioletSmartServiceHandlers",
    "ServicePerformanceMonitor",
    
    # Registration Functions
    "async_register_enhanced_services",
    "async_unregister_services",
    
    # Schema Collections
    "ALL_SERVICE_SCHEMAS",
    "ENHANCED_SERVICE_SCHEMAS",
    "LEGACY_SERVICE_SCHEMAS",
    "SMART_SERVICE_SCHEMAS",
    
    # Utility Functions
    "get_service_call_validation_errors",
    "is_service_available",
    "get_available_services",
    "get_service_info",
    "log_service_execution",
    "handle_service_error",
    
    # Constants
    "SERVICE_DESCRIPTIONS",
    "ENTITY_DEVICE_MAPPING",
    "DOSING_TYPE_MAPPING",
    "TEMPERATURE_PROFILES",
    "CHEMICAL_PROFILES"
]

# Module completion log
_LOGGER.info("Violet Pool Controller Services module loaded successfully - %d total services available", len(ALL_SERVICE_SCHEMAS))LOGGER.info("Device %s set to mode %s", device_key, mode)
                        
                        # Set safety lock for force_off
                        if mode == "force_off":
                            self.manager.set_safety_lock(device_key, duration or 600)
                        
                        # Schedule restoration if requested
                        if restore_after > 0:
                            self.hass.async_create_task(
                                self._schedule_mode_restoration(coordinator, device_key, restore_after)
                            )
                    else:
                        error_msg = result.get("response", result)
                        _LOGGER.error("Failed to set device %s to mode %s: %s", device_key, mode, error_msg)
                        
                except VioletPoolAPIError as err:
                    _LOGGER.error("API error setting device mode for %s: %s", device_key, err)
                    raise HomeAssistantError(f"Device mode change failed: {err}") from err
                except Exception as err:
                    _LOGGER.error("Unexpected error setting device mode for %s: %s", device_key, err)
                    raise HomeAssistantError(f"Device mode change failed: {err}") from err
            
            await coordinator.async_request_refresh()
    
    async def _schedule_mode_restoration(self, coordinator: VioletPoolDataUpdateCoordinator, 
                                       device_key: str, delay_seconds: int) -> None:
        """Schedule automatic mode restoration."""
        await asyncio.sleep(delay_seconds)
        try:
            result = await coordinator.device.api.set_switch_state(
                key=device_key, action=ACTION_AUTO
            )
            if result.get("success", True):
                _LOGGER.info("Restored device %s to AUTO mode after %d seconds", device_key, delay_seconds)
            await coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error restoring device %s to AUTO: %s", device_key, err)
    
    async def handle_control_pump_advanced(self, call: ServiceCall) -> None:
        """Advanced pump control with speed management."""
        coordinators = await self.manager.get_coordinators_for_entities(call.data["entity_id"])
        action = call.data["action"]
        speed = call.data.get("speed", 2)
        duration = call.data.get("duration", 0)
        force_off_duration = call.data.get("force_off_duration", 600)
        
        for coordinator in coordinators:
            for entity_id in call.data["entity_id"]:
                device_key = self.manager.extract_device_key_from_entity_id(entity_id)
                
                if device_key != "PUMP":
                    _LOGGER.warning("Entity %s is not a pump device", entity_id)
                    continue
                
                try:
                    if action == "speed_control":
                        result = await coordinator.device.api.set_switch_state(
                            key="PUMP", action=ACTION_ON, duration=duration, last_value=speed
                        )
                    elif action == "force_off":
                        result = await coordinator.device.api.set_switch_state(
                            key="PUMP", action=ACTION_OFF, duration=force_off_duration
                        )
                        self.manager.set_safety_lock("PUMP", force_off_duration)
                    elif action == "eco_mode":
                        result = await coordinator.device.api.set_switch_state(
                            key="PUMP", action=ACTION_ON, duration=duration, last_value=1
                        )
                    elif action == "boost_mode":
                        result = await coordinator.device.api.set_switch_state(
                            key="PUMP", action=ACTION_ON, duration=duration or 3600, last_value=3
                        )
                    elif action == "auto_schedule":
                        result = await coordinator.device.api.set_switch_state(
                            key="PUMP", action=ACTION_AUTO
                        )
                    
                    if result.get("success", True):
                        _LOGGER.info("Pump action %s executed successfully", action)
                    else:
                        _LOGGER.error("Pump action %s failed: %s", action, result.get("response", result))
                        
                except VioletPoolAPIError as err:
                    _LOGGER.error("API error in pump control: %s", err)
                    raise HomeAssistantError(f"Pump control failed: {err}") from err
            
            await coordinator.async_request_refresh()
    
    async def handle_smart_dosing(self, call: ServiceCall) -> None:
        """Smart dosing control with safety features."""
        coordinators = await self.manager.get_coordinators_for_entities(call.data["entity_id"])
        dosing_type = call.data["dosing_type"]
        action = call.data["action"]
        duration = call.data.get("duration", 30)
        safety_override = call.data.get("safety_override", False)
        target_value = call.data.get("target_value")
        
        device_key = DOSING_TYPE_MAPPING.get(dosing_type)
        
        if not device_key:
            raise HomeAssistantError(f"Unknown dosing type: {dosing_type}")
        
        for coordinator in coordinators:
            try:
                if not safety_override:
                    safety_check = await self.manager.validate_dosing_safety(coordinator, device_key, duration)
                    if not safety_check["valid"]:
                        _LOGGER.error("Dosing safety check failed: %s", safety_check["error"])
                        raise HomeAssistantError(f"Dosing safety check failed: {safety_check['error']}")
                
                if action == "manual_dose":
                    result = await coordinator.device.api.set_switch_state(
                        key=device_key, action=ACTION_MAN, duration=duration
                    )
                    if not safety_override and "safety_interval" in safety_check:
                        self.manager.set_safety_lock(device_key, safety_check["safety_interval"])
                        
                elif action == "auto_calibrate":
                    result = await coordinator.device.api.set_switch_state(
                        key=device_key, action=ACTION_AUTO
                    )
                    
                elif action == "safety_stop":
                    result = await coordinator.device.api.set_switch_state(
                        key=device_key, action=ACTION_OFF
                    )
                    
                elif action == "schedule":
                    result = await coordinator.device.api.set_switch_state(
                        key=device_key, action=ACTION_AUTO
                    )
                
                if result.get("success", True):
                    _LOGGER.info("Smart dosing %s action %s executed", dosing_type, action)
                else:
                    _LOGGER.error("Smart dosing failed: %s", result.get("response", result))
                    
                await coordinator.async_request_refresh()
            except VioletPoolAPIError as err:
                _LOGGER.error("API error in smart dosing: %s", err)
                raise HomeAssistantError(f"Smart dosing failed: {err}") from err
    
    async def handle_manage_pv_surplus(self, call: ServiceCall) -> None:
        """Advanced PV surplus management."""
        coordinators = await self.manager.get_coordinators_for_entities(call.data["entity_id"])
        mode = call.data["mode"]
        pump_speed = call.data.get("pump_speed", 2)
        priority_override = call.data.get("priority_override", False)
        weather_dependent = call.data.get("weather_dependent", True)
        
        for coordinator in coordinators:
            try:
                if mode == "activate":
                    result = await coordinator.device.api.set_pv_surplus(
                        active=True, pump_speed=pump_speed
                    )
                elif mode == "deactivate":
                    result = await coordinator.device.api.set_pv_surplus(active=False)
                elif mode == "smart_control":
                    current_pump_state = coordinator.data.get("PUMP", "")
                    pump_state_info = get_device_state_info(current_pump_state, "PUMP")
                    
                    if pump_state_info.get("mode") == "auto":
                        result = await coordinator.device.api.set_pv_surplus(
                            active=True, pump_speed=pump_speed
                        )
                    else:
                        result = {"success": True, "response": "PV surplus not activated - pump not in auto mode"}
                elif mode == "schedule":
                    result = await coordinator.device.api.set_switch_state(
                        key="PVSURPLUS", action=ACTION_AUTO
                    )
                
                if result.get("success", True):
                    _LOGGER.info("PV surplus mode %s executed", mode)
                else:
                    _LOGGER.error("PV surplus management failed: %s", result.get("response", result))
                    
                await coordinator.async_request_refresh()
            except VioletPoolAPIError as err:
                _LOGGER.error("API error in PV surplus management: %s", err)
                raise HomeAssistantError(f"PV surplus management failed: {err}") from err
    
    async def handle_control_extension_relay(self, call: ServiceCall) -> None:
        """Control extension relays with timer functionality."""
        coordinators = await self.manager.get_coordinators_for_entities(call.data["entity_id"])
        action = call.data["action"]
        duration = call.data.get("duration", 3600)
        pulse_duration = call.data.get("pulse_duration", 1)
        repeat_count = call.data.get("repeat_count", 1)
        
        for coordinator in coordinators:
            for entity_id in call.data["entity_id"]:
                device_key = self.manager.extract_device_key_from_entity_id(entity_id)
                
                if not (device_key.startswith("EXT1_") or device_key.startswith("EXT2_") or device_key.startswith("OMNI_DC")):
                    _LOGGER.warning("Entity %s is not an extension relay", entity_id)
                    continue
                
                try:
                    if action == "timer_on":
                        result = await coordinator.device.api.set_switch_state(
                            key=device_key, action=ACTION_ON, duration=duration
                        )
                    elif action == "timer_off":
                        result = await coordinator.device.api.set_switch_state(
                            key=device_key, action=ACTION_OFF, duration=duration
                        )
                    elif action == "pulse":
                        for i in range(repeat_count):
                            await coordinator.device.api.set_switch_state(
                                key=device_key, action=ACTION_ON, duration=pulse_duration
                            )
                            await asyncio.sleep(pulse_duration + 1)
                            await coordinator.device.api.set_switch_state(
                                key=device_key, action=ACTION_OFF, duration=pulse_duration
                            )
                            if i < repeat_count - 1:
                                await asyncio.sleep(pulse_duration + 1)
                        result = {"success": True, "response": f"Pulse sequence completed {repeat_count} times"}
                    elif action == "schedule":
                        result = await coordinator.device.api.set_switch_state(
                            key=device_key, action=ACTION_AUTO
                        )
                    
                    if result.get("success", True):
                        _LOGGER.info("Extension relay %s action %s executed", device_key, action)
                    else:
                        _LOGGER.error("Extension relay control failed: %s", result.get("response", result))
                        
                except VioletPoolAPIError as err:
                    _LOGGER.error("API error in extension relay control: %s", err)
                    raise HomeAssistantError(f"Extension relay control failed: {err}") from err
            
            await coordinator.async_request_refresh()
    
    async def handle_manage_digital_rules(self, call: ServiceCall) -> None:
        """Manage digital input rules."""
        device_id = call.data["device_id"]
        rule_key = call.data["rule_key"]
        action = call.data["action"]
        delay = call.data.get("delay", 0)
        
        coordinator = await self.manager.get_coordinator_for_device(device_id)
        if not coordinator:
            raise HomeAssistantError(f"Device not found: {device_id}")
        
        try:
            if action == "trigger":
                result = await coordinator.device.api.trigger_digital_input_rule(rule_key)
            elif action == "lock":
                result = await coordinator.device.api.set_digital_input_rule_lock(rule_key, True)
            elif action == "unlock":
                result = await coordinator.device.api.set_digital_input_rule_lock(rule_key, False)
            elif action == "schedule":
                if delay > 0:
                    self.hass.async_create_task(self._delayed_rule_trigger(coordinator, rule_key, delay))
                    result = {"success": True, "response": f"Rule {rule_key} scheduled for {delay}s"}
                else:
                    result = await coordinator.device.api.trigger_digital_input_rule(rule_key)
            elif action == "disable":
                result = await coordinator.device.api.set_digital_input_rule_lock(rule_key, True)
            
            if result.get("success", True):
                _LOGGER.info("Digital rule %s action %s executed", rule_key, action)
            else:
                _LOGGER.error("Digital rule management failed: %s", result.get("response", result))
                
            await coordinator.async_request_refresh()
        except VioletPoolAPIError as err:
            _LOGGER.error("API error in digital rule management: %s", err)
            raise HomeAssistantError(f"Digital rule management failed: {err}") from err
    
    async def _delayed_rule_trigger(self, coordinator: VioletPoolDataUpdateCoordinator, 
                                  rule_key: str, delay_seconds: int) -> None:
        """Execute delayed digital rule trigger."""
        await asyncio.sleep(delay_seconds)
        try:
            result = await coordinator.device.api.trigger_digital_input_rule(rule_key)
            if result.get("success", True):
                _LOGGER.info("Delayed trigger executed for rule %s", rule_key)
            await coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error in delayed rule trigger for %s: %s", rule_key, err)
    
    async def handle_control_dmx_scenes(self, call: ServiceCall) -> None:
        """Advanced DMX scene control."""
        device_id = call.data["device_id"]
        action = call.data["action"]
        scene_selection = call.data.get("scene_selection", [])
        sequence_delay = call.data.get("sequence_delay", 2)
        
        coordinator = await self.manager.get_coordinator_for_device(device_id)
        if not coordinator:
            raise HomeAssistantError(f"Device not found: {device_id}")
        
        try:
            if action == "all_on":
                result = await coordinator.device.api.set_all_dmx_scenes(ACTION_ALLON)
            elif action == "all_off":
                result = await coordinator.device.api.set_all_dmx_scenes(ACTION_ALLOFF)
            elif action == "all_auto":
                result = await coordinator.device.api.set_all_dmx_scenes(ACTION_ALLAUTO)
            elif action == "sequence":
                if not scene_selection:
                    scene_selection = [f"DMX_SCENE{i}" for i in range(1, 13)]
                
                for scene in scene_selection:
                    await coordinator.device.api.set_switch_state(scene, ACTION_ON)
                    await asyncio.sleep(sequence_delay)
                    await coordinator.device.api.set_switch_state(scene, ACTION_OFF)
                    
                result = {"success": True, "response": f"Scene sequence completed with {len(scene_selection)} scenes"}
            elif action == "random":
                import random
                all_scenes = [f"DMX_SCENE{i}" for i in range(1, 13)]
                random_scenes = random.sample(all_scenes, min(5, len(all_scenes)))
                
                for scene in random_scenes:
                    await coordinator.device.api.set_switch_state(scene, ACTION_ON)
                    
                result = {"success": True, "response": f"Random scenes activated: {', '.join(random_scenes)}"}
            elif action == "party_mode":
                await coordinator.device.api.set_all_dmx_scenes(ACTION_ALLON)
                await coordinator.device.api.set_light_color_pulse()
                result = {"success": True, "response": "Party mode activated"}
            
            if result.get("success", True):
                _LOGGER.info("DMX scene action %s executed", action)
            else:
                _LOGGER.error("DMX scene control failed: %s", result.get("response", result))
                
            await coordinator.async_request_refresh()
        except VioletPoolAPIError as err:
            _LOGGER.error("API error in DMX scene control: %s", err)
            raise HomeAssistantError(f"DMX scene control failed: {err}") from err
    
    async def handle_manage_temperature(self, call: ServiceCall) -> None:
        """Temperature management with profiles."""
        coordinators = await self.manager.get_coordinators_for_entities(call.data["entity_id"])
        action = call.data["action"]
        temperature = call.data.get("temperature")
        profile_duration = call.data.get("profile_duration", 0)
        
        for coordinator in coordinators:
            for entity_id in call.data["entity_id"]:
                device_key = self.manager.extract_device_key_from_entity_id(entity_id)
                
                if device_key not in ["HEATER", "SOLAR"]:
                    _LOGGER.warning("Entity %s is not a temperature control device", entity_id)
                    continue
                
                try:
                    if action == "set_target" and temperature:
                        result = await coordinator.device.api.set_device_temperature(device_key, temperature)
                    elif action in TEMPERATURE_PROFILES:
                        profile_temp = TEMPERATURE_PROFILES[action]
                        result = await coordinator.device.api.set_device_temperature(device_key, profile_temp)
                        
                        if profile_duration > 0:
                            original_temp = coordinator.data.get(f"{device_key}_TARGET_TEMP", 28.0)
                            self.hass.async_create_task(
                                self._restore_temperature_profile(coordinator, device_key, original_temp, profile_duration)
                            )
                    
                    if result.get("success", True):
                        _LOGGER.info("Temperature management %s executed for %s", action, device_key)
                    else:
                        _LOGGER.error("Temperature management failed: %s", result.get("response", result))
                        
                except VioletPoolAPIError as err:
                    _LOGGER.error("API error in temperature management: %s", err)
                    raise HomeAssistantError(f"Temperature management failed: {err}") from err
            
            await coordinator.async_request_refresh()
    
    async def _restore_temperature_profile(self, coordinator: VioletPoolDataUpdateCoordinator,
                                         device_key: str, original_temp: float, delay_seconds: int) -> None:
        """Restore temperature after profile duration."""
        await asyncio.sleep(delay_seconds)
        try:
            result = await coordinator.device.api.set_device_temperature(device_key, original_temp)
            if result.get("success", True):
                _LOGGER.info("Temperature restored for %s to %.1f°C", device_key, original_temp)
            await coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error restoring temperature for %s: %s", device_key, err)
    
    async def handle_advanced_water_analysis(self, call: ServiceCall) -> None:
        """Advanced water analysis and testing."""
        coordinators = await self.manager.get_coordinators_for_entities(call.data["entity_id"])
        analysis_type = call.data["analysis_type"]
        include_sensors = call.data.get("include_sensors", [])
        save_results = call.data.get("save_results", True)
        
        for coordinator in coordinators:
            try:
                if analysis_type == "quick_test":
                    result = await coordinator.device.api.start_water_analysis()
                elif analysis_type == "full_analysis":
                    result = await coordinator.device.api.start_water_analysis()
                    await coordinator.async_request_refresh()
                elif analysis_type == "calibration":
                    result = await coordinator.device.api.start_water_analysis()
                    await asyncio.sleep(30)
                    await coordinator.async_request_refresh()
                elif analysis_type == "trend_analysis":
                    current_data = coordinator.data
                    analysis_result = self._analyze_water_trends(current_data)
                    result = {"success": True, "response": f"Trend analysis completed: {analysis_result}"}
                
                if result.get("success", True):
                    _LOGGER.info("Water analysis %s completed", analysis_type)
                    
                    if save_results:
                        self._save_analysis_results(coordinator, analysis_type, result)
                else:
                    _LOGGER.error("Water analysis failed: %s", result.get("response", result))
                    
                await coordinator.async_request_refresh()
            except VioletPoolAPIError as err:
                _LOGGER.error("API error in water analysis: %s", err)
                raise HomeAssistantError(f"Water analysis failed: {err}") from err
    
    def _analyze_water_trends(self, current_data: Dict) -> str:
        """Analyze water quality trends."""
        trends = []
        
        ph_value = current_data.get("pH_value")
        if ph_value:
            if ph_value < 7.0:
                trends.append("pH trending acidic")
            elif ph_value > 7.4:
                trends.append("pH trending basic")
            else:
                trends.append("pH stable")
        
        orp_value = current_data.get("orp_value")
        if orp_value:
            if orp_value < 650:
                trends.append("ORP low - increase chlorination")
            elif orp_value > 750:
                trends.append("ORP high - reduce chlorination")
            else:
                trends.append("ORP optimal")
        
        chlorine_value = current_data.get("pot_value")
        if chlorine_value:
            if chlorine_value < 0.5:
                trends.append("Chlorine low")
            elif chlorine_value > 1.5:
                trends.append("Chlorine high")
            else:
                trends.append("Chlorine optimal")
        
        return "; ".join(trends) if trends else "All parameters stable"
    
    def _save_analysis_results(self, coordinator: VioletPoolDataUpdateCoordinator, 
                             analysis_type: str, result: Dict) -> None:
        """Save analysis results for future reference."""
        if not hasattr(coordinator.device, '_analysis_history'):
            coordinator.device._analysis_history = []
        
        analysis_record = {
            "timestamp": datetime.now().isoformat(),
            "type": analysis_type,
            "result": result,
            "water_params": {
                "pH": coordinator.data.get("pH_value"),
                "orp": coordinator.data.get("orp_value"), 
                "chlorine": coordinator.data.get("pot_value"),
                "temperature": coordinator.data.get("onewire1_value")
            }
        }
        
        coordinator.device._analysis_history.append(analysis_record)
        
        if len(coordinator.device._analysis_history) > 50:
            coordinator.device._analysis_history = coordinator.device._analysis_history[-50:]
        
        _LOGGER.debug("Analysis results saved: %s", analysis_type)
    
    async def handle_system_maintenance(self, call: ServiceCall) -> None:
        """System maintenance and diagnostics."""
        device_id = call.data["device_id"]
        maintenance_type = call.data["maintenance_type"]
        diagnostic_level = call.data.get("diagnostic_level", "basic")
        reset_scope = call.data.get("reset_scope", "errors_only")
        
        coordinator = await self.manager.get_coordinator_for_device(device_id)
        if not coordinator:
            raise HomeAssistantError(f"Device not found: {device_id}")
        
        try:
            if maintenance_type == "enable":
                result = await coordinator.device.api.set_maintenance_mode(True)
            elif maintenance_type == "disable":
                result = await coordinator.device.api.set_maintenance_mode(False)
            elif maintenance_type == "diagnostic":
                result = await self._execute_diagnostics(coordinator, diagnostic_level)
            elif maintenance_type == "reset_errors":
                result = await self._reset_device_errors(coordinator, reset_scope)
            elif maintenance_type == "backup_config":
                result = await self._backup_device_config(coordinator)
            
            if result.get("success", True):
                _LOGGER.info("System maintenance %s completed", maintenance_type)
            else:
                _LOGGER.error("System maintenance failed: %s", result.get("response", result))
                
            await coordinator.async_request_refresh()
        except VioletPoolAPIError as err:
            _LOGGER.error("API error in system maintenance: %s", err)
            raise HomeAssistantError(f"System maintenance failed: {err}") from err
    
    async def _execute_diagnostics(self, coordinator: VioletPoolDataUpdateCoordinator, level: str) -> Dict:
        """Execute diagnostic tests."""
        diagnostics = {"success": True, "diagnostics": {}}
        
        if level in ["basic", "extended", "full"]:
            diagnostics["diagnostics"]["sensors"] = self._check_sensor_health(coordinator.data)
        
        if level in ["extended", "full"]:
            diagnostics["diagnostics"]["devices"] = self._check_device_health(coordinator.data)
        
        if level == "full":
            try:
                test_result = await coordinator.device.api.get_readings("ALL")
                diagnostics["diagnostics"]["api_connectivity"] = "OK" if test_result else "FAILED"
            except Exception:
                diagnostics["diagnostics"]["api_connectivity"] = "FAILED"
        
        return diagnostics
    
    def _check_sensor_health(self, data: Dict) -> Dict:
        """Check sensor health status."""
        sensor_health = {}
        
        temp_sensors = ["onewire1_value", "onewire2_value", "onewire3_value", "onewire4_value", "onewire5_value"]
        for sensor in temp_sensors:
            value = data.get(sensor)
            if value is not None:
                try:
                    temp_val = float(value)
                    if -20 <= temp_val <= 60:
                        sensor_health[sensor] = "OK"
                    else:
                        sensor_health[sensor] = f"OUT_OF_RANGE ({temp_val}°C)"
                except (ValueError, TypeError):
                    sensor_health[sensor] = "INVALID_VALUE"
            else:
                sensor_health[sensor] = "NO_DATA"
        
        chem_sensors = {"pH_value": (6.0, 8.5), "orp_value": (400, 1000), "pot_value": (0, 5)}
        for sensor, (min_val, max_val) in chem_sensors.items():
            value = data.get(sensor)
            if value is not None:
                try:
                    chem_val = float(value)
                    if min_val <= chem_val <= max_val:
                        sensor_health[sensor] = "OK"
                    else:
                        sensor_health[sensor] = f"OUT_OF_RANGE ({chem_val})"
                except (ValueError, TypeError):
                    sensor_health[sensor] = "INVALID_VALUE"
            else:
                sensor_health[sensor] = "NO_DATA"
        
        return sensor_health
    
    def _check_device_health(self, data: Dict) -> Dict:
        """Check device operational health."""
        device_health = {}
        
        main_devices = ["PUMP", "HEATER", "SOLAR", "DOS_1_CL", "DOS_4_PHM", "DOS_5_PHP"]
        for device in main_devices:
            state = data.get(device, "")
            state_info = get_device_state_info(state, device)
            
            if state_info.get("mode") == "error":
                device_health[device] = "ERROR"
            elif state_info.get("mode") == "maintenance":
                device_health[device] = "MAINTENANCE"
            else:
                device_health[device] = "OK"
        
        return device_health
    
    async def _reset_device_errors(self, coordinator: VioletPoolDataUpdateCoordinator, scope: str) -> Dict:
        """Reset device error states."""
        reset_actions = []
        
        if scope in ["errors_only", "all_data"]:
            main_devices = ["PUMP", "HEATER", "SOLAR", "DOS_1_CL", "DOS_4_PHM", "DOS_5_PHP"]
            for device in main_devices:
                state = coordinator.data.get(device, "")
                state_info = get_device_state_info(state, device)
                
                if state_info.get("mode") == "error":
                    try:
                        await coordinator.device.api.set_switch_state(device, ACTION_AUTO)
                        reset_actions.append(f"{device} reset to AUTO")
                    except Exception as err:
                        reset_actions.append(f"{device} reset FAILED: {err}")
        
        return {"success": True, "response": f"Reset completed: {'; '.join(reset_actions)}"}
    
    async def _backup_device_config(self, coordinator: VioletPoolDataUpdateCoordinator) -> Dict:
        """Backup device configuration."""
        try:
            config_data = await coordinator.device.api.get_readings("ALL")
            
            if not hasattr(coordinator.device, '_config_backups'):
                coordinator.device._config_backups = []
            
            backup_record = {
                "timestamp": datetime.now().isoformat(),
                "config_data": config_data,
                "active_features": coordinator.device.active_features
            }
            
            coordinator.device._config_backups.append(backup_record)
            
            if len(coordinator.device._config_backups) > 10:
                coordinator.device._config_backups = coordinator.device._config_backups[-10:]
            
            return {"success": True, "response": "Configuration backup created successfully"}
            
        except Exception as err:
            return {"success": False, "response": f"Backup failed: {err}"}

# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY SERVICE HANDLERS - 6 SERVICES
# ═══════════════════════════════════════════════════════════════════════════════

class VioletLegacyServiceHandlers:
    """Legacy service handlers for backward compatibility."""
    
    def __init__(self, service_manager: VioletServiceManager):
        self.manager = service_manager
        self.hass = service_manager.hass
    
    async def handle_turn_auto(self, call: ServiceCall) -> None:
        """Legacy AUTO mode service."""
        entity_ids = call.data["entity_id"]
        auto_delay = call.data.get("auto_delay", 0)
        last_value = call.data.get("last_value", 0)
        
        coordinators = await self.manager.get_coordinators_for_entities(entity_ids)
        if not coordinators:
            raise HomeAssistantError("No valid coordinators found for entities")
        
        for coordinator in coordinators:
            for entity_id in entity_ids:
                device_key = self.manager.extract_device_key_from_entity_id(entity_id)
                
                try:
                    result = await coordinator.device.api.set_switch_state(
                        key=device_key, action=ACTION_AUTO, duration=auto_delay, last_value=last_value
                    )
                    
                    if result.get("success", True):
                        _LOGGER.info("Device %s turned to AUTO mode", device_key)
                    else:
                        _LOGGER.warning("AUTO mode for %s possibly failed: %s", 
                                      device_key, result.get("response", result))
                        
                except VioletPoolAPIError as err:
                    _LOGGER.error("Error turning to AUTO mode: %s", err)
                    raise HomeAssistantError(f"AUTO mode failed: {err}") from err
            
            await coordinator.async_request_refresh()
    
    async def handle_set_pv_surplus(self, call: ServiceCall) -> None:
        """Legacy PV surplus service."""
        coordinators = await self.manager.get_coordinators_for_entities(call.data["entity_id"])
        pump_speed = call.data.get("pump_speed", 2)
        active = call.data.get("active", True)
        
        for coordinator in coordinators:
            try:
                result = await coordinator.device.api.set_pv_surplus(
                    active=active, pump_speed=pump_speed
                )
                
                if result.get("success", True):
                    _LOGGER.info("PV surplus %s with pump speed %d", "activated" if active else "deactivated", pump_speed)
                else:
                    _LOGGER.warning("PV surplus operation possibly failed: %s", result.get("response", result))
                    
            except VioletPoolAPIError as err:
                _LOGGER.error("Error setting PV surplus: %s", err)
                raise HomeAssistantError(f"PV surplus failed: {err}") from err
            
            await coordinator.async_request_refresh()
    
    async def handle_manual_dosing(self, call: ServiceCall) -> None:
        """Legacy manual dosing service."""
        coordinators = await self.manager.get_coordinators_for_entities(call.data["entity_id"])
        duration = call.data["duration_seconds"]
        dosing_type = call.data.get("dosing_type")
        
        for coordinator in coordinators:
            for entity_id in call.data["entity_id"]:
                if not dosing_type:
                    if "cl" in entity_id.lower() or "chlor" in entity_id.lower():
                        dosing_type = "Chlor"
                    elif "ph_minus" in entity_id.lower() or "phm" in entity_id.lower():
                        dosing_type = "pH-"
                    elif "ph_plus" in entity_id.lower() or "php" in entity_id.lower():
                        dosing_type = "pH+"
                    elif "floc" in entity_id.lower():
                        dosing_type = "Flockmittel"
                    else:
                        _LOGGER.warning("Could not determine dosing type for %s", entity_id)
                        continue
                
                try:
                    result = await coordinator.device.api.manual_dosing(dosing_type, duration)
                    
                    if result.get("success", True):
                        _LOGGER.info("Manual dosing %s started for %d seconds", dosing_type, duration)
                    else:
                        _LOGGER.warning("Manual dosing %s possibly failed: %s", 
                                      dosing_type, result.get("response", result))
                        
                except VioletPoolAPIError as err:
                    _LOGGER.error("Error with manual dosing: %s", err)
                    raise HomeAssistantError(f"Manual dosing failed: {err}") from err
            
            await coordinator.async_request_refresh()
    
    async def handle_set_light_color_pulse(self, call: ServiceCall) -> None:
        """Legacy light color pulse service."""
        coordinators = await self.manager.get_coordinators_for_entities(call.data["entity_id"])
        pulse_count = call.data.get("pulse_count", 1)
        pulse_interval = call.data.get("pulse_interval", 500)
        
        for coordinator in coordinators:
            try:
                for i in range(pulse_count):
                    result = await coordinator.device.api.set_light_color_pulse()
                    
                    if not result.get("success", True):
                        _LOGGER.warning("Light color pulse %d failed: %s", i+1, result.get("response", result))
                    
                    if i < pulse_count - 1:
                        await asyncio.sleep(pulse_interval / 1000)
                
                _LOGGER.info("Light color pulse sequence completed (%d pulses)", pulse_count)
                
            except VioletPoolAPIError as err:
                _LOGGER.error("Error with light color pulse: %s", err)
                raise HomeAssistantError(f"Light color pulse failed: {err}") from err
            
            await coordinator.async_request_refresh()
    
    async def handle_set_extension_timer(self, call: ServiceCall) -> None:
        """Legacy extension timer service."""
        coordinators = await self.manager.get_coordinators_for_entities(call.data["entity_id"])
        duration = call.data["duration"]
        auto_off = call.data.get("auto_off", True)
        
        for coordinator in coordinators:
            for entity_id in call.data["entity_id"]:
                device_key = self.manager.extract_device_key_from_entity_id(entity_id)
                
                if not (device_key.startswith("EXT1_") or device_key.startswith("EXT2_") or device_key.startswith("OMNI_DC")):
                    _LOGGER.warning("Entity %s is not an extension relay", entity_id)
                    continue
                
                try:
                    if auto_off:
                        result = await coordinator.device.api.set_switch_state(
                            key=device_key, action=ACTION_ON, duration=duration
                        )
                    else:
                        result = await coordinator.device.api.set_switch_state(
                            key=device_key, action=ACTION_ON
                        )
                    
                    if result.get("success", True):
                    _LOGGER.info("Extension timer %s set for %d seconds", device_key, duration)
                else:
                    _LOGGER.warning("Extension timer possibly failed: %s", result.get("response", result))
                    
            except VioletPoolAPIError as err:
                _LOGGER.error("Error with extension timer: %s", err)
                raise HomeAssistantError(f"Extension timer failed: {err}") from err
        
        await coordinator.async_request_refresh()

async def handle_force_device_off(self, call: ServiceCall) -> None:
    """Legacy force device off service."""
    coordinators = await self.manager.get_coordinators_for_entities(call.data["entity_id"])
    lock_duration = call.data.get("lock_duration", 600)
    reason = call.data.get("reason", "manual")
    
    for coordinator in coordinators:
        for entity_id in call.data["entity_id"]:
            device_key = self.manager.extract_device_key_from_entity_id(entity_id)
            
            try:
                result = await coordinator.device.api.set_switch_state(
                    key=device_key, action=ACTION_OFF, duration=lock_duration
                )
                
                if result.get("success", True):
                    _LOGGER.info("Device %s forced off for %d seconds (reason: %s)", device_key, lock_duration, reason)
                    self.manager.set_safety_lock(device_key, lock_duration)
                else:
                    _LOGGER.warning("Force off for %s possibly failed: %s", device_key, result.get("response", result))
                    
            except VioletPoolAPIError as err:
                _LOGGER.error("Error forcing device off: %s", err)
                raise HomeAssistantError(f"Force off failed: {err}") from err
        
        await coordinator.async_request_refresh()

# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE REGISTRATION FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

async def async_register_enhanced_services(hass: HomeAssistant) -> None:
    """Register all enhanced services for Violet Pool Controller."""
    if hass.services.has_service(DOMAIN, "set_device_mode"):
        _LOGGER.debug("Enhanced services already registered")
        return
    
    try:
        # Initialize service manager and handlers
        service_manager = VioletServiceManager(hass)
        enhanced_handlers = VioletEnhancedServiceHandlers(service_manager)
        legacy_handlers = VioletLegacyServiceHandlers(service_manager)
        smart_handlers = VioletSmartServiceHandlers(service_manager)
        
        # Register Enhanced Services (10 services)
        enhanced_services = [
            "set_device_mode", "control_pump_advanced", "smart_dosing",
            "manage_pv_surplus", "control_extension_relay", "manage_digital_rules",
            "control_dmx_scenes", "manage_temperature", "advanced_water_analysis",
            "system_maintenance"
        ]
        
        for service_name in enhanced_services:
            handler_method = getattr(enhanced_handlers, f"handle_{service_name}")
            hass.services.async_register(
                DOMAIN, service_name, handler_method,
                schema=ENHANCED_SERVICE_SCHEMAS[service_name]
            )
        
        # Register Legacy Services (6 services)
        legacy_services = [
            "turn_auto", "set_pv_surplus", "manual_dosing",
            "set_light_color_pulse", "set_extension_timer", "force_device_off"
        ]
        
        for service_name in legacy_services:
            handler_method = getattr(legacy_handlers, f"handle_{service_name}")
            hass.services.async_register(
                DOMAIN, service_name, handler_method,
                schema=LEGACY_SERVICE_SCHEMAS[service_name]
            )
        
        # Register Smart Services (3 services)
        smart_services = [
            "smart_pool_optimization", "adaptive_chemical_balancing",
            "seasonal_pool_preparation"
        ]
        
        for service_name in smart_services:
            handler_method = getattr(smart_handlers, f"handle_{service_name}")
            hass.services.async_register(
                DOMAIN, service_name, handler_method,
                schema=SMART_SERVICE_SCHEMAS[service_name]
            )
        
        _LOGGER.info("Enhanced services registered successfully: %d enhanced + %d legacy + %d smart services", 
                    len(ENHANCED_SERVICE_SCHEMAS), len(LEGACY_SERVICE_SCHEMAS), len(SMART_SERVICE_SCHEMAS))
        
    except Exception as err:
        _LOGGER.error("Failed to register services: %s", err)
        raise HomeAssistantError(f"Service registration failed: {err}") from err

# ═══════════════════════════════════════════════════════════════════════════════
# SERVICE CLEANUP AND UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def async_unregister_services(hass: HomeAssistant) -> None:
    """Unregister all Violet Pool Controller services."""
    services_to_remove = list(ALL_SERVICE_SCHEMAS.keys())
    
    for service_name in services_to_remove:
        if hass.services.has_service(DOMAIN, service_name):
            hass.services.async_remove(DOMAIN, service_name)
            _LOGGER.debug("Service %s unregistered", service_name)
    
    _LOGGER.info("All Violet Pool Controller services unregistered")

# Export all public classes, functions and constants
__all__ = [
    # Core Classes
    "VioletServiceManager",
    "VioletEnhancedServiceHandlers",
    "VioletLegacyServiceHandlers", 
    "VioletSmartServiceHandlers",
    "ServicePerformanceMonitor",
    
    # Registration Functions
    "async_register_enhanced_services",
    "async_unregister_services",
    
    # Schema Collections
    "ALL_SERVICE_SCHEMAS",
    "ENHANCED_SERVICE_SCHEMAS",
    "LEGACY_SERVICE_SCHEMAS",
    "SMART_SERVICE_SCHEMAS",
]

# Module completion log
_LOGGER.info("Violet Pool Controller Services module loaded successfully - %d total services available", len(ALL_SERVICE_SCHEMAS))
