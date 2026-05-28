# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Config Flow Constants."""

from __future__ import annotations

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
    "outdoor": "🏖️ Outdoor Pool",
    "indoor": "🏠 Indoor Pool",
    "whirlpool": "🛁 Whirlpool/Spa",
    "natural": "🌿 Natural Pool",
    "combination": "🔄 Combination",
}

DISINFECTION_OPTIONS = {
    "chlorine": "🧪 Chlorine (Liquid/Tablets)",
    "salt": "🧂 Salt Electrolysis",
    "bromine": "⚗️ Bromine",
    "active_oxygen": "💧 Active Oxygen/H₂O₂",
    "uv": "💡 UV Disinfection",
    "ozone": "🌀 Ozone Treatment",
}

# =============================================================================
# ENHANCED FEATURES
# =============================================================================

ENHANCED_FEATURES = {
    "heating": {"icon": "🔥", "name": "Heating Control"},
    "solar": {"icon": "☀️", "name": "Solar Absorber"},
    "ph_control": {"icon": "🧪", "name": "pH Control"},
    "chlorine_control": {"icon": "💧", "name": "Chlorine Management"},
    "cover_control": {"icon": "🪟", "name": "Cover Control"},
    "backwash": {"icon": "🔄", "name": "Backwash Automation"},
    "pv_surplus": {"icon": "🔋", "name": "PV Surplus"},
    "filter_control": {"icon": "🌊", "name": "Filter Pump"},
    "water_level": {"icon": "📏", "name": "Water Level Monitor"},
    "water_refill": {"icon": "🚰", "name": "Auto Refill"},
    "led_lighting": {"icon": "💡", "name": "LED Lighting"},
    "digital_inputs": {"icon": "🔌", "name": "Digital Inputs"},
    "extension_outputs": {"icon": "🔗", "name": "Extension Modules"},
}

# =============================================================================
# DOCUMENTATION URLs
# =============================================================================

GITHUB_BASE_URL: Final = "https://github.com/xerolux/violet-hass"
HELP_DOC_DE_URL: Final = (
    f"{GITHUB_BASE_URL}/blob/main/docs/help/configuration-guide.de.md"
)
HELP_DOC_EN_URL: Final = (
    f"{GITHUB_BASE_URL}/blob/main/docs/help/configuration-guide.en.md"
)
SUPPORT_URL: Final = f"{GITHUB_BASE_URL}/issues"

# =============================================================================
# MENU ACTIONS
# =============================================================================

MENU_ACTION_START: Final = "start_setup"
MENU_ACTION_HELP: Final = "open_help"
