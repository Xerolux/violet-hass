# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Mappings for Violet Pool Controller error codes with German translations."""

from __future__ import annotations

from dataclasses import dataclass

# Error types
ERROR_TYPE_MESSAGE = "MESSAGE"
ERROR_TYPE_ALERT = "ALERT"
ERROR_TYPE_WARNING = "WARNING"
ERROR_TYPE_REMINDER = "REMINDER"

# Severity levels
SEVERITY_INFO = "info"
SEVERITY_WARNING = "warning"
SEVERITY_CRITICAL = "critical"


@dataclass(frozen=True)
class ErrorCodeEntry:
    """Single error code definition with translations."""

    code: str
    error_type: str
    subject_en: str
    subject_de: str
    severity: str
    description_en: str
    description_de: str
    blocking: str | None = None

    def to_dict(self, german: bool = False) -> dict[str, str]:
        """Convert to dictionary for legacy compatibility."""
        return {
            "type": self.error_type,
            "subject": self.subject_de if german else self.subject_en,
            "severity": self.severity,
            "description": self.description_de if german else self.description_en,
        }


# Complete Error Code Database with German translations
_ERROR_DATABASE: list[ErrorCodeEntry] = [
    # System & Network Errors (0000-0009)
    ErrorCodeEntry(
        "0",
        ERROR_TYPE_MESSAGE,
        "Test message",
        "Testnachricht",
        SEVERITY_INFO,
        "Test message from the controller.",
        "Testnachricht vom Controller.",
    ),
    ErrorCodeEntry(
        "1",
        ERROR_TYPE_MESSAGE,
        "Status message",
        "Statusmeldung",
        SEVERITY_INFO,
        "Status message from the controller.",
        "Statusmeldung vom Controller.",
    ),
    ErrorCodeEntry(
        "2",
        ERROR_TYPE_ALERT,
        "Hardware problem (COM link to carrier faulty)",
        "Hardware-Problem (COM-Verbindung zur Trägerplatine fehlerhaft)",
        SEVERITY_CRITICAL,
        "Communication link to the carrier board is faulty.",
        "Die COM-Verbindung zur Trägerplatine ist fehlerhaft.",
    ),
    ErrorCodeEntry(
        "3",
        ERROR_TYPE_REMINDER,
        "Happy Birthday",
        "Herzlichen Glückwunsch zum Geburtstag",
        SEVERITY_INFO,
        "Birthday greeting from the system.",
        "Geburtstagsglückwunsch vom System.",
    ),
    ErrorCodeEntry(
        "8",
        ERROR_TYPE_WARNING,
        "CPU temperature high",
        "CPU-Temperatur hoch",
        SEVERITY_WARNING,
        "The main processor temperature is approaching the limit.",
        "Die Hauptprozessortemperatur nähert sich dem Grenzwert.",
    ),
    ErrorCodeEntry(
        "9",
        ERROR_TYPE_ALERT,
        "CPU temperature too high",
        "CPU-Temperatur zu hoch",
        SEVERITY_CRITICAL,
        "The CPU temperature is significantly above the permissible value.",
        "Die CPU-Temperatur liegt deutlich über dem zulässigen Wert.",
    ),
    # Update Messages (10-12)
    ErrorCodeEntry(
        "10",
        ERROR_TYPE_REMINDER,
        "Update available (Auto)",
        "Update verfügbar (Automatisch)",
        SEVERITY_INFO,
        "A software update will be automatically installed during the coming night.",
        "Ein Software-Update wird in der kommenden Nacht automatisch installiert.",
    ),
    ErrorCodeEntry(
        "11",
        ERROR_TYPE_REMINDER,
        "Update available (Confirmation required)",
        "Update verfügbar (Bestätigung erforderlich)",
        SEVERITY_INFO,
        "A new software update requires manual confirmation.",
        "Ein neues Software-Update erfordert manuelle Bestätigung.",
    ),
    ErrorCodeEntry(
        "12",
        ERROR_TYPE_REMINDER,
        "Update available (Manual)",
        "Update verfügbar (Manuell)",
        SEVERITY_INFO,
        "A software update is available and must be triggered manually.",
        "Ein Software-Update ist verfügbar und muss manuell ausgelöst werden.",
    ),
    # Filter & Pressure Errors (20-31)
    ErrorCodeEntry(
        "20",
        ERROR_TYPE_ALERT,
        "Filter pressure too low",
        "Filterdruck zu niedrig",
        SEVERITY_CRITICAL,
        "The filter pump remains deactivated until the error is resolved.",
        "Die Filterpumpe bleibt deaktiviert, bis der Fehler behoben ist.",
    ),
    ErrorCodeEntry(
        "21",
        ERROR_TYPE_ALERT,
        "Filter pressure too high",
        "Filterdruck zu hoch",
        SEVERITY_CRITICAL,
        "The filter pump remains deactivated until the error is resolved.",
        "Die Filterpumpe bleibt deaktiviert, bis der Fehler behoben ist.",
    ),
    ErrorCodeEntry(
        "22",
        ERROR_TYPE_WARNING,
        "Measuring water inflow missing",
        "Messwasserzufluss fehlt",
        SEVERITY_WARNING,
        "Inflow to the electrodes is too low or absent.",
        "Der Wasserzufluss zu den Elektroden ist zu niedrig oder fehlt.",
    ),
    ErrorCodeEntry(
        "23",
        ERROR_TYPE_WARNING,
        "Measuring water inflow too high",
        "Messwasserzufluss zu hoch",
        SEVERITY_WARNING,
        "Inflow to the electrodes exceeds the limit.",
        "Der Wasserzufluss zu den Elektroden überschreitet das Limit.",
    ),
    ErrorCodeEntry(
        "24",
        ERROR_TYPE_ALERT,
        "Circulation missing",
        "Zirkulation fehlt",
        SEVERITY_CRITICAL,
        "The filter pump has been deactivated until circulation is restored.",
        "Die Filterpumpe wurde deaktiviert, bis die Zirkulation wiederhergestellt ist.",
    ),
    ErrorCodeEntry(
        "25",
        ERROR_TYPE_ALERT,
        "Circulation too high",
        "Zirkulation zu hoch",
        SEVERITY_CRITICAL,
        "The filter pump has been deactivated until circulation normalizes.",
        "Die Filterpumpe wurde deaktiviert, bis die Zirkulation normalisiert ist.",
    ),
    ErrorCodeEntry(
        "26",
        ERROR_TYPE_ALERT,
        "Frost protection filter pump unavailable",
        "Frostschutz Filterpumpe nicht verfügbar",
        SEVERITY_CRITICAL,
        "Temperature sensor error prevents the pump frost protection function.",
        "Temperatursensorfehler verhindert die Frostschutsfunktion der Pumpe.",
    ),
    ErrorCodeEntry(
        "27",
        ERROR_TYPE_ALERT,
        "Frost protection absorber unavailable",
        "Frostschutz Absorber nicht verfügbar",
        SEVERITY_CRITICAL,
        "Temperature sensor error prevents the absorber frost protection function.",
        "Temperatursensorfehler verhindert die Frostschutsfunktion des Absorbers.",
    ),
    # Heat Exchanger Errors (30-31)
    ErrorCodeEntry(
        "30",
        ERROR_TYPE_WARNING,
        "Heat exchanger temperature high",
        "Wärmetauscher-Temperatur hoch",
        SEVERITY_WARNING,
        "The heat exchanger has exceeded the limit.",
        "Der Wärmetauscher hat das Limit überschritten.",
    ),
    ErrorCodeEntry(
        "31",
        ERROR_TYPE_ALERT,
        "Overheat protection unavailable",
        "Übertemperaturschutz nicht verfügbar",
        SEVERITY_CRITICAL,
        "Temperature sensor error prevents overheat protection.",
        "Temperatursensorfehler verhindert Übertemperaturschutz.",
    ),
    # Backwash Errors (40-49)
    ErrorCodeEntry(
        "40",
        ERROR_TYPE_WARNING,
        "Backwash skipped",
        "Rückspülung übersprungen",
        SEVERITY_WARNING,
        "The scheduled backwash could not be performed.",
        "Die geplante Rückspülung konnte nicht durchgeführt werden.",
    ),
    ErrorCodeEntry(
        "41",
        ERROR_TYPE_MESSAGE,
        "Refill before backwash failed",
        "Nachfüllung vor Rückspülung fehlgeschlagen",
        SEVERITY_INFO,
        "The minimum fill level was not reached in time.",
        "Der minimale Füllstand wurde nicht rechtzeitig erreicht.",
    ),
    ErrorCodeEntry(
        "42",
        ERROR_TYPE_MESSAGE,
        "Refill not possible",
        "Nachfüllung nicht möglich",
        SEVERITY_INFO,
        "Refill valve is locked or manually switched off.",
        "Nachfüllventil ist gesperrt oder manuell ausgeschaltet.",
    ),
    ErrorCodeEntry(
        "45",
        ERROR_TYPE_ALERT,
        "Omnitronic no feedback (Backwash)",
        "Omnitronic keine Rückmeldung (Rückspülung)",
        SEVERITY_CRITICAL,
        "Actuator has not reached the backwash position.",
        "Aktuator hat die Rückspülposition nicht erreicht.",
    ),
    ErrorCodeEntry(
        "46",
        ERROR_TYPE_ALERT,
        "Omnitronic no feedback (Rinse)",
        "Omnitronic keine Rückmeldung (Spülung)",
        SEVERITY_CRITICAL,
        "Actuator has not reached the rinse position.",
        "Aktuator hat die Spülposition nicht erreicht.",
    ),
    ErrorCodeEntry(
        "47",
        ERROR_TYPE_ALERT,
        "Omni actuator position not reached",
        "Omni-Aktuatorposition nicht erreicht",
        SEVERITY_CRITICAL,
        "The actuator is not reporting position feedback.",
        "Der Aktuator meldet keine Positionsrückmeldung.",
    ),
    ErrorCodeEntry(
        "49",
        ERROR_TYPE_ALERT,
        "Omnitronic feedback contact open",
        "Omnitronic-Rückmeldungskontakt offen",
        SEVERITY_CRITICAL,
        "Filter pump remains deactivated until the contact is closed.",
        "Filterpumpe bleibt deaktiviert, bis der Kontakt geschlossen ist.",
    ),
    # Refill Errors (50-52)
    ErrorCodeEntry(
        "50",
        ERROR_TYPE_ALERT,
        "Water refill safety time exceeded",
        "Nachfüll-Sicherheitszeit überschritten",
        SEVERITY_CRITICAL,
        "Float switch has not switched in time.",
        "Schwimmerschalter hat nicht rechtzeitig geschaltet.",
    ),
    ErrorCodeEntry(
        "51",
        ERROR_TYPE_ALERT,
        "Water refill upper float",
        "Nachfüllung oberer Schwimmer",
        SEVERITY_CRITICAL,
        "Upper float switch has not responded.",
        "Oberer Schwimmerschalter hat nicht reagiert.",
    ),
    ErrorCodeEntry(
        "52",
        ERROR_TYPE_ALERT,
        "Water refill lower float",
        "Nachfüllung unterer Schwimmer",
        SEVERITY_CRITICAL,
        "Lower float switch has not switched back.",
        "Unterer Schwimmerschalter hat nicht zurückgeschaltet.",
    ),
    # Overflow Tank Errors (60-62)
    ErrorCodeEntry(
        "60",
        ERROR_TYPE_ALERT,
        "Overflow tank refill failed",
        "Überlauftank-Nachfüllung fehlgeschlagen",
        SEVERITY_CRITICAL,
        "Upper fill level could not be reached.",
        "Der obere Füllstand konnte nicht erreicht werden.",
    ),
    ErrorCodeEntry(
        "61",
        ERROR_TYPE_WARNING,
        "Overflow tank dry run",
        "Überlauftank Trockenfahrt",
        SEVERITY_WARNING,
        "Dry run protection of the filter pump triggered.",
        "Trockenfahrtschutz der Filterpumpe ausgelöst.",
    ),
    ErrorCodeEntry(
        "62",
        ERROR_TYPE_WARNING,
        "Overflow tank level measurement faulty",
        "Überlauftank-Füllstandsmessung fehlerhaft",
        SEVERITY_WARNING,
        "Level probe is faulty or not connected.",
        "Niveausonde ist fehlerhaft oder nicht angeschlossen.",
    ),
    # Temperature Rule Activations (71-78)
    *[
        ErrorCodeEntry(
            f"7{i}",
            ERROR_TYPE_WARNING,
            f"Temperature control program {i}",
            f"Temperaturregelungsprogramm {i}",
            SEVERITY_WARNING,
            f"Switching program {i} of the temperature control has been triggered.",
            f"Schaltprogramm {i} der Temperaturregelung wurde ausgelöst.",
        )
        for i in range(1, 9)
    ],
    # Analog Rule Activations (81-88)
    *[
        ErrorCodeEntry(
            f"8{i}",
            ERROR_TYPE_WARNING,
            f"Analog control program {i}",
            f"Analoges Steuerprogramm {i}",
            SEVERITY_WARNING,
            f"Switching program {i} of the analog controls has been triggered.",
            f"Schaltprogramm {i} der Analogsteuerung wurde ausgelöst.",
        )
        for i in range(1, 9)
    ],
    # Switching Rule Activations (91-98)
    *[
        ErrorCodeEntry(
            f"9{i}",
            ERROR_TYPE_WARNING,
            f"Switching rule program {i}",
            f"Schalt-Regelprogramm {i}",
            SEVERITY_WARNING,
            f"Switching program {i} of the switching rules has been triggered.",
            f"Schaltprogramm {i} der Schaltregeln wurde ausgelöst.",
        )
        for i in range(1, 9)
    ],
    # Temperature Sensor Errors (101-112)
    *[
        ErrorCodeEntry(
            f"10{i}",
            ERROR_TYPE_WARNING,
            f"Temperature sensor {i} error",
            f"Temperatursensor {i} Fehler",
            SEVERITY_WARNING,
            f"Temperature sensor {i} is no longer detected.",
            f"Temperatursensor {i} wird nicht mehr erkannt.",
        )
        for i in range(1, 13)
    ],
    # Dosing Warnings (120-175)
    ErrorCodeEntry(
        "120",
        ERROR_TYPE_WARNING,
        "Chlorine dosing ORP limit",
        "Chlor-Dosierung ORP-Grenzwert",
        SEVERITY_WARNING,
        "ORP warning limit of chlorine dosing reached.",
        "ORP-Warngrenzwert der Chlor-Dosierung erreicht.",
    ),
    ErrorCodeEntry(
        "121",
        ERROR_TYPE_WARNING,
        "Chlorine dosing chlorine limit",
        "Chlor-Dosierung Chlor-Grenzwert",
        SEVERITY_WARNING,
        "Chlorine warning limit of chlorine dosing reached.",
        "Chlor-Warngrenzwert der Chlor-Dosierung erreicht.",
    ),
    ErrorCodeEntry(
        "122",
        ERROR_TYPE_WARNING,
        "Chlorine dosing max. daily output",
        "Chlor-Dosierung max. Tagesleistung",
        SEVERITY_WARNING,
        "Daily dosing output exceeded.",
        "Die tägliche Dosierleistung wurde überschritten.",
    ),
    ErrorCodeEntry(
        "123",
        ERROR_TYPE_WARNING,
        "Chlorine canister low",
        "Chlorbehälter niedrig",
        SEVERITY_WARNING,
        "Remaining contents of the chlorine canister is low.",
        "Der Restbestand des Chlorbehälters ist niedrig.",
    ),
    ErrorCodeEntry(
        "124",
        ERROR_TYPE_WARNING,
        "Chlorine canister empty",
        "Chlorbehälter leer",
        SEVERITY_WARNING,
        "The chlorine canister is empty.",
        "Der Chlorbehälter ist leer.",
    ),
    ErrorCodeEntry(
        "125",
        ERROR_TYPE_WARNING,
        "Chlorine canister empty detector",
        "Chlor-Behälter-Leerdetekt.",
        SEVERITY_WARNING,
        "Empty detection contact of the suction lance triggered.",
        "Leererkennung der Sauglanzenverbindung ausgelöst.",
    ),
    # Electrolysis Warnings (130-135)
    ErrorCodeEntry(
        "130",
        ERROR_TYPE_WARNING,
        "Electrolysis ORP limit",
        "Elektrolyse ORP-Grenzwert",
        SEVERITY_WARNING,
        "ORP warning limit of electrolysis reached.",
        "ORP-Warngrenzwert der Elektrolyse erreicht.",
    ),
    ErrorCodeEntry(
        "131",
        ERROR_TYPE_WARNING,
        "Electrolysis chlorine limit",
        "Elektrolyse Chlor-Grenzwert",
        SEVERITY_WARNING,
        "Chlorine warning limit of electrolysis reached.",
        "Chlor-Warngrenzwert der Elektrolyse erreicht.",
    ),
    ErrorCodeEntry(
        "132",
        ERROR_TYPE_WARNING,
        "Electrolysis max. daily production",
        "Elektrolyse max. Tagesproduktion",
        SEVERITY_WARNING,
        "Daily production output reached.",
        "Die tägliche Produktionsleistung wurde erreicht.",
    ),
    ErrorCodeEntry(
        "133",
        ERROR_TYPE_WARNING,
        "Electrolysis remaining runtime",
        "Elektrolyse-Restlaufzeit",
        SEVERITY_WARNING,
        "Remaining runtime warning of the electrolysis cell reached.",
        "Warngrenzwert für Restlaufzeit der Elektrolysezelle erreicht.",
    ),
    ErrorCodeEntry(
        "134",
        ERROR_TYPE_WARNING,
        "Electrolysis max. operating time",
        "Elektrolyse max. Betriebszeit",
        SEVERITY_WARNING,
        "Maximum total operating time of the electrolysis cell reached.",
        "Maximale Gesamtbetriebszeit der Elektrolysezelle erreicht.",
    ),
    ErrorCodeEntry(
        "135",
        ERROR_TYPE_WARNING,
        "Flow switch electrolysis",
        "Durchflusschalter Elektrolyse",
        SEVERITY_WARNING,
        "Flow switch of the electrolysis cell triggered.",
        "Durchflusschalter der Elektrolysezelle ausgelöst.",
    ),
    # H2O2 Warnings (142-145)
    ErrorCodeEntry(
        "142",
        ERROR_TYPE_WARNING,
        "H2O2 max. daily dosing output",
        "H2O2 max. Tagesdosis",
        SEVERITY_WARNING,
        "Maximum daily dosing output reached.",
        "Maximale tägliche Dosierleistung erreicht.",
    ),
    ErrorCodeEntry(
        "143",
        ERROR_TYPE_WARNING,
        "H2O2 canister low",
        "H2O2-Behälter niedrig",
        SEVERITY_WARNING,
        "Remaining contents of the H2O2 canister is low.",
        "Der Restbestand des H2O2-Behälters ist niedrig.",
    ),
    ErrorCodeEntry(
        "144",
        ERROR_TYPE_WARNING,
        "H2O2 canister empty",
        "H2O2-Behälter leer",
        SEVERITY_WARNING,
        "The H2O2 canister is empty.",
        "Der H2O2-Behälter ist leer.",
    ),
    ErrorCodeEntry(
        "145",
        ERROR_TYPE_WARNING,
        "Oxygen canister empty detector",
        "Sauerstoffbehälter-Leerdetekt.",
        SEVERITY_WARNING,
        "Empty detection contact of the suction lance triggered.",
        "Leererkennung der Sauglanzenverbindung ausgelöst.",
    ),
    # pH-Minus Warnings (150-155)
    ErrorCodeEntry(
        "150",
        ERROR_TYPE_WARNING,
        "pH-minus limit",
        "pH-Minus-Grenzwert",
        SEVERITY_WARNING,
        "Warning limits of pH-minus dosing reached.",
        "Warngrenzwerte der pH-Minus-Dosierung erreicht.",
    ),
    ErrorCodeEntry(
        "152",
        ERROR_TYPE_WARNING,
        "pH-minus max. daily dosing output",
        "pH-Minus max. Tagesdosis",
        SEVERITY_WARNING,
        "Daily dosing output exceeded.",
        "Die tägliche Dosierleistung wurde überschritten.",
    ),
    ErrorCodeEntry(
        "153",
        ERROR_TYPE_WARNING,
        "pH-minus canister low",
        "pH-Minus-Behälter niedrig",
        SEVERITY_WARNING,
        "Remaining contents of the pH-minus canister is low.",
        "Der Restbestand des pH-Minus-Behälters ist niedrig.",
    ),
    ErrorCodeEntry(
        "154",
        ERROR_TYPE_WARNING,
        "pH-minus canister empty",
        "pH-Minus-Behälter leer",
        SEVERITY_WARNING,
        "The pH-minus canister is empty.",
        "Der pH-Minus-Behälter ist leer.",
    ),
    ErrorCodeEntry(
        "155",
        ERROR_TYPE_WARNING,
        "pH-minus empty detection contact",
        "pH-Minus-Leerdetekt.",
        SEVERITY_WARNING,
        "Empty detection contact of the suction lance triggered.",
        "Leererkennung der Sauglanzenverbindung ausgelöst.",
    ),
    # pH-Plus Warnings (160-165)
    ErrorCodeEntry(
        "160",
        ERROR_TYPE_WARNING,
        "pH-plus limit",
        "pH-Plus-Grenzwert",
        SEVERITY_WARNING,
        "Warning limits of pH-plus dosing reached.",
        "Warngrenzwerte der pH-Plus-Dosierung erreicht.",
    ),
    ErrorCodeEntry(
        "162",
        ERROR_TYPE_WARNING,
        "pH-plus max. daily dosing output",
        "pH-Plus max. Tagesdosis",
        SEVERITY_WARNING,
        "Daily dosing output exceeded.",
        "Die tägliche Dosierleistung wurde überschritten.",
    ),
    ErrorCodeEntry(
        "163",
        ERROR_TYPE_WARNING,
        "pH-plus canister low",
        "pH-Plus-Behälter niedrig",
        SEVERITY_WARNING,
        "Remaining contents of the pH-plus canister is low.",
        "Der Restbestand des pH-Plus-Behälters ist niedrig.",
    ),
    ErrorCodeEntry(
        "164",
        ERROR_TYPE_WARNING,
        "pH-plus canister empty",
        "pH-Plus-Behälter leer",
        SEVERITY_WARNING,
        "The pH-plus canister is empty.",
        "Der pH-Plus-Behälter ist leer.",
    ),
    ErrorCodeEntry(
        "165",
        ERROR_TYPE_WARNING,
        "pH-plus empty detection contact",
        "pH-Plus-Leerdetekt.",
        SEVERITY_WARNING,
        "Empty detection contact of the suction lance triggered.",
        "Leererkennung der Sauglanzenverbindung ausgelöst.",
    ),
    # Flocculant Warnings (172-175)
    ErrorCodeEntry(
        "172",
        ERROR_TYPE_WARNING,
        "Flocculant max. daily dosing output",
        "Flockungsmittel max. Tagesdosis",
        SEVERITY_WARNING,
        "Daily dosing output of flocculant dosing reached.",
        "Die tägliche Dosierleistung für Flockungsmittel wurde erreicht.",
    ),
    ErrorCodeEntry(
        "173",
        ERROR_TYPE_WARNING,
        "Flocculant canister low",
        "Flockungsmittel-Behälter niedrig",
        SEVERITY_WARNING,
        "Remaining contents of the flocculant canister is low.",
        "Der Restbestand des Flockungsmittel-Behälters ist niedrig.",
    ),
    ErrorCodeEntry(
        "174",
        ERROR_TYPE_WARNING,
        "Flocculant canister empty",
        "Flockungsmittel-Behälter leer",
        SEVERITY_WARNING,
        "The flocculant canister is empty.",
        "Der Flockungsmittel-Behälter ist leer.",
    ),
    ErrorCodeEntry(
        "175",
        ERROR_TYPE_WARNING,
        "Flocculant empty detection contact",
        "Flockungsmittel-Leerdetekt.",
        SEVERITY_WARNING,
        "Empty detection contact of the suction lance triggered.",
        "Leererkennung der Sauglanzenverbindung ausgelöst.",
    ),
    # Calibration Reminders (180-182)
    ErrorCodeEntry(
        "180",
        ERROR_TYPE_REMINDER,
        "Calibrate pH electrode",
        "pH-Elektrode kalibrieren",
        SEVERITY_INFO,
        "Calibration of the pH electrode is due.",
        "Kalibrierung der pH-Elektrode ist fällig.",
    ),
    ErrorCodeEntry(
        "181",
        ERROR_TYPE_REMINDER,
        "Calibrate ORP electrode",
        "ORP-Elektrode kalibrieren",
        SEVERITY_INFO,
        "Calibration of the ORP electrode is due.",
        "Kalibrierung der ORP-Elektrode ist fällig.",
    ),
    ErrorCodeEntry(
        "182",
        ERROR_TYPE_REMINDER,
        "Calibrate chlorine electrode",
        "Chlor-Elektrode kalibrieren",
        SEVERITY_INFO,
        "Calibration of the chlorine electrode is due.",
        "Kalibrierung der Chlor-Elektrode ist fällig.",
    ),
    # Module Communication Errors (200-210)
    ErrorCodeEntry(
        "200",
        ERROR_TYPE_WARNING,
        "Dosing module disconnected",
        "Dosiermodul getrennt",
        SEVERITY_WARNING,
        "No communication link to the dosing module.",
        "Keine Kommunikationsverbindung zum Dosiermodul.",
    ),
    ErrorCodeEntry(
        "201",
        ERROR_TYPE_WARNING,
        "Dosing module communication lost",
        "Dosiermodul-Kommunikation unterbrochen",
        SEVERITY_WARNING,
        "Communication to the dosing module has been interrupted.",
        "Die Kommunikation zum Dosiermodul wurde unterbrochen.",
    ),
    ErrorCodeEntry(
        "203",
        ERROR_TYPE_WARNING,
        "Relay extension 1 disconnected",
        "Erweiterungsmodul 1 getrennt",
        SEVERITY_WARNING,
        "No communication link to relay extension 1.",
        "Keine Kommunikationsverbindung zu Erweiterungsmodul 1.",
    ),
    ErrorCodeEntry(
        "204",
        ERROR_TYPE_WARNING,
        "Relay extension 1 communication lost",
        "Erweiterungsmodul 1 Kommunikation unterbrochen",
        SEVERITY_WARNING,
        "Communication to relay extension 1 has been interrupted.",
        "Die Kommunikation zu Erweiterungsmodul 1 wurde unterbrochen.",
    ),
    ErrorCodeEntry(
        "206",
        ERROR_TYPE_WARNING,
        "Relay extension 2 disconnected",
        "Erweiterungsmodul 2 getrennt",
        SEVERITY_WARNING,
        "No communication link to relay extension 2.",
        "Keine Kommunikationsverbindung zu Erweiterungsmodul 2.",
    ),
    ErrorCodeEntry(
        "207",
        ERROR_TYPE_WARNING,
        "Relay extension 2 communication lost",
        "Erweiterungsmodul 2 Kommunikation unterbrochen",
        SEVERITY_WARNING,
        "Communication to relay extension 2 has been interrupted.",
        "Die Kommunikation zu Erweiterungsmodul 2 wurde unterbrochen.",
    ),
    ErrorCodeEntry(
        "209",
        ERROR_TYPE_ALERT,
        "Second dosing module detected",
        "Zweites Dosiermodul erkannt",
        SEVERITY_CRITICAL,
        "A second dosing module is being ignored.",
        "Ein zweites Dosiermodul wird ignoriert.",
    ),
    ErrorCodeEntry(
        "210",
        ERROR_TYPE_ALERT,
        "Incorrectly coded relay extension",
        "Falsch codiertes Erweiterungsmodul",
        SEVERITY_CRITICAL,
        "A second relay extension has the same coding.",
        "Ein zweites Erweiterungsmodul hat die gleiche Codierung.",
    ),
    # Timer Rule Activations (A1-A8)
    *[
        ErrorCodeEntry(
            f"A{i}",
            ERROR_TYPE_WARNING,
            f"Timer rule program {i}",
            f"Timer-Regelprogramm {i}",
            SEVERITY_WARNING,
            f"Timer program {i} has been activated.",
            f"Timer-Programm {i} wurde aktiviert.",
        )
        for i in range(1, 9)
    ],
]

# Build lookup dict
ERROR_CODES: dict[str, dict[str, str]] = {}
_CODE_ENTRIES: dict[str, ErrorCodeEntry] = {}

for entry in _ERROR_DATABASE:
    ERROR_CODES[entry.code] = entry.to_dict(german=False)
    _CODE_ENTRIES[entry.code] = entry


def get_error_info(code: str, german: bool = False) -> dict[str, str]:
    """Return error information for a given code.

    Args:
        code: Error code as string.
        german: Return German translations if True.

    Returns:
        Dictionary with error information.
    """
    code_str = str(code).strip()

    if code_str in _CODE_ENTRIES:
        return _CODE_ENTRIES[code_str].to_dict(german=german)

    return {
        "type": "UNKNOWN",
        "subject": (
            f"Unbekannter Code: {code_str}"
            if german
            else f"Unknown code: {code_str}"
        ),
        "severity": "info",
        "description": (
            "Keine Beschreibung verfügbar"
            if german
            else "No description available"
        ),
    }


def get_error_entry(code: str) -> ErrorCodeEntry | None:
    """Get complete error code entry.

    Args:
        code: Error code as string.

    Returns:
        ErrorCodeEntry or None if not found.
    """
    if code is None:
        return None
    return _CODE_ENTRIES.get(str(code).strip())
