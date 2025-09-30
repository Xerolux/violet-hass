"""
Violet Pool Controller - Service Utilities
Gemeinsame Funktionen und Konstanten für alle Services
"""
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import ATTR_ENTITY_ID, ATTR_DEVICE_ID
from typing import Dict, Any

from .const import DEVICE_PARAMETERS, get_device_state_info

_LOGGER = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# MAPPINGS
# ═══════════════════════════════════════════════════════════════════════════════

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

DOSING_TYPE_MAPPING = {
    "pH-": "DOS_4_PHM",
    "pH+": "DOS_5_PHP",
    "Chlor": "DOS_1_CL",
    "Flockmittel": "DOS_6_FLOC"
}

# ═══════════════════════════════════════════════════════════════════════════════
# CORE SERVICE SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

CORE_SERVICE_SCHEMAS = {
    "set_device_mode": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("mode"): vol.In(["auto", "manual_on", "manual_off", "force_off"]),
        vol.Optional("duration", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=86400)),
        vol.Optional("speed", default=2): vol.All(vol.Coerce(int), vol.Range(min=1, max=3)),
        vol.Optional("restore_after", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=86400)),
    }),
    
    "control_pump": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("action"): vol.In(["speed_control", "force_off", "eco_mode", "boost_mode", "auto"]),
        vol.Optional("speed", default=2): vol.All(vol.Coerce(int), vol.Range(min=1, max=3)),
        vol.Optional("duration", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=86400)),
    }),
    
    "smart_dosing": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("dosing_type"): vol.In(["pH-", "pH+", "Chlor", "Flockmittel"]),
        vol.Required("action"): vol.In(["manual_dose", "auto", "stop"]),
        vol.Optional("duration", default=30): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
        vol.Optional("safety_override", default=False): cv.boolean,
    }),
    
    "manage_pv_surplus": vol.Schema({
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("mode"): vol.In(["activate", "deactivate", "auto"]),
        vol.Optional("pump_speed", default=2): vol.All(vol.Coerce(int), vol.Range(min=1, max=3)),
    }),
}

# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def validate_dosing_safety(coordinator, device_key: str, duration: int, manager) -> Dict[str, Any]:
    """
    Validiere Dosierung für Sicherheit.
    
    Returns:
        dict: {"valid": bool, "error": str (optional), "safety_interval": int (optional)}
    """
    if device_key not in DEVICE_PARAMETERS:
        return {"valid": False, "error": "Unbekanntes Gerät"}
    
    device_config = DEVICE_PARAMETERS[device_key]
    safety_interval = device_config.get("safety_interval", 300)
    max_duration = device_config.get("max_dosing_duration", 300)
    
    # Safety-Lock prüfen
    if manager.check_safety_lock(device_key):
        remaining = manager.get_remaining_lock_time(device_key)
        return {"valid": False, "error": f"Safety-Intervall aktiv ({remaining}s)"}
    
    # Max. Dauer prüfen
    if duration > max_duration:
        return {"valid": False, "error": f"Dauer {duration}s > Max {max_duration}s"}
    
    # Aktueller Status prüfen
    current_state = coordinator.data.get(device_key, "")
    state_info = get_device_state_info(current_state, device_key)
    
    if state_info.get("active"):
        return {"valid": False, "error": f"{device_key} bereits aktiv"}
    
    # Tank-Level prüfen
    remaining_key = f"{device_key}_REMAINING_RANGE"
    remaining = coordinator.data.get(remaining_key)
    if remaining and str(remaining).lower() in ["empty", "low", "0"]:
        return {"valid": False, "error": f"Tank für {device_key} leer/niedrig"}
    
    return {"valid": True, "safety_interval": safety_interval}


def get_dosing_type_from_key(device_key: str) -> str:
    """Hole Dosiertyp aus Device Key."""
    reverse_map = {v: k for k, v in DOSING_TYPE_MAPPING.items()}
    return reverse_map.get(device_key, "Chlor")


def validate_temperature(temperature: float) -> bool:
    """Prüfe ob Temperatur im gültigen Bereich liegt."""
    return 20.0 <= temperature <= 40.0


def validate_pump_speed(speed: int) -> bool:
    """Prüfe ob Pumpengeschwindigkeit gültig ist."""
    return 1 <= speed <= 3
