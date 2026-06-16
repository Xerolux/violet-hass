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
        "name": "Poolwasser",
        "translation_key": "onewire1_value",
        "icon": "mdi:pool",
    },
    "onewire2_value": {
        "name": "Außentemperatur",
        "translation_key": "onewire2_value",
        "icon": "mdi:thermometer",
    },
    "onewire3_value": {
        "name": "Sonnenkollektor",
        "translation_key": "onewire3_value",
        "icon": "mdi:solar-power",
    },
    "onewire4_value": {
        "name": "Kollektor-Rücklauf",
        "translation_key": "onewire4_value",
        "icon": "mdi:pipe-valve",
    },
    "onewire5_value": {
        "name": "Wärmetauscher",
        "translation_key": "onewire5_value",
        "icon": "mdi:radiator",
    },
    "onewire6_value": {
        "name": "Wärmespeicher",
        "translation_key": "onewire6_value",
        "icon": "mdi:water-boiler",
    },
    "onewire7_value": {
        "name": "Temperatursensor 7",
        "translation_key": "onewire7_value",
        "icon": "mdi:thermometer",
    },
    "onewire8_value": {
        "name": "Temperatursensor 8",
        "translation_key": "onewire8_value",
        "icon": "mdi:thermometer",
    },
    "onewire9_value": {
        "name": "Temperatursensor 9",
        "translation_key": "onewire9_value",
        "icon": "mdi:thermometer",
    },
    "onewire10_value": {
        "name": "Temperatursensor 10",
        "translation_key": "onewire10_value",
        "icon": "mdi:thermometer",
    },
    "onewire11_value": {
        "name": "Temperatursensor 11",
        "translation_key": "onewire11_value",
        "icon": "mdi:thermometer",
    },
    "onewire12_value": {
        "name": "Temperatursensor 12",
        "translation_key": "onewire12_value",
        "icon": "mdi:thermometer",
    },
}

ONEWIRE_ROMCODE_SENSORS = {
    "onewire1_rcode": {
        "name": "OneWire-ROM-Code 1",
        "translation_key": "onewire1_rcode",
        "icon": "mdi:identifier",
    },
    "onewire1_romcode": {
        "name": "OneWire-ROM-Code 1",
        "translation_key": "onewire1_romcode",
        "icon": "mdi:identifier",
    },
    "onewire2_rcode": {
        "name": "OneWire-ROM-Code 2",
        "translation_key": "onewire2_rcode",
        "icon": "mdi:identifier",
    },
    "onewire2_romcode": {
        "name": "OneWire-ROM-Code 2",
        "translation_key": "onewire2_romcode",
        "icon": "mdi:identifier",
    },
    "onewire3_rcode": {
        "name": "OneWire-ROM-Code 3",
        "translation_key": "onewire3_rcode",
        "icon": "mdi:identifier",
    },
    "onewire3_romcode": {
        "name": "OneWire-ROM-Code 3",
        "translation_key": "onewire3_romcode",
        "icon": "mdi:identifier",
    },
    "onewire4_rcode": {
        "name": "OneWire-ROM-Code 4",
        "translation_key": "onewire4_rcode",
        "icon": "mdi:identifier",
    },
    "onewire4_romcode": {
        "name": "OneWire-ROM-Code 4",
        "translation_key": "onewire4_romcode",
        "icon": "mdi:identifier",
    },
    "onewire5_rcode": {
        "name": "OneWire-ROM-Code 5",
        "translation_key": "onewire5_rcode",
        "icon": "mdi:identifier",
    },
    "onewire5_romcode": {
        "name": "OneWire-ROM-Code 5",
        "translation_key": "onewire5_romcode",
        "icon": "mdi:identifier",
    },
    "onewire6_rcode": {
        "name": "OneWire-ROM-Code 6",
        "translation_key": "onewire6_rcode",
        "icon": "mdi:identifier",
    },
    "onewire6_romcode": {
        "name": "OneWire-ROM-Code 6",
        "translation_key": "onewire6_romcode",
        "icon": "mdi:identifier",
    },
    "onewire7_rcode": {
        "name": "OneWire-ROM-Code 7",
        "translation_key": "onewire7_rcode",
        "icon": "mdi:identifier",
    },
    "onewire7_romcode": {
        "name": "OneWire-ROM-Code 7",
        "translation_key": "onewire7_romcode",
        "icon": "mdi:identifier",
    },
    "onewire8_rcode": {
        "name": "OneWire-ROM-Code 8",
        "translation_key": "onewire8_rcode",
        "icon": "mdi:identifier",
    },
    "onewire8_romcode": {
        "name": "OneWire-ROM-Code 8",
        "translation_key": "onewire8_romcode",
        "icon": "mdi:identifier",
    },
    "onewire9_rcode": {
        "name": "OneWire-ROM-Code 9",
        "translation_key": "onewire9_rcode",
        "icon": "mdi:identifier",
    },
    "onewire9_romcode": {
        "name": "OneWire-ROM-Code 9",
        "translation_key": "onewire9_romcode",
        "icon": "mdi:identifier",
    },
    "onewire10_rcode": {
        "name": "OneWire-ROM-Code 10",
        "translation_key": "onewire10_rcode",
        "icon": "mdi:identifier",
    },
    "onewire10_romcode": {
        "name": "OneWire-ROM-Code 10",
        "translation_key": "onewire10_romcode",
        "icon": "mdi:identifier",
    },
    "onewire11_rcode": {
        "name": "OneWire-ROM-Code 11",
        "translation_key": "onewire11_rcode",
        "icon": "mdi:identifier",
    },
    "onewire11_romcode": {
        "name": "OneWire-ROM-Code 11",
        "translation_key": "onewire11_romcode",
        "icon": "mdi:identifier",
    },
    "onewire12_rcode": {
        "name": "OneWire-ROM-Code 12",
        "translation_key": "onewire12_rcode",
        "icon": "mdi:identifier",
    },
    "onewire12_romcode": {
        "name": "OneWire-ROM-Code 12",
        "translation_key": "onewire12_romcode",
        "icon": "mdi:identifier",
    },
}

WATER_CHEM_SENSORS = {
    "pH_value": {"name": "pH-Wert", "translation_key": "ph_value", "icon": "mdi:ph"},
    "orp_value": {
        "name": "ORP-Wert",
        "translation_key": "orp_value",
        "icon": "mdi:lightning-bolt-circle",
    },
    "pot_value": {
        "name": "Chlorgehalt",
        "translation_key": "pot_value",
        "icon": "mdi:water-plus",
    },
}

ANALOG_SENSORS = {
    "ADC1_value": {
        "name": "Filterdruck",
        "translation_key": "adc1_value",
        "icon": "mdi:gauge",
    },
    "ADC2_value": {
        "name": "Ausgleichstank",
        "translation_key": "adc2_value",
        "icon": "mdi:water-sync",
    },
    "ADC3_value": {
        "name": "Durchflussmesser (4-20mA)",
        "translation_key": "adc3_value",
        "icon": "mdi:swap-horizontal",
    },
    "ADC4_value": {
        "name": "Analogsensor 4 (4-20mA)",
        "translation_key": "adc4_value",
        "icon": "mdi:gauge",
    },
    "ADC5_value": {
        "name": "Analogsensor 5 (0-10V)",
        "translation_key": "adc5_value",
        "icon": "mdi:sine-wave",
    },
    "IMP1_value": {
        "name": "Dosiereingang",
        "translation_key": "imp1_value",
        "icon": "mdi:pipe-valve",
    },
    "IMP2_value": {
        "name": "Pumpendurchfluss",
        "translation_key": "imp2_value",
        "icon": "mdi:water-pump",
    },
}

SYSTEM_SENSORS = {
    # Keys match exactly what READINGS object exposes in getReadings response
    # (verified against firmware source generateReadings.js)
    "SYSTEM_cpu_temperature": {
        "name": "CPU-Temperatur",
        "translation_key": "system_cpu_temperature",
        "icon": "mdi:thermometer-alert",
    },
    "SYSTEM_carrier_cpu_temperature": {
        "name": "Träger-CPU-Temperatur",
        "translation_key": "system_carrier_cpu_temperature",
        "icon": "mdi:motherboard",
    },
    "SYSTEM_memoryusage": {
        "name": "Speichernutzung",
        "translation_key": "system_memoryusage",
        "icon": "mdi:memory",
    },
    "SYSTEM_dosagemodule_cpu_temperature": {
        "name": "Dosier-Modul CPU-Temperatur",
        "translation_key": "system_dosagemodule_cpu_temperature",
        "icon": "mdi:memory-lan",
    },
    "CPU_UPTIME": {
        "name": "Betriebszeit des Geräts",
        "translation_key": "cpu_uptime",
        "icon": "mdi:timer-outline",
    },
    "LOAD_AVG": {
        "name": "CPU-Auslastung",
        "translation_key": "load_avg",
        "icon": "mdi:speedometer",
    },
    "pump_rs485_pwr": {
        "name": "RS485-Pumpenleistung",
        "translation_key": "pump_rs485_pwr",
        "icon": "mdi:lightning-bolt",
    },
    **{
        f"DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH{k}": {
            "name": f"DI-Regel {k} verbleibende Zeit",
            "translation_key": f"di_rule_{k}_stopwatch",
            "icon": "mdi:timer-sand",
        }
        for k in range(1, 9)
    },
}

STATUS_SENSORS = {
    "PUMP": {"name": "Pumpenstatus", "translation_key": "pump", "icon": "mdi:pump"},
    "HEATER": {
        "name": "Heizerstatus",
        "translation_key": "heater",
        "icon": "mdi:radiator",
    },
    "SOLAR": {
        "name": "Solarstatus",
        "translation_key": "solar",
        "icon": "mdi:solar-power",
    },
    "BACKWASH": {
        "name": "Rückspülstatus",
        "translation_key": "backwash",
        "icon": "mdi:autorenew",
    },
    "BACKWASHRINSE": {
        "name": "Nachspülstatus",
        "translation_key": "backwashrinse",
        "icon": "mdi:water-opacity",
    },
    "LIGHT": {
        "name": "Beleuchtungsstatus",
        "translation_key": "light",
        "icon": "mdi:lightbulb",
    },
    "REFILL": {
        "name": "Nachfüllstatus",
        "translation_key": "refill",
        "icon": "mdi:water",
    },
    "ECO": {
        "name": "Eco-Modus Status",
        "translation_key": "eco",
        "icon": "mdi:leaf",
    },
    "PVSURPLUS": {
        "name": "PV-Überschuss Status",
        "translation_key": "pvsurplus",
        "icon": "mdi:solar-power",
    },
    "FW": {
        "name": "Firmware-Version",
        "translation_key": "fw",
        "icon": "mdi:package-variant",
    },
}

DOSING_STATE_SENSORS = {
    "DOS_1_CL_STATE": {
        "name": "Chlordosier-Status",
        "translation_key": "dos_1_cl_state",
        "icon": "mdi:flask-outline",
    },
    "DOS_2_ELO_STATE": {
        "name": "Elektrolysestatus",
        "translation_key": "dos_2_elo_state",
        "icon": "mdi:lightning-bolt",
    },
    "DOS_4_PHM_STATE": {
        "name": "pH--Dosier-Status",
        "translation_key": "dos_4_phm_state",
        "icon": "mdi:flask-minus",
    },
    "DOS_5_PHP_STATE": {
        "name": "pH+-Dosier-Status",
        "translation_key": "dos_5_php_state",
        "icon": "mdi:flask-plus",
    },
    "DOS_6_FLOC_STATE": {
        "name": "Flockungsstatus",
        "translation_key": "dos_6_floc_state",
        "icon": "mdi:water",
    },
}

# Extra diagnostic sensors that surface useful controller state previously
# dropped on the floor.  Source: shm/READINGS.json snapshot (fw 1.0.9).
EXTRA_DIAGNOSTIC_SENSORS = {
    # Last error code pushed by the controller (kept as raw int).
    "last_error_id": {
        "name": "Letzte Fehler-ID",
        "translation_key": "last_error_id",
        "icon": "mdi:alert-circle-outline",
        "entity_category": "diagnostic",
    },
    # Electrolysis cell polarity (0 or 1) – flips regularly to prevent
    # scaling; useful for lifetime tracking.
    "DOS_2_CURRENT_POLARITY": {
        "name": "Elektrolyse-Polarität",
        "translation_key": "dos_2_current_polarity",
        "icon": "mdi:battery-positive",
        "entity_category": "diagnostic",
    },
    # OmniTronic multi-port valve state string (e.g. "OK",
    # "BLOCKED_BY_Z1Z2") and motion flag.
    "BACKWASH_OMNI_STATE": {
        "name": "OmniTronic-Ventilstatus",
        "translation_key": "backwash_omni_state",
        "icon": "mdi:valve",
        "entity_category": "diagnostic",
    },
    "BACKWASH_OMNI_MOVING": {
        "name": "OmniTronic bewegt sich",
        "translation_key": "backwash_omni_moving",
        "icon": "mdi:arrow-oscillating",
        "entity_category": "diagnostic",
    },
    # Separate "last run" timestamps for auto-triggered vs manually
    # triggered backwash – useful to detect missed cycles.
    "BACKWASH_LAST_AUTO_RUN": {
        "name": "Letzte automatische Rückspülung",
        "translation_key": "backwash_last_auto_run",
        "icon": "mdi:clock-time-twelve",
        "entity_category": "diagnostic",
    },
    "BACKWASH_LAST_MANUAL_RUN": {
        "name": "Letzte manuelle Rückspülung",
        "translation_key": "backwash_last_manual_run",
        "icon": "mdi:hand-clock",
        "entity_category": "diagnostic",
    },
    # Remaining-range strings delivered by the controller for each dosing
    # channel (e.g. ">99d").  No unit – it's already formatted.
    **{
        f"DOS_{prefix}_REMAINING_RANGE": {
            "name": f"{label} verbleibende Reichweite",
            "translation_key": f"{prefix.lower()}_remaining_range",
            "icon": "mdi:gauge",
            "entity_category": "diagnostic",
        }
        for prefix, label in (
            ("1_CL", "Chlor"),
            ("2_ELO", "Elektrolyse"),
            ("4_PHM", "pH-"),
            ("5_PHP", "pH+"),
            ("6_FLOC", "Flockungsmittel"),
        )
    },
}

# Analog and temperature switching-rule state sensors.
# Source: shm/ANALOGRULE_STATE.states + shm/TEMPRULE_STATE.states (fw 1.0.9).
# Each rule is a 0/1 active flag (1 = rule currently triggered and driving an
# output).  Mirrors the existing DIGITALINPUTRULE_STATE handling.
ANALOG_RULE_SENSORS = {
    f"ANALOGRULE_{i}": {
        "name": f"Analogregel {i}",
        "translation_key": f"analogrule_{i}",
        "icon": "mdi:chart-line",
        "entity_category": "diagnostic",
    }
    for i in range(1, 9)
}

TEMP_RULE_SENSORS = {
    f"TEMPRULE_{i}": {
        "name": f"Temperaturregel {i}",
        "translation_key": f"temprule_{i}",
        "icon": "mdi:thermometer-lines",
        "entity_category": "diagnostic",
    }
    for i in range(1, 9)
}

RUNTIME_SENSORS = {
    "PUMP_RUNTIME": {
        "name": "Pumpenlaufzeit heute",
        "translation_key": "pump_runtime",
        "icon": "mdi:clock-outline",
    },
    "SOLAR_RUNTIME": {
        "name": "Solaranlage-Laufzeit heute",
        "translation_key": "solar_runtime",
        "icon": "mdi:clock-outline",
    },
    "HEATER_RUNTIME": {
        "name": "Heizer-Laufzeit heute",
        "translation_key": "heater_runtime",
        "icon": "mdi:clock-outline",
    },
    "LIGHT_RUNTIME": {
        "name": "Beleuchtungs-Laufzeit heute",
        "translation_key": "light_runtime",
        "icon": "mdi:clock-outline",
    },
    "BACKWASH_RUNTIME": {
        "name": "Rückspül-Laufzeit",
        "translation_key": "backwash_runtime",
        "icon": "mdi:clock-outline",
    },
    "BACKWASHRINSE_RUNTIME": {
        "name": "Nachspül-Laufzeit",
        "translation_key": "backwashrinse_runtime",
        "icon": "mdi:clock-outline",
    },
    "ECO_RUNTIME": {
        "name": "Eco-Modus Laufzeit",
        "translation_key": "eco_runtime",
        "icon": "mdi:clock-outline",
    },
    "DOS_1_CL_RUNTIME": {
        "name": "Chlordosier-Laufzeit",
        "translation_key": "dos_1_cl_runtime",
        "icon": "mdi:clock-outline",
    },
    "DOS_2_ELO_RUNTIME": {
        "name": "Elektrolyse-Laufzeit",
        "translation_key": "dos_2_elo_runtime",
        "icon": "mdi:clock-outline",
    },
    "DOS_3_ELO_REV_RUNTIME": {
        "name": "Elektrolyse Umkehr-Laufzeit",
        "translation_key": "dos_3_elo_rev_runtime",
        "icon": "mdi:clock-outline",
    },
    "DOS_4_PHM_RUNTIME": {
        "name": "pH--Dosier-Laufzeit",
        "translation_key": "dos_4_phm_runtime",
        "icon": "mdi:clock-outline",
    },
    "DOS_5_PHP_RUNTIME": {
        "name": "pH+-Dosier-Laufzeit",
        "translation_key": "dos_5_php_runtime",
        "icon": "mdi:clock-outline",
    },
    "DOS_6_FLOC_RUNTIME": {
        "name": "Flockung-Laufzeit",
        "translation_key": "dos_6_floc_runtime",
        "icon": "mdi:clock-outline",
    },
    "REFILL_RUNTIME": {
        "name": "Nachfüll-Laufzeit",
        "translation_key": "refill_runtime",
        "icon": "mdi:clock-outline",
    },
    # Extension relay runtimes (EXT1/EXT2 modules)
    **{f"EXT{i}_{j}_RUNTIME": {
        "name": f"Erweiterung {i} Relais {j} Laufzeit",
        "translation_key": f"ext{i}_{j}_runtime",
        "icon": "mdi:clock-outline",
    } for i in (1, 2) for j in range(1, 9)},
    # OMNI module runtimes
    **{f"OMNI_DC{i}_RUNTIME": {
        "name": f"OMNI-Gleichstrommotor {i} Laufzeit",
        "translation_key": f"omni_dc{i}_runtime",
        "icon": "mdi:clock-outline",
    } for i in range(6)},
    # Pump RPM level runtimes
    **{f"PUMP_RPM_{i}_RUNTIME": {
        "name": f"Pumpe RPM-Stufe {i} Laufzeit",
        "translation_key": f"pump_rpm_{i}_runtime",
        "icon": "mdi:clock-outline",
    } for i in range(4)},
}

DOSING_STATS_SENSORS = {
    "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": {
        "name": "Tägliche Chlordosierung",
        "translation_key": "dos_1_cl_daily",
        "icon": "mdi:beaker",
    },
    "DOS_2_ELO_DAILY_DOSING_AMOUNT_ML": {
        "name": "Tägliche Elektrolysedosierung",
        "translation_key": "dos_2_elo_daily",
        "icon": "mdi:lightning-bolt",
    },
    "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": {
        "name": "Tägliche pH--Dosierung",
        "translation_key": "dos_4_phm_daily",
        "icon": "mdi:beaker-minus",
    },
    "DOS_5_PHP_DAILY_DOSING_AMOUNT_ML": {
        "name": "Tägliche pH+-Dosierung",
        "translation_key": "dos_5_php_daily",
        "icon": "mdi:beaker-plus",
    },
    "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": {
        "name": "Tägliche Flockungsdosierung",
        "translation_key": "dos_6_floc_daily",
        "icon": "mdi:beaker-outline",
    },
    "DOS_1_CL_TOTAL_CAN_AMOUNT_ML": {
        "name": "Chlorbehälter-Volumen",
        "translation_key": "dos_1_cl_total_can",
        "icon": "mdi:beaker",
    },
    "DOS_2_ELO_TOTAL_CAN_AMOUNT_ML": {
        "name": "Elektrolysebehälter-Volumen",
        "translation_key": "dos_2_elo_total_can",
        "icon": "mdi:lightning-bolt",
    },
    "DOS_4_PHM_TOTAL_CAN_AMOUNT_ML": {
        "name": "pH--Behälter-Volumen",
        "translation_key": "dos_4_phm_total_can",
        "icon": "mdi:beaker-minus",
    },
    "DOS_5_PHP_TOTAL_CAN_AMOUNT_ML": {
        "name": "pH+-Behälter-Volumen",
        "translation_key": "dos_5_php_total_can",
        "icon": "mdi:beaker-plus",
    },
    "DOS_6_FLOC_TOTAL_CAN_AMOUNT_ML": {
        "name": "Flockungsmittel-Behälter-Volumen",
        "translation_key": "dos_6_floc_total_can",
        "icon": "mdi:beaker-outline",
    },
}

COMPOSITE_STATE_SENSORS = {
    "PUMPSTATE": {
        "name": "Pumpen-Detailstatus",
        "translation_key": "pumpstate",
        "icon": "mdi:water-pump",
    },
    "HEATERSTATE": {
        "name": "Heizer-Detailstatus",
        "translation_key": "heaterstate",
        "icon": "mdi:radiator",
    },
    "SOLARSTATE": {
        "name": "Solar-Detailstatus",
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
    "SYSTEM_cpu_temperature": "°C",
    "SYSTEM_carrier_cpu_temperature": "°C",
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
    # RS485 pump power consumption
    "pump_rs485_pwr": "W",
    # Dosing Statistics — daily consumption
    "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "ml",
    "DOS_2_ELO_DAILY_DOSING_AMOUNT_ML": "ml",
    "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "ml",
    "DOS_5_PHP_DAILY_DOSING_AMOUNT_ML": "ml",
    "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": "ml",
    # Dosing Statistics — remaining can amount
    "DOS_1_CL_TOTAL_CAN_AMOUNT_ML": "ml",
    "DOS_2_ELO_TOTAL_CAN_AMOUNT_ML": "ml",
    "DOS_4_PHM_TOTAL_CAN_AMOUNT_ML": "ml",
    "DOS_5_PHP_TOTAL_CAN_AMOUNT_ML": "ml",
    "DOS_6_FLOC_TOTAL_CAN_AMOUNT_ML": "ml",
    # DI-Rule Stopwatch — remaining timer in seconds
    **{f"DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH{k}": "s" for k in range(1, 9)},
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
    # Extra diagnostic sensors (no meaningful unit)
    "last_error_id",
    "DOS_2_CURRENT_POLARITY",
    "BACKWASH_OMNI_STATE",
    "BACKWASH_OMNI_MOVING",
    "BACKWASH_LAST_AUTO_RUN",
    "BACKWASH_LAST_MANUAL_RUN",
    *(f"DOS_{p}_REMAINING_RANGE" for p in ("1_CL", "2_ELO", "4_PHM", "5_PHP", "6_FLOC")),
    # Analog/Temp rule state flags (0/1)
    *(f"ANALOGRULE_{i}" for i in range(1, 9)),
    *(f"TEMPRULE_{i}" for i in range(1, 9)),
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
    "DOS_2_ELO_DAILY_DOSING_AMOUNT_ML": "chlorine_control",
    "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "ph_control",
    "DOS_5_PHP_DAILY_DOSING_AMOUNT_ML": "ph_control",
    "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": "flocculation",
    "DOS_1_CL_TOTAL_CAN_AMOUNT_ML": "chlorine_control",
    "DOS_2_ELO_TOTAL_CAN_AMOUNT_ML": "chlorine_control",
    "DOS_4_PHM_TOTAL_CAN_AMOUNT_ML": "ph_control",
    "DOS_5_PHP_TOTAL_CAN_AMOUNT_ML": "ph_control",
    "DOS_6_FLOC_TOTAL_CAN_AMOUNT_ML": "flocculation",
    "pump_rs485_pwr": "filter_control",
}
