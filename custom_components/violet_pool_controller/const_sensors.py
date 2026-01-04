"""This module defines constants related to sensor entities.

It includes definitions for different categories of sensors such as temperature,
water chemistry, and system diagnostics. It also provides unit mappings and
mappings between sensor keys and integration features to control sensor creation
based on user configuration.
"""

# =============================================================================
# SENSOR DEFINITIONS
# =============================================================================

TEMP_SENSORS = {
    "onewire1_value": {"name": "Beckenwasser", "icon": "mdi:pool"},
    "onewire2_value": {"name": "Außentemperatur", "icon": "mdi:thermometer"},
    "onewire3_value": {"name": "Solarabsorber", "icon": "mdi:solar-power"},
    "onewire4_value": {"name": "Absorber-Rücklauf", "icon": "mdi:pipe"},
    "onewire5_value": {"name": "Wärmetauscher", "icon": "mdi:radiator"},
    "onewire6_value": {"name": "Heizungs-Speicher", "icon": "mdi:water-boiler"},
}

WATER_CHEM_SENSORS = {
    "pH_value": {"name": "pH-Wert", "icon": "mdi:flask"},
    "orp_value": {"name": "Redoxpotential", "icon": "mdi:flash"},
    "pot_value": {"name": "Chlorgehalt", "icon": "mdi:test-tube"},
}

ANALOG_SENSORS = {
    "ADC1_value": {"name": "Filterdruck", "icon": "mdi:gauge"},
    "ADC2_value": {"name": "Überlaufbehälter", "icon": "mdi:water-percent"},
    "ADC3_value": {"name": "Durchflussmesser (4-20mA)", "icon": "mdi:pump"},
    "ADC4_value": {"name": "Analogsensor 4 (4-20mA)", "icon": "mdi:gauge"},
    "ADC5_value": {"name": "Analogsensor 5 (0-10V)", "icon": "mdi:gauge"},
    "IMP1_value": {"name": "Flow-Switch", "icon": "mdi:water-pump"},
    "IMP2_value": {"name": "Pumpen-Durchfluss", "icon": "mdi:pump"},
}

SYSTEM_SENSORS = {
    "CPU_TEMP": {"name": "CPU Temperatur", "icon": "mdi:chip"},
    "CPU_TEMP_CARRIER": {"name": "Carrier Board", "icon": "mdi:expansion-card"},
    "CPU_UPTIME": {"name": "System Uptime", "icon": "mdi:clock"},
    "SYSTEM_CPU_TEMPERATURE": {"name": "System CPU Temperatur", "icon": "mdi:chip"},
    "SYSTEM_CARRIER_CPU_TEMPERATURE": {
        "name": "Carrier CPU Temperatur",
        "icon": "mdi:expansion-card",
    },
    "SYSTEM_DOSAGEMODULE_CPU_TEMPERATURE": {
        "name": "Dosiermodul CPU Temperatur",
        "icon": "mdi:chip",
    },
    "SYSTEM_memoryusage": {"name": "System Memory Usage", "icon": "mdi:memory"},
}

STATUS_SENSORS = {
    "PUMP": {"name": "Pumpen-Status", "icon": "mdi:pump"},
    "HEATER": {"name": "Heizungs-Status", "icon": "mdi:radiator"},
    "SOLAR": {"name": "Solar-Status", "icon": "mdi:solar-power"},
    "BACKWASH": {"name": "Rückspül-Status", "icon": "mdi:refresh"},
    "LIGHT": {"name": "Beleuchtung Status", "icon": "mdi:lightbulb"},
    "PVSURPLUS": {"name": "PV-Überschuss Status", "icon": "mdi:solar-power-variant"},
    "FW": {"name": "Firmware Version", "icon": "mdi:package-up"},
}

DOSING_STATE_SENSORS = {
    "DOS_1_CL_STATE": {"name": "Chlor Dosierung Status", "icon": "mdi:flask-outline"},
    "DOS_2_ELO_STATE": {"name": "Elektrolyse Status", "icon": "mdi:lightning-bolt"},
    "DOS_4_PHM_STATE": {"name": "pH- Dosierung Status", "icon": "mdi:flask-minus"},
    "DOS_5_PHP_STATE": {"name": "pH+ Dosierung Status", "icon": "mdi:flask-plus"},
    "DOS_6_FLOC_STATE": {"name": "Flockung Status", "icon": "mdi:flask"},
}

COMPOSITE_STATE_SENSORS = {
    "PUMPSTATE": {"name": "Pumpen Detail-Status", "icon": "mdi:pump"},
    "HEATERSTATE": {"name": "Heizung Detail-Status", "icon": "mdi:radiator"},
    "SOLARSTATE": {"name": "Solar Detail-Status", "icon": "mdi:solar-power"},
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
    # Pump RPMs
    **{f"PUMP_RPM_{i}": "RPM" for i in range(4)},
    **{f"PUMP_RPM_{i}_VALUE": "RPM" for i in range(4)},
}

# Sensors that should explicitly have no unit.
# This is important for sensors where a unit is semantically incorrect (e.g., firmware versions)
# or to maintain backward compatibility for Home Assistant's long-term statistics.
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
    # System diagnostic sensors are kept unitless for statistics compatibility
    "SYSTEM_CPU_TEMPERATURE",
    "SYSTEM_CARRIER_CPU_TEMPERATURE",
    "SYSTEM_DOSAGEMODULE_CPU_TEMPERATURE",
    "SYSTEM_memoryusage",
}

# =============================================================================
# FEATURE MAPPINGS
# =============================================================================

# Maps specific sensor keys to the features that enable them.
# A value of None means the sensor is always created if available.
SENSOR_FEATURE_MAP = {
    # Always create core temperature sensors
    "onewire1_value": None,
    "onewire2_value": None,
    # Feature-dependent sensors
    "onewire3_value": "solar",
    # Dosing state sensors (array-based)
    "DOS_1_CL_STATE": "chlorine_control",
    "DOS_2_ELO_STATE": "chlorine_control",
    "DOS_4_PHM_STATE": "ph_control",
    "DOS_5_PHP_STATE": "ph_control",
    "DOS_6_FLOC_STATE": "flocculation",
    # Composite state sensors (pipe-separated strings)
    "PUMPSTATE": "filter_control",
    "HEATERSTATE": "heating",
    "SOLARSTATE": "solar",
    "onewire4_value": "solar",
    "onewire5_value": "heating",
    "onewire6_value": "heating",
    "pH_value": "ph_control",
    "orp_value": "chlorine_control",
    "pot_value": "chlorine_control",
    # Always create core system sensors
    "CPU_TEMP": None,
    "CPU_UPTIME": None,
}
