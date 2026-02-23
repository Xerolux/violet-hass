"""Config Flow Constants."""

from typing import Final

# =============================================================================
# VALIDATION LIMITS
# =============================================================================

MIN_POLLING_INTERVAL: Final = 10
MAX_POLLING_INTERVAL: Final = 3600
MIN_TIMEOUT: Final = 1
MAX_TIMEOUT: Final = 60
MIN_RETRIES: Final = 1
MAX_RETRIES: Final = 10
MIN_POOL_SIZE: Final = 0.1
MAX_POOL_SIZE: Final = 1000.0
MIN_DEVICE_ID: Final = 1
MAX_DEVICE_ID: Final = 99

# =============================================================================
# RETRY CONSTANTS
# =============================================================================

BASE_RETRY_DELAY: Final = 2
DEFAULT_API_TIMEOUT: Final = 10

# =============================================================================
# ERROR MESSAGES
# =============================================================================

ERROR_ALREADY_CONFIGURED: Final = "already_configured"
ERROR_INVALID_IP: Final = "invalid_ip_address"
ERROR_CANNOT_CONNECT: Final = "cannot_connect"
ERROR_AGREEMENT_DECLINED: Final = "agreement_declined"

# =============================================================================
# POOL & DISINFECTION OPTIONS
# =============================================================================

POOL_TYPE_OPTIONS = {
    "outdoor": "🏖️ Freibad",
    "indoor": "🏠 Hallenbad",
    "whirlpool": "🛁 Whirlpool/Spa",
    "natural": "🌿 Naturpool/Schwimmteich",
    "combination": "🔄 Kombination",
}

DISINFECTION_OPTIONS = {
    "chlorine": "🧪 Chlor (Flüssig/Tabletten)",
    "salt": "🧂 Salzelektrolyse",
    "bromine": "⚗️ Brom",
    "active_oxygen": "💧 Aktivsauerstoff/H₂O₂",
    "uv": "💡 UV-Desinfektion",
    "ozone": "🌀 Ozon-Desinfektion",
}

# =============================================================================
# ENHANCED FEATURES
# =============================================================================

ENHANCED_FEATURES = {
    "heating": {"icon": "🔥", "name": "Heizungssteuerung"},
    "solar": {"icon": "☀️", "name": "Solarabsorber"},
    "ph_control": {"icon": "🧪", "name": "pH-Automatik"},
    "chlorine_control": {"icon": "💧", "name": "Chlor-Management"},
    "cover_control": {"icon": "🪟", "name": "Abdeckungssteuerung"},
    "backwash": {"icon": "🔄", "name": "Rückspül-Automatik"},
    "pv_surplus": {"icon": "🔋", "name": "PV-Überschuss"},
    "filter_control": {"icon": "🌊", "name": "Filterpumpe"},
    "water_level": {"icon": "📏", "name": "Füllstand-Monitor"},
    "water_refill": {"icon": "🚰", "name": "Auto-Nachfüllung"},
    "led_lighting": {"icon": "💡", "name": "LED-Beleuchtung"},
    "digital_inputs": {"icon": "🔌", "name": "Digitale Eingänge"},
    "extension_outputs": {"icon": "🔗", "name": "Erweiterungsmodule"},
}

# =============================================================================
# DOCUMENTATION URLs
# =============================================================================

GITHUB_BASE_URL: Final = "https://github.com/xerolux/violet-hass"
HELP_DOC_DE_URL: Final = f"{GITHUB_BASE_URL}/blob/main/docs/help/configuration-guide.de.md"
HELP_DOC_EN_URL: Final = f"{GITHUB_BASE_URL}/blob/main/docs/help/configuration-guide.en.md"
SUPPORT_URL: Final = f"{GITHUB_BASE_URL}/issues"

# =============================================================================
# MENU ACTIONS
# =============================================================================

MENU_ACTION_START: Final = "start_setup"
MENU_ACTION_HELP: Final = "open_help"
