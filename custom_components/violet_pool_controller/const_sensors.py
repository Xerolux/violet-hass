# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""This module defines constants related to sensor entities.

It includes definitions for different categories of sensors such as temperature,
water chemistry, and system diagnostics. It also provides unit mappings and
mappings between sensor keys and integration features to control sensor creation
based on user configuration.
"""

from __future__ import annotations

# =============================================================================
# SENSOR DEFINITIONS
# =============================================================================

TEMP_SENSORS = {
    "onewire1_value": {
        "name": "Pool Water",
        "translation_key": "onewire1_value",
        "icon": "mdi:pool",
    },
    "onewire2_value": {
        "name": "Outside Temperature",
        "translation_key": "onewire2_value",
        "icon": "mdi:thermometer",
    },
    "onewire3_value": {
        "name": "Solar Absorber",
        "translation_key": "onewire3_value",
        "icon": "mdi:solar-power",
    },
    "onewire4_value": {
        "name": "Absorber Return",
        "translation_key": "onewire4_value",
        "icon": "mdi:pipe-valve",
    },
    "onewire5_value": {
        "name": "Heat Exchanger",
        "translation_key": "onewire5_value",
        "icon": "mdi:radiator",
    },
    "onewire6_value": {
        "name": "Heater Storage",
        "translation_key": "onewire6_value",
        "icon": "mdi:water-boiler",
    },
    "onewire7_value": {
        "name": "Temperature Sensor 7",
        "translation_key": "onewire7_value",
        "icon": "mdi:thermometer",
    },
    "onewire8_value": {
        "name": "Temperature Sensor 8",
        "translation_key": "onewire8_value",
        "icon": "mdi:thermometer",
    },
    "onewire9_value": {
        "name": "Temperature Sensor 9",
        "translation_key": "onewire9_value",
        "icon": "mdi:thermometer",
    },
    "onewire10_value": {
        "name": "Temperature Sensor 10",
        "translation_key": "onewire10_value",
        "icon": "mdi:thermometer",
    },
    "onewire11_value": {
        "name": "Temperature Sensor 11",
        "translation_key": "onewire11_value",
        "icon": "mdi:thermometer",
    },
    "onewire12_value": {
        "name": "Temperature Sensor 12",
        "translation_key": "onewire12_value",
        "icon": "mdi:thermometer",
    },
}

WATER_CHEM_SENSORS = {
    "pH_value": {"name": "pH Value", "translation_key": "ph_value", "icon": "mdi:ph"},
    "orp_value": {
        "name": "ORP Value",
        "translation_key": "orp_value",
        "icon": "mdi:lightning-bolt-circle",
    },
    "pot_value": {
        "name": "Chlorine Level",
        "translation_key": "pot_value",
        "icon": "mdi:water-plus",
    },
}

ANALOG_SENSORS = {
    "ADC1_value": {
        "name": "Filter Pressure",
        "translation_key": "adc1_value",
        "icon": "mdi:gauge",
    },
    "ADC2_value": {
        "name": "Overflow Tank",
        "translation_key": "adc2_value",
        "icon": "mdi:water-sync",
    },
    "ADC3_value": {
        "name": "Flow Meter (4-20mA)",
        "translation_key": "adc3_value",
        "icon": "mdi:swap-horizontal",
    },
    "ADC4_value": {
        "name": "Analog Sensor 4 (4-20mA)",
        "translation_key": "adc4_value",
        "icon": "mdi:gauge",
    },
    "ADC5_value": {
        "name": "Analog Sensor 5 (0-10V)",
        "translation_key": "adc5_value",
        "icon": "mdi:sine-wave",
    },
    "IMP1_value": {
        "name": "Dosing Inflow",
        "translation_key": "imp1_value",
        "icon": "mdi:pipe-valve",
    },
    "IMP2_value": {
        "name": "Pump Flow Rate",
        "translation_key": "imp2_value",
        "icon": "mdi:water-pump",
    },
}

SYSTEM_SENSORS = {
    "CPU_TEMP": {
        "name": "CPU Temperature",
        "translation_key": "cpu_temp",
        "icon": "mdi:thermometer-alert",
    },
    "CPU_TEMP_CARRIER": {
        "name": "Carrier Board",
        "translation_key": "cpu_temp_carrier",
        "icon": "mdi:motherboard",
    },
    "CPU_UPTIME": {
        "name": "System Uptime",
        "translation_key": "cpu_uptime",
        "icon": "mdi:clock-time-eight",
    },
    "SYSTEM_CPU_TEMPERATURE": {
        "name": "System CPU Temperature",
        "translation_key": "system_cpu_temperature",
        "icon": "mdi:thermometer-check",
    },
    "SYSTEM_CARRIER_CPU_TEMPERATURE": {
        "name": "Carrier CPU Temperature",
        "translation_key": "system_carrier_cpu_temperature",
        "icon": "mdi:memory",
    },
    # Spec key is lowercase: SYSTEM_dosagemodule_cpu_temperature
    "SYSTEM_dosagemodule_cpu_temperature": {
        "name": "Dosing Module CPU Temperature",
        "translation_key": "system_dosagemodule_cpu_temperature",
        "icon": "mdi:memory-lan",
    },
    "SYSTEM_memoryusage": {
        "name": "System Memory Usage",
        "translation_key": "system_memoryusage",
        "icon": "mdi:memory-lan",
    },
}

STATUS_SENSORS = {
    "PUMP": {"name": "Pump Status", "translation_key": "pump", "icon": "mdi:pump"},
    "HEATER": {
        "name": "Heater Status",
        "translation_key": "heater",
        "icon": "mdi:radiator",
    },
    "SOLAR": {
        "name": "Solar Status",
        "translation_key": "solar",
        "icon": "mdi:solar-power",
    },
    "BACKWASH": {
        "name": "Backwash Status",
        "translation_key": "backwash",
        "icon": "mdi:autorenew",
    },
    "BACKWASHRINSE": {
        "name": "Backwash Rinse Status",
        "translation_key": "backwashrinse",
        "icon": "mdi:water-opacity",
    },
    "LIGHT": {
        "name": "Lighting Status",
        "translation_key": "light",
        "icon": "mdi:lightbulb",
    },
    "REFILL": {
        "name": "Refill Status",
        "translation_key": "refill",
        "icon": "mdi:water",
    },
    "ECO": {
        "name": "ECO Status",
        "translation_key": "eco",
        "icon": "mdi:leaf",
    },
    "PVSURPLUS": {
        "name": "PV Surplus Status",
        "translation_key": "pvsurplus",
        "icon": "mdi:solar-power",
    },
    "FW": {
        "name": "Firmware Version",
        "translation_key": "fw",
        "icon": "mdi:package-variant",
    },
}

DOSING_STATE_SENSORS = {
    "DOS_1_CL_STATE": {
        "name": "Chlorine Dosing Status",
        "translation_key": "dos_1_cl_state",
        "icon": "mdi:flask-outline",
    },
    "DOS_2_ELO_STATE": {
        "name": "Electrolysis Status",
        "translation_key": "dos_2_elo_state",
        "icon": "mdi:lightning-bolt",
    },
    "DOS_4_PHM_STATE": {
        "name": "pH- Dosing Status",
        "translation_key": "dos_4_phm_state",
        "icon": "mdi:flask-minus",
    },
    "DOS_5_PHP_STATE": {
        "name": "pH+ Dosing Status",
        "translation_key": "dos_5_php_state",
        "icon": "mdi:flask-plus",
    },
    "DOS_6_FLOC_STATE": {
        "name": "Flocculation Status",
        "translation_key": "dos_6_floc_state",
        "icon": "mdi:water",
    },
}

RUNTIME_SENSORS = {
    "PUMP_RUNTIME": {
        "name": "Pump Runtime Today",
        "translation_key": "pump_runtime",
        "icon": "mdi:clock-outline",
    },
    "SOLAR_RUNTIME": {
        "name": "Solar Runtime Today",
        "translation_key": "solar_runtime",
        "icon": "mdi:clock-outline",
    },
    "HEATER_RUNTIME": {
        "name": "Heater Runtime Today",
        "translation_key": "heater_runtime",
        "icon": "mdi:clock-outline",
    },
    "LIGHT_RUNTIME": {
        "name": "Light Runtime Today",
        "translation_key": "light_runtime",
        "icon": "mdi:clock-outline",
    },
    "BACKWASH_RUNTIME": {
        "name": "Backwash Runtime",
        "translation_key": "backwash_runtime",
        "icon": "mdi:clock-outline",
    },
    "BACKWASHRINSE_RUNTIME": {
        "name": "Backwash Rinse Runtime",
        "translation_key": "backwashrinse_runtime",
        "icon": "mdi:clock-outline",
    },
    "ECO_RUNTIME": {
        "name": "ECO Runtime",
        "translation_key": "eco_runtime",
        "icon": "mdi:clock-outline",
    },
    "DOS_1_CL_RUNTIME": {
        "name": "Chlorine Dosing Runtime",
        "translation_key": "dos_1_cl_runtime",
        "icon": "mdi:clock-outline",
    },
    "DOS_2_ELO_RUNTIME": {
        "name": "Electrolysis Runtime",
        "translation_key": "dos_2_elo_runtime",
        "icon": "mdi:clock-outline",
    },
    "DOS_3_ELO_REV_RUNTIME": {
        "name": "Electrolysis Reverse Runtime",
        "translation_key": "dos_3_elo_rev_runtime",
        "icon": "mdi:clock-outline",
    },
    "DOS_4_PHM_RUNTIME": {
        "name": "pH- Dosing Runtime",
        "translation_key": "dos_4_phm_runtime",
        "icon": "mdi:clock-outline",
    },
    "DOS_5_PHP_RUNTIME": {
        "name": "pH+ Dosing Runtime",
        "translation_key": "dos_5_php_runtime",
        "icon": "mdi:clock-outline",
    },
    "DOS_6_FLOC_RUNTIME": {
        "name": "Flocculation Runtime",
        "translation_key": "dos_6_floc_runtime",
        "icon": "mdi:clock-outline",
    },
    "REFILL_RUNTIME": {
        "name": "Refill Runtime",
        "translation_key": "refill_runtime",
        "icon": "mdi:clock-outline",
    },
    # Extension relay runtimes (EXT1/EXT2 modules)
    **{f"EXT{i}_{j}_RUNTIME": {
        "name": f"Extension {i} Relay {j} Runtime",
        "translation_key": f"ext{i}_{j}_runtime",
        "icon": "mdi:clock-outline",
    } for i in (1, 2) for j in range(1, 9)},
    # OMNI module runtimes
    **{f"OMNI_DC{i}_RUNTIME": {
        "name": f"OMNI DC Motor {i} Runtime",
        "translation_key": f"omni_dc{i}_runtime",
        "icon": "mdi:clock-outline",
    } for i in range(6)},
    # Pump RPM level runtimes
    **{f"PUMP_RPM_{i}_RUNTIME": {
        "name": f"Pump RPM Level {i} Runtime",
        "translation_key": f"pump_rpm_{i}_runtime",
        "icon": "mdi:clock-outline",
    } for i in range(4)},
}

DOSING_STATS_SENSORS = {
    "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": {
        "name": "Chlorine Daily Dosing",
        "translation_key": "dos_1_cl_daily",
        "icon": "mdi:beaker",
    },
    "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": {
        "name": "pH- Daily Dosing",
        "translation_key": "dos_4_phm_daily",
        "icon": "mdi:beaker-minus",
    },
    "DOS_5_PHP_DAILY_DOSING_AMOUNT_ML": {
        "name": "pH+ Daily Dosing",
        "translation_key": "dos_5_php_daily",
        "icon": "mdi:beaker-plus",
    },
    "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": {
        "name": "Flocculant Daily Dosing",
        "translation_key": "dos_6_floc_daily",
        "icon": "mdi:beaker-outline",
    },
}

COMPOSITE_STATE_SENSORS = {
    "PUMPSTATE": {
        "name": "Pump Detail Status",
        "translation_key": "pumpstate",
        "icon": "mdi:water-pump",
    },
    "HEATERSTATE": {
        "name": "Heater Detail Status",
        "translation_key": "heaterstate",
        "icon": "mdi:radiator",
    },
    "SOLARSTATE": {
        "name": "Solar Detail Status",
        "translation_key": "solarstate",
        "icon": "mdi:solar-power-variant",
    },
}

PRIMARY_SENSOR_KEYS = {
    "onewire1_value",
    "pH_value",
    "pot_value",
    "orp_value",
    "IMP2_value",
    "ADC1_value",
}

# =============================================================================
# UNIT MAPPINGS
# =============================================================================

UNIT_MAP = {
    # Temperatures
    "onewire1_value": "°C",
    "onewire2_value": "°C",
    "onewire3_value": "°C",
    "onewire4_value": "°C",
    "onewire5_value": "°C",
    "onewire6_value": "°C",
    "onewire7_value": "°C",
    "onewire8_value": "°C",
    "onewire9_value": "°C",
    "onewire10_value": "°C",
    "onewire11_value": "°C",
    "onewire12_value": "°C",
    "CPU_TEMP": "°C",
    "CPU_TEMP_CARRIER": "°C",
    # Water Chemistry
    "orp_value": "mV",
    "pot_value": "mg/l",
    # Analog Sensors
    "ADC1_value": "bar",
    "ADC2_value": "cm",
    "ADC3_value": "m³/h",
    "ADC5_value": "V",
    "IMP1_value": "cm/s",
    "IMP2_value": "m³/h",
    # Pump RPMs - only _VALUE sensors carry actual RPM measurements
    # PUMP_RPM_{i} (without _VALUE) returns a state code (0-6), not a speed in RPM
    **{f"PUMP_RPM_{i}_VALUE": "RPM" for i in range(4)},
    # Dosing Statistics
    "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "ml",
    "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "ml",
    "DOS_5_PHP_DAILY_DOSING_AMOUNT_ML": "ml",
    "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": "ml",
}

# Sensors that should explicitly have no unit.
# This is important for sensors where a unit is semantically incorrect
# (e.g., firmware versions) or to maintain backward compatibility for
# Home Assistant's long-term statistics.
NO_UNIT_SENSORS = {
    "FW",
    "SW_VERSION",
    "HW_VERSION",
    "SERIAL_NUMBER",
    "MAC_ADDRESS",
    "IP_ADDRESS",
    "VERSION",
    "CPU_UPTIME",
    "time",
    "TIME",
    "CURRENT_TIME",
    "LOAD_AVG",
    "CPU_GOV",
    "SYSTEM_CPU_TEMPERATURE",
    "SYSTEM_CARRIER_CPU_TEMPERATURE",
    # SYSTEM_dosagemodule_cpu_temperature deliberately not listed: it is a
    # FLOAT in °C and must keep its temperature unit
    "SYSTEM_memoryusage",
    *(f"PUMP_RPM_{i}" for i in range(4)),
    "PUMP_RUNTIME",
    "SOLAR_RUNTIME",
    "HEATER_RUNTIME",
    "LIGHT_RUNTIME",
    "BACKWASH_RUNTIME",
    "BACKWASHRINSE_RUNTIME",
    "ECO_RUNTIME",
    "DOS_1_CL_RUNTIME",
    "DOS_2_ELO_RUNTIME",
    "DOS_3_ELO_REV_RUNTIME",
    "DOS_4_PHM_RUNTIME",
    "DOS_5_PHP_RUNTIME",
    "DOS_6_FLOC_RUNTIME",
    "REFILL_RUNTIME",
    # Extension relay runtimes
    *(f"EXT{i}_{j}_RUNTIME" for i in (1, 2) for j in range(1, 9)),
    # OMNI module runtimes
    *(f"OMNI_DC{i}_RUNTIME" for i in range(6)),
    # Pump RPM level runtimes
    *(f"PUMP_RPM_{i}_RUNTIME" for i in range(4)),
}

# =============================================================================
# FEATURE MAPPINGS
# =============================================================================

# Maps specific sensor keys to the features that enable them.
# A value of None means the sensor is always created if available.
SENSOR_FEATURE_MAP = {
    "onewire1_value": None,
    "onewire2_value": None,
    "onewire3_value": "solar",
    "onewire4_value": "solar",
    "onewire5_value": "heating",
    "onewire6_value": "heating",
    "onewire7_value": None,
    "onewire8_value": None,
    "onewire9_value": None,
    "onewire10_value": None,
    "onewire11_value": None,
    "onewire12_value": None,
    "DOS_1_CL_STATE": "chlorine_control",
    "DOS_2_ELO_STATE": "chlorine_control",
    "DOS_4_PHM_STATE": "ph_control",
    "DOS_5_PHP_STATE": "ph_control",
    "DOS_6_FLOC_STATE": "flocculation",
    "PUMPSTATE": "filter_control",
    "HEATERSTATE": "heating",
    "SOLARSTATE": "solar",
    "pH_value": "ph_control",
    "orp_value": "chlorine_control",
    "pot_value": "chlorine_control",
    "CPU_TEMP": None,
    "CPU_UPTIME": None,
    "REFILL": "water_refill",
    "ECO": None,
    "PUMP_RUNTIME": "filter_control",
    "SOLAR_RUNTIME": "solar",
    "HEATER_RUNTIME": "heating",
    "LIGHT_RUNTIME": "led_lighting",
    "BACKWASH_RUNTIME": "backwash",
    "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "chlorine_control",
    "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "ph_control",
    "DOS_5_PHP_DAILY_DOSING_AMOUNT_ML": "ph_control",
    "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": "flocculation",
}
