"""Mappings for Violet Pool Controller error codes."""

from __future__ import annotations

from typing import Dict, List

# The dictionary below is intentionally focused on the most common error codes
# observed in production systems.  Unknown codes fall back to a generic
# response so the integration remains robust even when the controller ships a
# firmware with additional diagnostics.

ERROR_CODES: Dict[str, Dict[str, str]] = {
    "0": {
        "type": "MESSAGE",
        "subject": "Testnachricht",
        "severity": "info",
        "description": "Testnachricht von . Die Nachricht wurde am  um  ausgelöst und am  um  versendet.",
    },
    "1": {
        "type": "MESSAGE",
        "subject": "Statusnachricht",
        "severity": "info",
        "description": "Statusnachricht von .",
    },
    "2": {
        "type": "ALERT",
        "subject": "Hardwareproblem (COM-Link zum Carrier fehlerhaft)",
        "severity": "critical",
        "description": "Kommunikationsverbindung zum Carrier-Board fehlerhaft.",
    },
    "3": {
        "type": "REMINDER",
        "subject": "Happy Birthday",
        "severity": "info",
        "description": "Geburtstagsgruß des Systems.",
    },
    "8": {
        "type": "WARNING",
        "subject": "CPU-Temperatur hoch",
        "severity": "warning",
        "description": "Die Temperatur des Haupt-Prozessors nähert sich dem Grenzwert.",
    },
    "9": {
        "type": "ALERT",
        "subject": "CPU-Temperatur zu hoch",
        "severity": "critical",
        "description": "Die CPU-Temperatur liegt deutlich über dem zulässigen Wert.",
    },
    "10": {
        "type": "REMINDER",
        "subject": "Update verfügbar (Auto)",
        "severity": "info",
        "description": "Ein Software-Update wird in der kommenden Nacht automatisch installiert.",
    },
    "11": {
        "type": "REMINDER",
        "subject": "Update verfügbar (Bestätigung erforderlich)",
        "severity": "info",
        "description": "Ein neues Software-Update erfordert eine manuelle Bestätigung.",
    },
    "12": {
        "type": "REMINDER",
        "subject": "Update verfügbar (Manuell)",
        "severity": "info",
        "description": "Ein Software-Update steht bereit und muss manuell ausgelöst werden.",
    },
    "20": {
        "type": "ALERT",
        "subject": "Filterdruck zu niedrig",
        "severity": "critical",
        "description": "Die Filterpumpe bleibt deaktiviert, bis der Fehler behoben ist.",
    },
    "21": {
        "type": "ALERT",
        "subject": "Filterdruck zu hoch",
        "severity": "critical",
        "description": "Die Filterpumpe bleibt deaktiviert, bis der Fehler behoben ist.",
    },
    "22": {
        "type": "WARNING",
        "subject": "Messwasser Anströmung fehlt",
        "severity": "warning",
        "description": "Anströmung an den Elektroden zu niedrig oder nicht vorhanden.",
    },
    "23": {
        "type": "WARNING",
        "subject": "Messwasser Anströmung zu hoch",
        "severity": "warning",
        "description": "Anströmung an den Elektroden überschreitet den Grenzwert.",
    },
    "24": {
        "type": "ALERT",
        "subject": "Zirkulation fehlt",
        "severity": "critical",
        "description": "Die Filterpumpe wurde deaktiviert, bis die Zirkulation wiederhergestellt ist.",
    },
    "25": {
        "type": "ALERT",
        "subject": "Zirkulation zu hoch",
        "severity": "critical",
        "description": "Die Filterpumpe wurde deaktiviert, bis die Zirkulation normalisiert ist.",
    },
    "26": {
        "type": "ALERT",
        "subject": "Frostschutz Filterpumpe nicht verfügbar",
        "severity": "critical",
        "description": "Temperatursensor-Fehler verhindert die Frostschutzfunktion der Pumpe.",
    },
    "27": {
        "type": "ALERT",
        "subject": "Frostschutz Absorber nicht verfügbar",
        "severity": "critical",
        "description": "Temperatursensor-Fehler verhindert die Frostschutzfunktion des Absorbers.",
    },
    "30": {
        "type": "WARNING",
        "subject": "Wärmetauscher Temperatur hoch",
        "severity": "warning",
        "description": "Der Wärmetauscher hat den Grenzwert überschritten.",
    },
    "31": {
        "type": "ALERT",
        "subject": "Übertemperatur-Schutz nicht verfügbar",
        "severity": "critical",
        "description": "Temperatursensor-Fehler verhindert den Übertemperatur-Schutz.",
    },
    "40": {
        "type": "WARNING",
        "subject": "Rückspülung ausgelassen",
        "severity": "warning",
        "description": "Die geplante Rückspülung konnte nicht durchgeführt werden.",
    },
    "41": {
        "type": "MESSAGE",
        "subject": "Nachspeisung vor Rückspülung fehlgeschlagen",
        "severity": "info",
        "description": "Der Mindestfüllstand wurde nicht rechtzeitig erreicht.",
    },
    "42": {
        "type": "MESSAGE",
        "subject": "Nachspeisung nicht möglich",
        "severity": "info",
        "description": "Nachspeiseventil gesperrt oder manuell ausgeschaltet.",
    },
    "45": {
        "type": "ALERT",
        "subject": "Omnitronic ohne Rückmeldung (Rückspülen)",
        "severity": "critical",
        "description": "Stellantrieb hat die Rückspülposition nicht erreicht.",
    },
    "46": {
        "type": "ALERT",
        "subject": "Omnitronic ohne Rückmeldung (Nachspülen)",
        "severity": "critical",
        "description": "Stellantrieb hat die Nachspülposition nicht erreicht.",
    },
    "47": {
        "type": "ALERT",
        "subject": "Omni-Stellantrieb Position nicht erreicht",
        "severity": "critical",
        "description": "Der Stellantrieb meldet keine Positions-Rückmeldung.",
    },
    "49": {
        "type": "ALERT",
        "subject": "Omnitronic Rückmeldekontakt offen",
        "severity": "critical",
        "description": "Filterpumpe bleibt deaktiviert, bis der Kontakt geschlossen ist.",
    },
    "50": {
        "type": "ALERT",
        "subject": "Wassernachspeisung Sicherheitszeit überschritten",
        "severity": "critical",
        "description": "Schwimmerschalter hat nicht rechtzeitig geschaltet.",
    },
    "51": {
        "type": "ALERT",
        "subject": "Wassernachspeisung oberer Schwimmer",
        "severity": "critical",
        "description": "Oberer Schwimmerschalter hat nicht reagiert.",
    },
    "52": {
        "type": "ALERT",
        "subject": "Wassernachspeisung unterer Schwimmer",
        "severity": "critical",
        "description": "Unterer Schwimmerschalter hat nicht zurückgeschaltet.",
    },
    "60": {
        "type": "ALERT",
        "subject": "Überlaufbehälter Nachspeisung fehlgeschlagen",
        "severity": "critical",
        "description": "Oberer Füllstand konnte nicht erreicht werden.",
    },
    "61": {
        "type": "WARNING",
        "subject": "Überlaufbehälter Trockenlauf",
        "severity": "warning",
        "description": "Trockenlaufschutz der Filterpumpe ausgelöst.",
    },
    "62": {
        "type": "WARNING",
        "subject": "Überlaufbehälter Pegelmessung fehlerhaft",
        "severity": "warning",
        "description": "Pegelsonde ist fehlerhaft oder nicht verbunden.",
    },
    "71": {
        "type": "WARNING",
        "subject": "Temperaturregelung Programm 1",
        "severity": "warning",
        "description": "Schaltprogramm 1 der Temperatursteuerung wurde ausgelöst.",
    },
    "72": {
        "type": "WARNING",
        "subject": "Temperaturregelung Programm 2",
        "severity": "warning",
        "description": "Schaltprogramm 2 der Temperatursteuerung wurde ausgelöst.",
    },
    "73": {
        "type": "WARNING",
        "subject": "Temperaturregelung Programm 3",
        "severity": "warning",
        "description": "Schaltprogramm 3 der Temperatursteuerung wurde ausgelöst.",
    },
    "74": {
        "type": "WARNING",
        "subject": "Temperaturregelung Programm 4",
        "severity": "warning",
        "description": "Schaltprogramm 4 der Temperatursteuerung wurde ausgelöst.",
    },
    "75": {
        "type": "MESSAGE",
        "subject": "Temperaturregelung Programm 5",
        "severity": "info",
        "description": "Schaltprogramm 5 der Temperatursteuerung wurde ausgelöst.",
    },
    "76": {
        "type": "WARNING",
        "subject": "Temperaturregelung Programm 6",
        "severity": "warning",
        "description": "Schaltprogramm 6 der Temperatursteuerung wurde ausgelöst.",
    },
    "77": {
        "type": "WARNING",
        "subject": "Temperaturregelung Programm 7",
        "severity": "warning",
        "description": "Schaltprogramm 7 der Temperatursteuerung wurde ausgelöst.",
    },
    "78": {
        "type": "WARNING",
        "subject": "Temperaturregelung Programm 8",
        "severity": "warning",
        "description": "Schaltprogramm 8 der Temperatursteuerung wurde ausgelöst.",
    },
    "81": {
        "type": "WARNING",
        "subject": "Analogregeln Programm 1",
        "severity": "warning",
        "description": "Schaltprogramm 1 der Analogregeln wurde ausgelöst.",
    },
    "82": {
        "type": "WARNING",
        "subject": "Analogregeln Programm 2",
        "severity": "warning",
        "description": "Schaltprogramm 2 der Analogregeln wurde ausgelöst.",
    },
    "83": {
        "type": "WARNING",
        "subject": "Analogregeln Programm 3",
        "severity": "warning",
        "description": "Schaltprogramm 3 der Analogregeln wurde ausgelöst.",
    },
    "84": {
        "type": "WARNING",
        "subject": "Analogregeln Programm 4",
        "severity": "warning",
        "description": "Schaltprogramm 4 der Analogregeln wurde ausgelöst.",
    },
    "85": {
        "type": "WARNING",
        "subject": "Analogregeln Programm 5",
        "severity": "warning",
        "description": "Schaltprogramm 5 der Analogregeln wurde ausgelöst.",
    },
    "86": {
        "type": "WARNING",
        "subject": "Analogregeln Programm 6",
        "severity": "warning",
        "description": "Schaltprogramm 6 der Analogregeln wurde ausgelöst.",
    },
    "87": {
        "type": "WARNING",
        "subject": "Analogregeln Programm 7",
        "severity": "warning",
        "description": "Schaltprogramm 7 der Analogregeln wurde ausgelöst.",
    },
    "88": {
        "type": "WARNING",
        "subject": "Analogregeln Programm 8",
        "severity": "warning",
        "description": "Schaltprogramm 8 der Analogregeln wurde ausgelöst.",
    },
    "91": {
        "type": "WARNING",
        "subject": "Schaltregel Programm 1",
        "severity": "warning",
        "description": "Schaltprogramm 1 der Schaltregeln wurde ausgelöst.",
    },
    "92": {
        "type": "WARNING",
        "subject": "Schaltregel Programm 2",
        "severity": "warning",
        "description": "Schaltprogramm 2 der Schaltregeln wurde ausgelöst.",
    },
    "93": {
        "type": "WARNING",
        "subject": "Schaltregel Programm 3",
        "severity": "warning",
        "description": "Schaltprogramm 3 der Schaltregeln wurde ausgelöst.",
    },
    "94": {
        "type": "WARNING",
        "subject": "Schaltregel Programm 4",
        "severity": "warning",
        "description": "Schaltprogramm 4 der Schaltregeln wurde ausgelöst.",
    },
    "95": {
        "type": "WARNING",
        "subject": "Schaltregel Programm 5",
        "severity": "warning",
        "description": "Schaltprogramm 5 der Schaltregeln wurde ausgelöst.",
    },
    "96": {
        "type": "WARNING",
        "subject": "Schaltregel Programm 6",
        "severity": "warning",
        "description": "Schaltprogramm 6 der Schaltregeln wurde ausgelöst.",
    },
    "97": {
        "type": "WARNING",
        "subject": "Schaltregel Programm 7",
        "severity": "warning",
        "description": "Schaltprogramm 7 der Schaltregeln wurde ausgelöst.",
    },
    "98": {
        "type": "WARNING",
        "subject": "Schaltregel Programm 8",
        "severity": "warning",
        "description": "Schaltprogramm 8 der Schaltregeln wurde ausgelöst.",
    },
    "101": {
        "type": "WARNING",
        "subject": "Temperatursensor 1 Fehler",
        "severity": "warning",
        "description": "Temperatursensor 1 wurde nicht mehr erkannt.",
    },
    "102": {
        "type": "WARNING",
        "subject": "Temperatursensor 2 Fehler",
        "severity": "warning",
        "description": "Temperatursensor 2 wurde nicht mehr erkannt.",
    },
    "103": {
        "type": "WARNING",
        "subject": "Temperatursensor 3 Fehler",
        "severity": "warning",
        "description": "Temperatursensor 3 wurde nicht mehr erkannt.",
    },
    "104": {
        "type": "WARNING",
        "subject": "Temperatursensor 4 Fehler",
        "severity": "warning",
        "description": "Temperatursensor 4 wurde nicht mehr erkannt.",
    },
    "105": {
        "type": "WARNING",
        "subject": "Temperatursensor 5 Fehler",
        "severity": "warning",
        "description": "Temperatursensor 5 wurde nicht mehr erkannt.",
    },
    "106": {
        "type": "WARNING",
        "subject": "Temperatursensor 6 Fehler",
        "severity": "warning",
        "description": "Temperatursensor 6 wurde nicht mehr erkannt.",
    },
    "107": {
        "type": "WARNING",
        "subject": "Temperatursensor 7 Fehler",
        "severity": "warning",
        "description": "Temperatursensor 7 wurde nicht mehr erkannt.",
    },
    "108": {
        "type": "WARNING",
        "subject": "Temperatursensor 8 Fehler",
        "severity": "warning",
        "description": "Temperatursensor 8 wurde nicht mehr erkannt.",
    },
    "109": {
        "type": "WARNING",
        "subject": "Temperatursensor 9 Fehler",
        "severity": "warning",
        "description": "Temperatursensor 9 wurde nicht mehr erkannt.",
    },
    "110": {
        "type": "WARNING",
        "subject": "Temperatursensor 10 Fehler",
        "severity": "warning",
        "description": "Temperatursensor 10 wurde nicht mehr erkannt.",
    },
    "111": {
        "type": "WARNING",
        "subject": "Temperatursensor 11 Fehler",
        "severity": "warning",
        "description": "Temperatursensor 11 wurde nicht mehr erkannt.",
    },
    "112": {
        "type": "WARNING",
        "subject": "Temperatursensor 12 Fehler",
        "severity": "warning",
        "description": "Temperatursensor 12 wurde nicht mehr erkannt.",
    },
    "120": {
        "type": "WARNING",
        "subject": "Chlor-Dosierung Redox Grenzwert",
        "severity": "warning",
        "description": "Redox-Warngrenze der Chlor-Dosierung erreicht.",
    },
    "121": {
        "type": "WARNING",
        "subject": "Chlor-Dosierung Chlor Grenzwert",
        "severity": "warning",
        "description": "Chlor-Warngrenze der Chlor-Dosierung erreicht.",
    },
    "122": {
        "type": "WARNING",
        "subject": "Chlor-Dosierung max. Tagesleistung",
        "severity": "warning",
        "description": "Tägliche Dosierleistung überschritten.",
    },
    "123": {
        "type": "WARNING",
        "subject": "Chlor-Kanister niedrig",
        "severity": "warning",
        "description": "Restinhalt des Chlor-Kanisters ist niedrig.",
    },
    "124": {
        "type": "WARNING",
        "subject": "Chlor-Kanister leer",
        "severity": "warning",
        "description": "Der Chlor-Kanister ist leer.",
    },
    "125": {
        "type": "WARNING",
        "subject": "Chlor-Kanister Leermelder",
        "severity": "warning",
        "description": "Leermeldekontakt der Sauglanze ausgelöst.",
    },
    "130": {
        "type": "WARNING",
        "subject": "Elektrolyse Redox Grenzwert",
        "severity": "warning",
        "description": "Redox-Warngrenze der Elektrolyse erreicht.",
    },
    "131": {
        "type": "WARNING",
        "subject": "Elektrolyse Chlor Grenzwert",
        "severity": "warning",
        "description": "Chlor-Warngrenze der Elektrolyse erreicht.",
    },
    "132": {
        "type": "WARNING",
        "subject": "Elektrolyse max. Tagesproduktion",
        "severity": "warning",
        "description": "Tägliche Produktionsleistung erreicht.",
    },
    "133": {
        "type": "WARNING",
        "subject": "Elektrolyse Restlaufzeit",
        "severity": "warning",
        "description": "Restlaufzeitwarnung der Elektrolysezelle erreicht.",
    },
    "134": {
        "type": "WARNING",
        "subject": "Elektrolyse max. Betriebszeit",
        "severity": "warning",
        "description": "Maximale Gesamtbetriebszeit der Elektrolysezelle erreicht.",
    },
    "135": {
        "type": "WARNING",
        "subject": "Durchflussschalter Elektrolyse",
        "severity": "warning",
        "description": "Durchflussschalter der Elektrolysezelle ausgelöst.",
    },
    "142": {
        "type": "WARNING",
        "subject": "H2O2 max. Tagesdosierleistung",
        "severity": "warning",
        "description": "Maximale Tagesdosierleistung erreicht.",
    },
    "143": {
        "type": "WARNING",
        "subject": "H2O2 Kanister niedrig",
        "severity": "warning",
        "description": "Restinhalt des H2O2-Kanisters ist niedrig.",
    },
    "144": {
        "type": "WARNING",
        "subject": "H2O2 Kanister leer",
        "severity": "warning",
        "description": "Der H2O2-Kanister ist leer.",
    },
    "145": {
        "type": "WARNING",
        "subject": "Sauerstoff-Kanister Leermelder",
        "severity": "warning",
        "description": "Leermeldekontakt der Sauglanze ausgelöst.",
    },
    "150": {
        "type": "WARNING",
        "subject": "pH-minus Grenzwert",
        "severity": "warning",
        "description": "Warngrenzen der pH-minus Dosierung erreicht.",
    },
    "152": {
        "type": "WARNING",
        "subject": "pH-minus max. Tagesdosierleistung",
        "severity": "warning",
        "description": "Tägliche Dosierleistung überschritten.",
    },
    "153": {
        "type": "WARNING",
        "subject": "pH-minus Kanister niedrig",
        "severity": "warning",
        "description": "Restinhalt des pH-minus Kanisters ist niedrig.",
    },
    "154": {
        "type": "WARNING",
        "subject": "pH-minus Kanister leer",
        "severity": "warning",
        "description": "Der pH-minus Kanister ist leer.",
    },
    "155": {
        "type": "WARNING",
        "subject": "pH-minus Leermeldekontakt",
        "severity": "warning",
        "description": "Leermeldekontakt der Sauglanze ausgelöst.",
    },
    "160": {
        "type": "WARNING",
        "subject": "pH-plus Grenzwert",
        "severity": "warning",
        "description": "Warngrenzen der pH-plus Dosierung erreicht.",
    },
    "162": {
        "type": "WARNING",
        "subject": "pH-plus max. Tagesdosierleistung",
        "severity": "warning",
        "description": "Tägliche Dosierleistung überschritten.",
    },
    "163": {
        "type": "WARNING",
        "subject": "pH-plus Kanister niedrig",
        "severity": "warning",
        "description": "Restinhalt des pH-plus Kanisters ist niedrig.",
    },
    "164": {
        "type": "WARNING",
        "subject": "pH-plus Kanister leer",
        "severity": "warning",
        "description": "Der pH-plus Kanister ist leer.",
    },
    "165": {
        "type": "WARNING",
        "subject": "pH-plus Leermeldekontakt",
        "severity": "warning",
        "description": "Leermeldekontakt der Sauglanze ausgelöst.",
    },
    "172": {
        "type": "WARNING",
        "subject": "Flockmittel max. Tagesdosierleistung",
        "severity": "warning",
        "description": "Tägliche Dosierleistung der Flockmittel-Dosierung erreicht.",
    },
    "173": {
        "type": "WARNING",
        "subject": "Flockmittel Kanister niedrig",
        "severity": "warning",
        "description": "Restinhalt des Flockmittel-Kanisters ist niedrig.",
    },
    "174": {
        "type": "WARNING",
        "subject": "Flockmittel Kanister leer",
        "severity": "warning",
        "description": "Der Flockmittel-Kanister ist leer.",
    },
    "175": {
        "type": "WARNING",
        "subject": "Flockmittel Leermeldekontakt",
        "severity": "warning",
        "description": "Leermeldekontakt der Sauglanze ausgelöst.",
    },
    "180": {
        "type": "REMINDER",
        "subject": "pH-Elektrode kalibrieren",
        "severity": "info",
        "description": "Kalibrierung der pH-Elektrode ist fällig.",
    },
    "181": {
        "type": "REMINDER",
        "subject": "Redox-Elektrode kalibrieren",
        "severity": "info",
        "description": "Kalibrierung der Redox-Elektrode ist fällig.",
    },
    "182": {
        "type": "REMINDER",
        "subject": "Chlor-Elektrode kalibrieren",
        "severity": "info",
        "description": "Kalibrierung der Chlor-Elektrode ist fällig.",
    },
    "200": {
        "type": "WARNING",
        "subject": "Dosiermodul getrennt",
        "severity": "warning",
        "description": "Keine Kommunikationsverbindung zum Dosiermodul.",
    },
    "201": {
        "type": "WARNING",
        "subject": "Dosiermodul Kommunikation verloren",
        "severity": "warning",
        "description": "Kommunikation zum Dosiermodul wurde unterbrochen.",
    },
    "203": {
        "type": "WARNING",
        "subject": "Relais-Erweiterung 1 getrennt",
        "severity": "warning",
        "description": "Keine Kommunikationsverbindung zur Relais-Erweiterung 1.",
    },
    "204": {
        "type": "WARNING",
        "subject": "Relais-Erweiterung 1 Kommunikation verloren",
        "severity": "warning",
        "description": "Kommunikation zur Relais-Erweiterung 1 wurde unterbrochen.",
    },
    "206": {
        "type": "WARNING",
        "subject": "Relais-Erweiterung 2 getrennt",
        "severity": "warning",
        "description": "Keine Kommunikationsverbindung zur Relais-Erweiterung 2.",
    },
    "207": {
        "type": "WARNING",
        "subject": "Relais-Erweiterung 2 Kommunikation verloren",
        "severity": "warning",
        "description": "Kommunikation zur Relais-Erweiterung 2 wurde unterbrochen.",
    },
    "209": {
        "type": "ALERT",
        "subject": "Zweites Dosiermodul erkannt",
        "severity": "critical",
        "description": "Ein zweites Dosiermodul wird ignoriert.",
    },
    "210": {
        "type": "ALERT",
        "subject": "Falsch codierte Relais Erweiterung",
        "severity": "critical",
        "description": "Eine zweite Relaiserweiterung hat die gleiche Codierung.",
    },
}


def get_error_info(code: str) -> Dict[str, str]:
    """Return error information for a given code."""

    return ERROR_CODES.get(
        str(code).strip(),
        {
            "type": "UNKNOWN",
            "subject": f"Unbekannter Code: {code}",
            "severity": "info",
            "description": "",
        },
    )


def get_errors_by_type(error_type: str) -> List[str]:
    """Return all error codes of a specific type."""

    upper_type = error_type.upper()
    return [
        code for code, data in ERROR_CODES.items() if data.get("type") == upper_type
    ]


def get_errors_by_severity(severity: str) -> List[str]:
    """Return all error codes with a specific severity."""

    lower_severity = severity.lower()
    return [
        code
        for code, data in ERROR_CODES.items()
        if data.get("severity", "").lower() == lower_severity
    ]
