"""Sensor-bezogene Konstanten für die Violet Pool Controller Integration."""

# =============================================================================
# SENSORS - Temperature, Chemistry, Analog, System
# =============================================================================

TEMP_SENSORS = {
    "onewire1_value": {"name": "Beckenwasser", "icon": "mdi:pool", "unit": "°C"},
    "onewire2_value": {"name": "Außentemperatur", "icon": "mdi:thermometer", "unit": "°C"},
    "onewire3_value": {"name": "Solarabsorber", "icon": "mdi:solar-power", "unit": "°C"},
    "onewire4_value": {"name": "Absorber-Rücklauf", "icon": "mdi:pipe", "unit": "°C"},
    "onewire5_value": {"name": "Wärmetauscher", "icon": "mdi:radiator", "unit": "°C"},
    "onewire6_value": {"name": "Heizungs-Speicher", "icon": "mdi:water-boiler", "unit": "°C"},
}

WATER_CHEM_SENSORS = {
    # IMPORTANT: pH sensor has NO unit per Home Assistant specification
    # This is intentional and correct behavior:
    # - pH Sensor (this): No unit - displays raw measurement value
    # - pH Number (setpoint): Has "pH" unit - for user input/setpoints
    "pH_value": {"name": "pH-Wert", "icon": "mdi:flask", "unit": None},  # pH ohne unit
    "orp_value": {"name": "Redoxpotential", "icon": "mdi:flash", "unit": "mV"},
    "pot_value": {"name": "Chlorgehalt", "icon": "mdi:test-tube", "unit": "mg/l"},
}

ANALOG_SENSORS = {
    "ADC1_value": {"name": "Filterdruck", "icon": "mdi:gauge", "unit": "bar"},
    "ADC2_value": {"name": "Überlaufbehälter", "icon": "mdi:water-percent", "unit": "cm"},
    "ADC3_value": {"name": "Durchflussmesser (4-20mA)", "icon": "mdi:pump", "unit": "m³/h"},
    "ADC4_value": {"name": "Analogsensor 4 (4-20mA)", "icon": "mdi:gauge", "unit": None},
    "ADC5_value": {"name": "Analogsensor 5 (0-10V)", "icon": "mdi:gauge", "unit": "V"},
    "IMP1_value": {"name": "Flow-Switch", "icon": "mdi:water-pump", "unit": "cm/s"},
    "IMP2_value": {"name": "Pumpen-Durchfluss", "icon": "mdi:pump", "unit": "m³/h"},
}

SYSTEM_SENSORS = {
    "CPU_TEMP": {"name": "CPU Temperatur", "icon": "mdi:chip", "unit": "°C"},
    "CPU_TEMP_CARRIER": {"name": "Carrier Board", "icon": "mdi:expansion-card", "unit": "°C"},
    "CPU_UPTIME": {"name": "System Uptime", "icon": "mdi:clock", "unit": None},
    # SYSTEM_*_TEMPERATURE and memory sensors: unit=None for backwards compatibility
    # with existing Home Assistant statistics (changing from None to a unit breaks statistics)
    "SYSTEM_CPU_TEMPERATURE": {"name": "System CPU Temperatur", "icon": "mdi:chip", "unit": None},
    "SYSTEM_CARRIER_CPU_TEMPERATURE": {"name": "Carrier CPU Temperatur", "icon": "mdi:expansion-card", "unit": None},
    "SYSTEM_DOSAGEMODULE_CPU_TEMPERATURE": {"name": "Dosiermodul CPU Temperatur", "icon": "mdi:chip", "unit": None},
    # Mixed-Case Varianten (vom Controller verwendet)
    "SYSTEM_cpu_temperature": {"name": "System CPU Temperatur", "icon": "mdi:chip", "unit": None},
    "SYSTEM_carrier_cpu_temperature": {"name": "Carrier CPU Temperatur", "icon": "mdi:expansion-card", "unit": None},
    "SYSTEM_dosagemodule_cpu_temperature": {"name": "Dosiermodul CPU Temperatur", "icon": "mdi:chip", "unit": None},
    "SYSTEM_memoryusage": {"name": "System Memory Usage", "icon": "mdi:memory", "unit": None},
    "SYSTEM_MEMORY": {"name": "System Memory Total", "icon": "mdi:memory", "unit": None},
    "MEMORY_USED": {"name": "Memory Used", "icon": "mdi:memory", "unit": None},
    "LOAD_AVG": {"name": "System Load Average", "icon": "mdi:gauge", "unit": None},
    "CPU_GOV": {"name": "CPU Governor", "icon": "mdi:chip", "unit": None},
    # ✅ Carrier/Module Alive Counts
    "SYSTEM_carrier_alive_count": {"name": "Carrier Alive Count", "icon": "mdi:counter", "unit": None},
    "SYSTEM_carrier_alive_faultcount": {"name": "Carrier Fault Count", "icon": "mdi:alert", "unit": None},
    "SYSTEM_dosagemodule_alive_count": {"name": "Dosiermodul Alive Count", "icon": "mdi:counter", "unit": None},
    "SYSTEM_dosagemodule_alive_faultcount": {"name": "Dosiermodul Fault Count", "icon": "mdi:alert", "unit": None},
    "SYSTEM_ext1module_alive_count": {"name": "Ext1 Modul Alive Count", "icon": "mdi:counter", "unit": None},
    "SYSTEM_ext1module_alive_faultcount": {"name": "Ext1 Modul Fault Count", "icon": "mdi:alert", "unit": None},
    # ✅ Pump RS485 Power
    "pump_rs485_pwr": {"name": "Pumpe RS485 Power", "icon": "mdi:flash", "unit": None},
}

# Status sensors for pumps, heaters, solar, etc.
STATUS_SENSORS = {
    "PUMPSTATE": {"name": "Pumpen-Status", "icon": "mdi:pump", "unit": None},
    "PUMP_STATE": {"name": "Pumpen-Status", "icon": "mdi:pump", "unit": None},
    "PUMP": {"name": "Pumpen-Status", "icon": "mdi:pump", "unit": None},  # ✅ Added PUMP
    "HEATERSTATE": {"name": "Heizungs-Status", "icon": "mdi:radiator", "unit": None},
    "HEATER_STATE": {"name": "Heizungs-Status", "icon": "mdi:radiator", "unit": None},
    "HEATER": {"name": "Heizungs-Status", "icon": "mdi:radiator", "unit": None},  # ✅ Added HEATER
    "SOLARSTATE": {"name": "Solar-Status", "icon": "mdi:solar-power", "unit": None},
    "SOLAR_STATE": {"name": "Solar-Status", "icon": "mdi:solar-power", "unit": None},
    "SOLAR": {"name": "Solar-Status", "icon": "mdi:solar-power", "unit": None},  # ✅ Added SOLAR
    "BACKWASHSTATE": {"name": "Rückspül-Status", "icon": "mdi:refresh", "unit": None},
    "BACKWASH_STATE": {"name": "Rückspül-Status", "icon": "mdi:refresh", "unit": None},
    "BACKWASH": {"name": "Rückspül-Status", "icon": "mdi:refresh", "unit": None},  # ✅ Added BACKWASH
    "FILTER_STATE": {"name": "Filter-Status", "icon": "mdi:air-filter", "unit": None},
    "LIGHT": {"name": "Beleuchtung Status", "icon": "mdi:lightbulb", "unit": None},  # ✅ Added LIGHT
    "PVSURPLUS": {"name": "PV-Überschuss Status", "icon": "mdi:solar-power-variant", "unit": None},  # ✅ Added PVSURPLUS
    "fw": {"name": "Firmware Version", "icon": "mdi:package-up", "unit": None},  # ✅ Added fw
    "FW": {"name": "Firmware Version", "icon": "mdi:package-up", "unit": None},  # ✅ Added FW
}

# =============================================================================
# RUNTIME AND TIMESTAMP SENSORS
# =============================================================================

RUNTIME_SENSORS = {
    "PUMP_RUNTIME": {"name": "Pumpe Laufzeit", "icon": "mdi:timer", "unit": None},
    "SOLAR_RUNTIME": {"name": "Solar Laufzeit", "icon": "mdi:timer", "unit": None},
    "HEATER_RUNTIME": {"name": "Heizung Laufzeit", "icon": "mdi:timer", "unit": None},
    "LIGHT_RUNTIME": {"name": "Beleuchtung Laufzeit", "icon": "mdi:timer", "unit": None},
    "BACKWASH_RUNTIME": {"name": "Rückspülung Laufzeit", "icon": "mdi:timer", "unit": None},
}

# Runtime for dosing
DOSING_RUNTIME_KEYS = [
    ("DOS_1_CL", "Chlor"),
    ("DOS_4_PHM", "pH-Minus"),
    ("DOS_5_PHP", "pH-Plus"),
    ("DOS_6_FLOC", "Flockmittel")
]
for dos_key, name in DOSING_RUNTIME_KEYS:
    RUNTIME_SENSORS[f"{dos_key}_RUNTIME"] = {
        "name": f"{name} Laufzeit", "icon": "mdi:timer", "unit": None
    }

# Runtime for extensions
for ext_bank in [1, 2]:
    for relay_num in range(1, 9):
        key = f"EXT{ext_bank}_{relay_num}_RUNTIME"
        RUNTIME_SENSORS[key] = {
            "name": f"Ext {ext_bank}.{relay_num} Laufzeit",
            "icon": "mdi:timer",
            "unit": None,
        }

TIMESTAMP_SENSORS = {
    "PUMP_LAST_ON": {"name": "Pumpe letzte Einschaltung"},
    "PUMP_LAST_OFF": {"name": "Pumpe letzte Ausschaltung"},
    "BACKWASH_LAST_AUTO_RUN": {"name": "Letzte automatische Rückspülung"},
    "BACKWASH_LAST_MANUAL_RUN": {"name": "Letzte manuelle Rückspülung"},
}

# =============================================================================
# UNIT MAPPINGS
# =============================================================================

UNIT_MAP = {
    # Temperature sensors
    "water_temp": "°C",
    "air_temp": "°C",
    "temp_value": "°C",
    "CPU_TEMP": "°C",
    "CPU_TEMP_CARRIER": "°C",
    # NOTE: SYSTEM_*_TEMPERATURE and SYSTEM_memory* sensors are in NO_UNIT_SENSORS
    # for backwards compatibility with existing Home Assistant statistics.
    # Do not add them to UNIT_MAP.
    # Water chemistry (pH WITHOUT unit!)
    "orp_value": "mV",
    "pot_value": "mg/l",
    # Analog values
    "ADC1_value": "bar",
    "ADC2_value": "cm",
    "ADC3_value": "m³/h",
    "ADC5_value": "V",
    "IMP1_value": "cm/s",
    "IMP2_value": "m³/h",
}

# Add OneWire temperatures
for i in range(1, 13):
    UNIT_MAP[f"onewire{i}_value"] = "°C"

# Add Pump RPMs
for i in range(4):
    UNIT_MAP[f"PUMP_RPM_{i}"] = "RPM"
    UNIT_MAP[f"PUMP_RPM_{i}_VALUE"] = "RPM"

# Sensors without units
# NOTE: System diagnostic sensors are excluded from units to maintain backwards
# compatibility with existing Home Assistant statistics. Adding units to sensors
# that previously had None breaks long-term statistics generation.
NO_UNIT_SENSORS = {
    "FW", "SW_VERSION", "HW_VERSION", "SERIAL_NUMBER", "MAC_ADDRESS", "IP_ADDRESS",
    "VERSION", "CPU_UPTIME", "BACKWASH_STATE", "PUMP_STATE", "HEATER_STATE",
    "SOLAR_STATE", "LIGHT_STATE", "time", "TIME", "CURRENT_TIME",
    "LOAD_AVG", "CPU_GOV", "fw", "pump_rs485_pwr",
    "SYSTEM_carrier_alive_count", "SYSTEM_carrier_alive_faultcount",
    "SYSTEM_dosagemodule_alive_count", "SYSTEM_dosagemodule_alive_faultcount",
    "SYSTEM_ext1module_alive_count", "SYSTEM_ext1module_alive_faultcount",
    # System diagnostic sensors - keep without units for statistics compatibility
    "SYSTEM_CPU_TEMPERATURE", "SYSTEM_CARRIER_CPU_TEMPERATURE", "SYSTEM_DOSAGEMODULE_CPU_TEMPERATURE",
    "SYSTEM_cpu_temperature", "SYSTEM_carrier_cpu_temperature", "SYSTEM_dosagemodule_cpu_temperature",
    "SYSTEM_memoryusage", "SYSTEM_MEMORY", "MEMORY_USED",
}

# =============================================================================
# FEATURE MAPPINGS
# =============================================================================

SENSOR_FEATURE_MAP = {
    # Temperature sensors
    "onewire1_value": None,  # Always show water temperature
    "onewire2_value": None,  # Always show air temperature
    "onewire3_value": "solar",
    "onewire4_value": "solar",
    "onewire5_value": "heating",
    "onewire6_value": "heating",
    # Water chemistry
    "pH_value": "ph_control",
    "orp_value": "chlorine_control",
    "pot_value": "chlorine_control",
    # System sensors
    "CPU_TEMP": None,
    "CPU_TEMP_CARRIER": None,
    "CPU_UPTIME": None,
}

__all__ = [
    "TEMP_SENSORS",
    "WATER_CHEM_SENSORS",
    "ANALOG_SENSORS",
    "SYSTEM_SENSORS",
    "STATUS_SENSORS",
    "RUNTIME_SENSORS",
    "TIMESTAMP_SENSORS",
    "UNIT_MAP",
    "NO_UNIT_SENSORS",
    "SENSOR_FEATURE_MAP",
]
