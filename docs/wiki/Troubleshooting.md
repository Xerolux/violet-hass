# 🚨 Troubleshooting - Fehlersuche

Fehler treten auf? Hier findest du die Lösungen!

## Häufige Fehler

### ❌ "Verbindung zum Controller fehlgeschlagen"

**Symptome:**
- Integration zeigt "Nicht verfügbar" in Rot
- Alle Entitäten sind "unavailable"

**Lösungsschritte:**

1. **Konnektivität testen:**
```bash
# Ping Controller
ping 192.168.1.100

# HTTP-Request testen
curl http://192.168.1.100/getReadings?ALL
```

2. **IP-Adresse überprüfen**
   - Stimmt die IP noch? (Router kann IP ändern)
   - Verwende statische IP oder DHCP-Reservierung

3. **Firewall prüfen**
   - Firewall blockiert Zugriff?
   - Port 80 (oder 8080) freigeben

4. **Controller neu starten**
   - Controller ausschalten (Hauptschalter)
   - 30 Sekunden warten
   - Wieder anschalten

5. **Integration neu laden**
   - Einstellungen → Geräte & Dienste → Violet
   - ⋮ (Menü) → "Neu laden"

### ❌ "SSL-Zertifikat-Fehler"

**Symptom:** `SSL: CERTIFICATE_VERIFY_FAILED`

**Ursachen:**
- Controller nutzt selbsigniertes Zertifikat
- Datum/Uhrzeit auf HA falsch
- Falscher Hostname in URL

**Lösung 1: SSL-Validation deaktivieren (schnell)**
1. Einstellungen → Geräte & Dienste → Violet
2. ⋮ → "Optionen"
3. "SSL-Zertifikat prüfen" deaktivieren

⚠️ **Warnung:** Nur für vertrauenswürdige Netzwerke!

**Lösung 2: Zertifikat validieren**
```bash
# Mit Browser prüfen
https://192.168.1.100/

# Oder mit OpenSSL
openssl s_client -connect 192.168.1.100:8443 -showcerts
```

### ❌ "Timeout - Request dauert zu lange"

**Symptome:**
- Integration arbeitet, aber sehr langsam
- Häufige "Timeout"-Fehler in Logs

**Ursachen:**
- Netzwerk überlastet
- Controller nicht responsive
- Zu viele Sensoren abgefragt
- Timeout-Wert zu niedrig

**Lösungen:**

1. **Abfrageintervall erhöhen:**
   - Einstellungen → Geräte & Dienste → Violet → Optionen
   - "Abfrageintervall" erhöhen (z.B. 45 Sekunden statt 30)

2. **Weniger Sensoren aktivieren:**
   - Integration neu laden
   - Nur wichtige Sensoren auswählen

3. **Timeout-Wert erhöhen (erweitert):**
   - Einstellungen → Geräte & Dienste → Violet → Optionen
   - "Timeout" erhöhen (z.B. 15 Sekunden statt 10)

4. **Netzwerk-Stabilität prüfen:**
```bash
# Ping und Packet Loss testen
ping -c 20 192.168.1.100
```

### ❌ "Entitäten sind ständig 'unavailable'"

**Symptome:**
- Entitäten zeigen "unavailable" State
- Koordinator-Fehler im Log

**Ursachen:**
- Zu kurzes Abfrageintervall
- Sensor-Fehler am Controller
- Rate-Limit erreicht

**Lösungen:**

1. **Abfrageintervall erhöhen:**
   - Momentan auf 10-15s? → Auf 30-45s erhöhen

2. **Integration neu laden:**
```yaml
# In Automatisierung oder Developer Tools
service: homeassistant.reload_config_entry
target:
  device_id: <device_id>
```

3. **Logs prüfen:**
```bash
tail -f /config/home-assistant.log | grep violet_pool_controller
```

### ❌ "Sensor zeigt 'unknown' oder falsche Werte"

**Ursachen:**
- Sensor nicht kalibriert
- Sensor defekt
- Falsche API-Antwort

**Lösungen:**

1. **Sensor-Kalibrierung:**
   - pH: Monatlich kalibrieren
   - ORP: Mit pH-Kalibrierung
   - Chlor: Mit Testkit wöchentlich prüfen

2. **Sensor reinigen:**
   - Linse der Sensoren säubern
   - Verschmutzung entfernen

3. **Controller prüfen:**
   - Error-Codes anschauen
   - `sensor.violet_system_error_codes` prüfen

## Debug-Modus aktivieren

Für detaillierte Logs:

1. **configuration.yaml bearbeiten:**
```yaml
logger:
  logs:
    custom_components.violet_pool_controller: debug
    aiohttp: debug
```

2. **Home Assistant neu starten**

3. **Logs prüfen:**
   - Home Assistant → Einstellungen → System → Protokolle
   - Oder: `tail -f /config/home-assistant.log`

## Logs analysieren

**Wichtige Log-Einträge:**

| Log-Level | Bedeutung | Beispiel |
|-----------|-----------|----------|
| **DEBUG** | Detailinfos | Request wird gesendet |
| **INFO** | Normale Infos | Integration loaded |
| **WARNING** | Warnung | Sensor nicht gefunden |
| **ERROR** | Fehler | Verbindung fehlgeschlagen |

**Logs speichern:**
```bash
# Logs in Datei speichern
cp /config/home-assistant.log ~/violet-logs.txt
```

## Häufige Log-Fehler

### `Connection refused`
- **Ursache:** Controller nicht erreichbar
- **Lösung:** IP, Port, Firewall prüfen

### `Request timeout`
- **Ursache:** Zu langsame Verbindung
- **Lösung:** Abfrageintervall erhöhen

### `SSL: CERTIFICATE_VERIFY_FAILED`
- **Ursache:** Zertifikats-Problem
- **Lösung:** SSL-Validation deaktivieren oder Zertifikat prüfen

### `Invalid JSON response`
- **Ursache:** Controller antwortet falsch
- **Lösung:** Controller neu starten, Firmware prüfen

## Fehler-Codes vom Controller

Diese Codes sieht du in `sensor.violet_system_error_codes`:

| Code | Fehler | Lösung |
|------|--------|--------|
| **101** | Sensor-Fehler (pH, ORP, etc.) | Sensor prüfen/reinigen |
| **205** | Druck zu hoch | Ventil öffnen, Rückspülung |
| **301** | Wasser-Level zu niedrig | Wasser nachfüllen |
| **401** | Temperatur-Sensor defekt | Sensor ersetzen |

Siehe Controller-Handbuch für vollständige Liste.

## Spezielle Probleme

### Problem: State bleibt bei "5" (Wartend)

**Bedeutung:** Automatik wartet auf Bedingungen

**Lösungen:**
1. Bedingungen prüfen (z.B. Temperatur-Schwellenwert)
2. Fehler-Codes prüfen
3. Sicherheitsintervall (normalerweise 5-10 Min)
4. Manuell auf "1" (an) setzen zum Testen

### Problem: Pumpen-Geschwindigkeit zeigt falsch

**Symptom:** Speed-Sensor zeigt 0 obwohl Pumpe läuft

**Lösung:**
- Nicht alle Controller haben Speed-Sensor
- Mit `control_pump` Service nutzen für Speed-Control

### Problem: DMX-Szenen funktionieren nicht

**Lösungen:**
1. Lichter sind mit DMX verbunden?
2. DMX-Adressierung korrekt im Controller?
3. Mit `test_output` Service testen

### Problem: Dosierung funktioniert nicht

**Prüfen:**
1. Dosierpumpen angeschlossen?
2. Sicherheitsintervall vorbei? (normalerweise 5 Min)
3. Safety-Override umgehen (wenn gewünscht)

## Performance & Optimierung

### Home Assistant wird langsam

**Checks:**
1. Abfrageintervall auf 45-60s erhöhen
2. Weniger Sensoren aktivieren
3. Automatisierungen reduzieren
4. Logs auf Fehler-Loop prüfen

### Zu viele Log-Einträge

```yaml
logger:
  logs:
    custom_components.violet_pool_controller: warning
    aiohttp: warning
```

## Backup & Recovery

### Backup erstellen
```
Einstellungen → System → Sicherungen → Erstellen
```

### Aus Backup wiederherstellen
```
Einstellungen → System → Sicherungen → Wiederherstellen
```

### Integration neu laden ohne Restart
```
Einstellungen → Geräte & Dienste → Violet → ⋮ → Neu laden
```

## Support anfordern

Wenn nichts hilft:

1. **Logs sammeln:**
   - 50-100 Zeilen aus home-assistant.log kopieren
   - Debug-Mode aktivieren

2. **System-Info:**
   - Home Assistant Version
   - Addon Version
   - Controller-Modell & Firmware

3. **Erstellung eines Issues:**
   - [GitHub Issues](https://github.com/xerolux/violet-hass/issues)
   - Detaillierte Problembeschreibung
   - Logs anhängen (ohne Passwörter!)

4. **Community-Hilfe:**
   - [Discord](https://discord.gg/Qa5fW2R)
   - [Community Forum](https://community.home-assistant.io/)

---

## Weitere Seiten

- 📖 [[Installation-Setup]] - Installation Schritt-für-Schritt
- 🎯 [[Device-States]] - States verstehen
- ❓ [[FAQ]] - Häufige Fragen
- 🤖 [[Services]] - Alle Services
