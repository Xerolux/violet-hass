# Fehler-Codes – Controller Fehlercodes erklärt

> Vollständige Referenz aller Violet Pool Controller Fehlercodes mit Ursachen und Lösungsansätzen.

---

## Überblick

Der Violet Pool Controller sendet Fehlercodes über die API. Diese werden in Home Assistant als Sensor-Attribute angezeigt und können für Automatisierungen genutzt werden.

### Severity-Klassen

| Klasse | Symbol | Bedeutung |
|--------|--------|-----------|
| `info` | ℹ️ | Information / Erinnerung – kein Handlungsbedarf |
| `warning` | ⚠️ | Warnung – Aufmerksamkeit erforderlich |
| `critical` | 🚨 | Kritisch – sofortige Aktion erforderlich |

### Code-Typen

| Typ | Beschreibung |
|-----|-------------|
| `MESSAGE` | Statusnachricht vom Controller |
| `ALERT` | Alarm – System-Fehler oder Sicherheitsfunktion aktiv |
| `WARNING` | Warnung – Grenzwert überschritten |
| `REMINDER` | Erinnerung – Wartung oder Update |

---

## System & Hardware

| Code | Typ | Schwere | Beschreibung | Lösung |
|------|-----|---------|-------------|--------|
| `0` | MESSAGE | ℹ️ | Testnachricht | Keine Aktion erforderlich |
| `1` | MESSAGE | ℹ️ | Statusnachricht | Keine Aktion erforderlich |
| `2` | ALERT | 🚨 | **Hardwareproblem: COM-Link zum Carrier fehlerhaft** | Gerät neu starten, Hardware prüfen, Support kontaktieren |
| `3` | REMINDER | ℹ️ | Happy Birthday | Systemgeburtstag – keine Aktion |
| `8` | WARNING | ⚠️ | CPU-Temperatur hoch | Gerät entlüften, Umgebungstemperatur prüfen |
| `9` | ALERT | 🚨 | **CPU-Temperatur kritisch** | Sofort Gerät abschalten, Gehäuse/Lüftung prüfen |

---

## Updates

| Code | Typ | Schwere | Beschreibung | Lösung |
|------|-----|---------|-------------|--------|
| `10` | REMINDER | ℹ️ | Update verfügbar – wird automatisch installiert | Nächste Nacht abwarten |
| `11` | REMINDER | ℹ️ | Update verfügbar – Bestätigung erforderlich | Im Controller-Webinterface bestätigen |
| `12` | REMINDER | ℹ️ | Update verfügbar – manuell installieren | Update manuell anstoßen |

---

## Filterpumpe & Druck

| Code | Typ | Schwere | Beschreibung | Lösung |
|------|-----|---------|-------------|--------|
| `20` | ALERT | 🚨 | **Filterdruck zu niedrig** | Pumpe und Filter prüfen, Ansaugung kontrollieren |
| `21` | ALERT | 🚨 | **Filterdruck zu hoch** | Filter rückspülen, Filtergehäuse prüfen |
| `22` | WARNING | ⚠️ | Messwasser-Anströmung fehlt | Probenahmehahn öffnen, Strömung prüfen |
| `23` | WARNING | ⚠️ | Messwasser-Anströmung zu hoch | Probenahmehahn drosseln |
| `24` | ALERT | 🚨 | **Zirkulation fehlt** | Pumpe und Rohrsystem prüfen |
| `25` | ALERT | 🚨 | **Zirkulation zu hoch** | Absperrorgan prüfen, Pumpe drosseln |
| `26` | ALERT | 🚨 | **Frostschutz Filterpumpe nicht verfügbar** | Temperatursensor prüfen |
| `27` | ALERT | 🚨 | **Frostschutz Absorber nicht verfügbar** | Solar-Temperatursensor prüfen |

---

## Heizung & Temperatur

| Code | Typ | Schwere | Beschreibung | Lösung |
|------|-----|---------|-------------|--------|
| `30` | WARNING | ⚠️ | Wärmetauscher-Temperatur hoch | Durchfluss erhöhen, Heizleistung reduzieren |
| `31` | ALERT | 🚨 | **Übertemperatur-Schutz nicht verfügbar** | Temperatursensor prüfen |

### Temperaturprogramme (71–78)

| Code | Typ | Schwere | Beschreibung |
|------|-----|---------|-------------|
| `71` | WARNING | ⚠️ | Temperaturregelung Programm 1 ausgelöst |
| `72` | WARNING | ⚠️ | Temperaturregelung Programm 2 ausgelöst |
| `73` | WARNING | ⚠️ | Temperaturregelung Programm 3 ausgelöst |
| `74` | WARNING | ⚠️ | Temperaturregelung Programm 4 ausgelöst |
| `75` | MESSAGE | ℹ️ | Temperaturregelung Programm 5 ausgelöst |
| `76` | WARNING | ⚠️ | Temperaturregelung Programm 6 ausgelöst |
| `77` | WARNING | ⚠️ | Temperaturregelung Programm 7 ausgelöst |
| `78` | WARNING | ⚠️ | Temperaturregelung Programm 8 ausgelöst |

---

## Rückspülung

| Code | Typ | Schwere | Beschreibung | Lösung |
|------|-----|---------|-------------|--------|
| `40` | WARNING | ⚠️ | Rückspülung ausgelassen | Manuell rückspülen, Zeitfenster prüfen |
| `41` | MESSAGE | ℹ️ | Nachspeisung vor Rückspülung fehlgeschlagen | Wasserzufuhr prüfen |
| `42` | MESSAGE | ℹ️ | Nachspeisung nicht möglich | Nachspeiseventil und Zufuhr prüfen |
| `45` | ALERT | 🚨 | **Omnitronic ohne Rückmeldung (Rückspülen)** | Stellantrieb prüfen, Verkabelung kontrollieren |
| `46` | ALERT | 🚨 | **Omnitronic ohne Rückmeldung (Nachspülen)** | Stellantrieb prüfen |
| `47` | ALERT | 🚨 | **Omni-Stellantrieb Position nicht erreicht** | Mechanik prüfen, Endschalter kontrollieren |
| `49` | ALERT | 🚨 | **Omnitronic Rückmeldekontakt offen** | Anschluss und Kontakt prüfen |

---

## Wassernachspeisung

| Code | Typ | Schwere | Beschreibung | Lösung |
|------|-----|---------|-------------|--------|
| `50` | ALERT | 🚨 | **Sicherheitszeit überschritten** | Schwimmerschalter und Wasserzufuhr prüfen |
| `51` | ALERT | 🚨 | **Oberer Schwimmer hat nicht reagiert** | Schwimmerschalter reinigen/tauschen |
| `52` | ALERT | 🚨 | **Unterer Schwimmer hat nicht zurückgeschaltet** | Schwimmerschalter reinigen/tauschen |

---

## Überlaufbehälter

| Code | Typ | Schwere | Beschreibung | Lösung |
|------|-----|---------|-------------|--------|
| `60` | ALERT | 🚨 | **Nachspeisung fehlgeschlagen** | Wasserzufuhr und Ventil prüfen |
| `61` | WARNING | ⚠️ | Trockenlauf | Füllstand erhöhen, Ansaugung prüfen |
| `62` | WARNING | ⚠️ | Pegelmessung fehlerhaft | Pegelsonde reinigen/kalibrieren |

---

## Temperatursensoren (101–112)

| Code | Typ | Schwere | Beschreibung | Lösung |
|------|-----|---------|-------------|--------|
| `101` | WARNING | ⚠️ | Temperatursensor 1 fehlt | Sensor-Kabel prüfen, Sensor tauschen |
| `102` | WARNING | ⚠️ | Temperatursensor 2 fehlt | Sensor-Kabel prüfen |
| `103–112` | WARNING | ⚠️ | Temperatursensoren 3–12 fehlen | Entsprechenden Sensor prüfen |

**Vorgehen bei Sensor-Fehler:**
1. Kabel auf Beschädigung prüfen
2. Stecker am Controller reinigen
3. Sensor mit Ohmmeter messen (1-Wire: ~1kΩ bei 25°C)
4. Bei Defekt: Gleichen Sensor-Typ (DS18B20) verwenden

---

## Chlor-Dosierung (120–125)

| Code | Typ | Schwere | Beschreibung | Lösung |
|------|-----|---------|-------------|--------|
| `120` | WARNING | ⚠️ | Redox-Grenzwert Chlor-Dosierung | ORP-Wert prüfen, ggf. manuell dosieren |
| `121` | WARNING | ⚠️ | Chlor-Grenzwert Dosierung | Chlorgehalt prüfen |
| `122` | WARNING | ⚠️ | Max. Tagesdosierung überschritten | Ursache suchen (Wasserverlust, hoher Bedarf) |
| `123` | WARNING | ⚠️ | Chlor-Kanister niedrig | Nachfüllen! |
| `124` | WARNING | ⚠️ | **Chlor-Kanister leer** | Sofort nachfüllen, Dosierung unterbrochen |
| `125` | WARNING | ⚠️ | Leermelder-Kontakt Sauglanze | Kanister-Füllstand und Sauglanze prüfen |

---

## Elektrolyse (130–135)

| Code | Typ | Schwere | Beschreibung | Lösung |
|------|-----|---------|-------------|--------|
| `130` | WARNING | ⚠️ | Redox-Grenzwert Elektrolyse | ORP-Wert überwachen |
| `131` | WARNING | ⚠️ | Chlor-Grenzwert Elektrolyse | Chlormessung prüfen |
| `132` | WARNING | ⚠️ | Max. Tagesproduktion Elektrolyse | Leistung prüfen |
| `133` | WARNING | ⚠️ | Elektrolyse Restlaufzeit | Zelle-Lebensdauer prüfen, Wartung planen |
| `134` | WARNING | ⚠️ | Max. Betriebszeit Elektrolyse-Zelle | Zelle tauschen |
| `135` | WARNING | ⚠️ | Durchflussschalter Elektrolyse | Durchfluss prüfen, Schalter reinigen |

---

## H2O2-Dosierung (142–145)

| Code | Typ | Schwere | Beschreibung | Lösung |
|------|-----|---------|-------------|--------|
| `142` | WARNING | ⚠️ | H2O2 max. Tagesdosierung | Wasserqualität prüfen |
| `143` | WARNING | ⚠️ | H2O2-Kanister niedrig | Nachfüllen |
| `144` | WARNING | ⚠️ | H2O2-Kanister leer | Sofort nachfüllen |
| `145` | WARNING | ⚠️ | Leermelder Sauerstoff-Kanister | Sauglanze prüfen |

---

## pH-Dosierung (150–165)

| Code | Typ | Schwere | Beschreibung | Lösung |
|------|-----|---------|-------------|--------|
| `150` | WARNING | ⚠️ | pH-minus Grenzwert | pH-Wert prüfen |
| `152` | WARNING | ⚠️ | pH-minus max. Tagesdosierung | Wasserchemie prüfen |
| `153` | WARNING | ⚠️ | pH-minus Kanister niedrig | Nachfüllen |
| `154` | WARNING | ⚠️ | **pH-minus Kanister leer** | Sofort nachfüllen |
| `155` | WARNING | ⚠️ | pH-minus Leermelder | Sauglanze prüfen |
| `160` | WARNING | ⚠️ | pH-plus Grenzwert | pH-Wert prüfen |
| `162` | WARNING | ⚠️ | pH-plus max. Tagesdosierung | Wasserchemie prüfen |
| `163` | WARNING | ⚠️ | pH-plus Kanister niedrig | Nachfüllen |
| `164` | WARNING | ⚠️ | **pH-plus Kanister leer** | Sofort nachfüllen |
| `165` | WARNING | ⚠️ | pH-plus Leermelder | Sauglanze prüfen |

---

## Flockmittel (172–175)

| Code | Typ | Schwere | Beschreibung | Lösung |
|------|-----|---------|-------------|--------|
| `172` | WARNING | ⚠️ | Flockmittel max. Tagesdosierung | Wassertrübung prüfen |
| `173` | WARNING | ⚠️ | Flockmittel-Kanister niedrig | Nachfüllen |
| `174` | WARNING | ⚠️ | **Flockmittel-Kanister leer** | Sofort nachfüllen |
| `175` | WARNING | ⚠️ | Flockmittel Leermelder | Sauglanze prüfen |

---

## Kalibrierungs-Erinnerungen (180–182)

| Code | Typ | Schwere | Beschreibung | Intervall |
|------|-----|---------|-------------|----------|
| `180` | REMINDER | ℹ️ | pH-Elektrode kalibrieren fällig | Monatlich |
| `181` | REMINDER | ℹ️ | Redox-Elektrode kalibrieren fällig | Monatlich |
| `182` | REMINDER | ℹ️ | Chlor-Elektrode kalibrieren fällig | Monatlich |

---

## Kommunikation & Module (200–210)

| Code | Typ | Schwere | Beschreibung | Lösung |
|------|-----|---------|-------------|--------|
| `200` | WARNING | ⚠️ | Dosiermodul getrennt | Kabel und Stecker prüfen |
| `201` | WARNING | ⚠️ | Dosiermodul Kommunikation verloren | Bus-Kommunikation prüfen |
| `203` | WARNING | ⚠️ | Relais-Erweiterung 1 getrennt | Kabel prüfen |
| `204` | WARNING | ⚠️ | Relais-Erweiterung 1 Kommunikation verloren | Bus-Kommunikation prüfen |
| `206` | WARNING | ⚠️ | Relais-Erweiterung 2 getrennt | Kabel prüfen |
| `207` | WARNING | ⚠️ | Relais-Erweiterung 2 Kommunikation verloren | Bus-Kommunikation prüfen |
| `209` | ALERT | 🚨 | **Zweites Dosiermodul erkannt** | Nur ein Dosiermodul erlaubt – entfernen |
| `210` | ALERT | 🚨 | **Falsch codierte Relais-Erweiterung** | Codierung der Erweiterung prüfen |

---

## Analog- und Schaltregeln (81–98)

### Analogregeln

| Code | Beschreibung |
|------|-------------|
| `81–88` | Analogregel-Programme 1–8 ausgelöst |

### Schaltregeln

| Code | Beschreibung |
|------|-------------|
| `91–98` | Schaltregel-Programme 1–8 ausgelöst |

---

## Fehlercode in Home Assistant nutzen

### Error-Sensor abfragen

```yaml
# Template-Sensor für aktuellen Fehlercode
template:
  - sensor:
      - name: "Pool Fehler-Text"
        state: >
          {{ state_attr('sensor.violet_error_code', 'description') | default('Kein Fehler') }}
```

### Automatisierung bei kritischem Fehler

```yaml
automation:
  - alias: "Pool: Kritischer Fehler-Alarm"
    trigger:
      - platform: template
        value_template: >
          {{ state_attr('sensor.violet_error_code', 'severity') == 'critical' }}
    action:
      - service: notify.mobile_app_phone
        data:
          title: "KRITISCHER POOL-FEHLER"
          message: >
            Code: {{ states('sensor.violet_error_code') }}
            Problem: {{ state_attr('sensor.violet_error_code', 'subject') }}
            Details: {{ state_attr('sensor.violet_error_code', 'description') }}
```

### Kalibrierungs-Erinnerung automatisch

```yaml
automation:
  - alias: "Pool: Kalibrierung fällig"
    trigger:
      - platform: template
        value_template: >
          {{ states('sensor.violet_error_code') in ['180', '181', '182'] }}
    action:
      - service: notify.mobile_app_phone
        data:
          title: "Pool: Kalibrierung erforderlich"
          message: >
            {{ state_attr('sensor.violet_error_code', 'subject') }}
```

---

## Unbekannte Fehlercodes

Wenn ein Code nicht in dieser Liste vorhanden ist:

1. Firmware-Version des Controllers prüfen (neuere Codes in neuerer Firmware)
2. Controller-Webinterface für direkte Fehlermeldung öffnen
3. [GitHub Issue](https://github.com/Xerolux/violet-hass/issues) erstellen mit Code und Beschreibung

---

*Zurück: [Troubleshooting](Troubleshooting) | Zurück: [Home](Home)*
