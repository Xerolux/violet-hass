# ❓ FAQ - Häufig gestellte Fragen

Über 40 häufige Fragen und Antworten!

## Allgemein

**F: Benötige ich eine Cloud-Anbindung?**
A: Nein! Das Addon ist 100% lokal. Keine Cloud, kein Internet erforderlich.

**F: Kann ich mehrere Controller ansteuern?**
A: Ja! Multi-Controller ist vollständig unterstützt. Einfach mehrere Integrationen hinzufügen.

**F: Ist das Addon sicher?**
A: Ja! Lokale Kommunikation mit SSL/TLS-Optionen und Input-Sanitization gegen Injection-Angriffe.

**F: Welche Home Assistant Version?**
A: Minimum 2025.12.0. Getestet auf 2026.x.

---

## Installation

**F: Wie finde ich die IP-Adresse meines Controllers?**
A:
1. Router-Admin öffnen (192.168.1.1)
2. Verbundene Geräte anzeigen
3. "Violet" suchen und IP notieren
4. Oder: `ping violet.local`

**F: Kann ich den Controller über HTTPS ansprechen?**
A: Ja! "SSL verwenden" aktivieren in den Einstellungen.

**F: Funktioniert selbsigniertes Zertifikat?**
A: Ja, aber "SSL-Zertifikat prüfen" deaktivieren (nur für vertrauenswürdige Netzwerke!).

**F: Warum wird meine Integration nicht angezeigt?**
A: Home Assistant neu starten nach Installation!

---

## Funktionen & Bedienung

**F: Was bedeutet "Automatik" vs. "Manuell"?**
A:
- **Automatik**: Controller regelt selbstständig (nach Temperatur, Zeit, etc.)
- **Manuell**: Du stellst direkt ein, Auto-Regeln werden ignoriert

**F: Was sind die Device States 0-6?**
A: Sieben verschiedene Betriebszustände:
- 0 = Automatik, aus
- 1 = Manuell an
- 2 = Automatik, an
- 3 = Automatik mit Timer, an
- 4 = Manuell erzwungen, an
- 5 = Automatik, wartend
- 6 = Manuell, aus

Lies [[Device-States]] für Details.

**F: Kann ich Pumpen-Geschwindigkeit einstellen?**
A: Ja! 3 Stufen möglich mit dem `control_pump` Service.

**F: Wie dosiere ich sicher?**
A:
- Kleine Mengen (15-30 Sekunden)
- Abstand zwischen Dosierungen beachten
- Sensor-Wert immer kontrollieren
- Safety-Override nur wenn nötig

**F: Können die Sensoren falsch zeigen?**
A: Möglich! Kalibrierung:
- pH/ORP: Monatlich
- Chlor: Mit Testkit wöchentlich
- Prüfe Sensoren auf Verschmutzung

---

## Probleme & Fehlersuche

**F: Sensoren zeigen "unavailable"**
A:
1. Abfrageintervall erhöhen (30-45s)
2. Integration neu laden
3. Weniger Sensoren aktivieren
4. Netzwerk-Stabilität prüfen

**F: Controller antwortet sehr langsam**
A:
1. Netzwerk-Auslastung prüfen
2. Abfrageintervall erhöhen
3. CPU-Last des Controllers prüfen
4. Zu viele Sensoren?

**F: Warum werden Sensoren nicht angezeigt?**
A:
1. Nicht im Setup-Flow aktiviert?
2. Controller hat diesen Sensor nicht
3. Feature ist nicht konfiguriert
4. Lösung: Integration neu laden

**F: "Verbindung fehlgeschlagen"**
A:
1. IP-Adresse stimmt? Ping testen: `ping 192.168.1.100`
2. Controller online? Web-Seite öffnen
3. Firewall blockiert?
4. Username/Passwort korrekt?

**F: SSL-Fehler beim Verbinden**
A:
1. Zertifikat valid? Mit Browser prüfen
2. "SSL-Zertifikat prüfen" deaktivieren (nur temp!)
3. Datum/Uhrzeit korrekt auf HA?

---

## Performance & Optimierung

**F: Welches Abfrageintervall sollte ich nutzen?**
A:
- 10-15s: Schnell, aber hohe Last
- **20-30s: Standard, gute Balance** ✅
- 45-60s: Sparsam, weniger reaktiv

**F: Ständig Automatisierungen schreiben - langweilig!**
A: Nutze Blueprints! Vorgefertigte Automatisierungs-Vorlagen sind im Repo enthalten.

**F: Kann ich Logging reduzieren?**
A: Ja, in `configuration.yaml`:
```yaml
logger:
  logs:
    custom_components.violet_pool_controller: warning
```

**F: Addon verlangsamt Home Assistant?**
A: Sollte nicht. Bei Problemen:
1. Abfrageintervall erhöhen
2. Weniger Sensoren aktivieren
3. Weniger Automatisierungen starten
4. Logs checken auf Fehler-Loop

---

## Services & Automatisierungen

**F: Wie rufe ich einen Service auf?**
A: Drei Möglichkeiten:
1. Developer Tools → Services
2. YAML in Automatisierung
3. Automation UI Builder

**F: Kann ich eine Automatisierung zeitgesteuert auslösen?**
A: Ja!
```yaml
trigger:
  - platform: time
    at: "08:00:00"
```

**F: Kann ich auf Wettervorhersagen reagieren?**
A: Ja, mit der Weather-Integration!

**F: Was ist der Unterschied zwischen Services?**
A: Services sind spezialisiert:
- `control_pump` - Pumpe mit Geschwindigkeit
- `smart_dosing` - Chemikalien dosieren
- `switch.turn_on` - Nur Ein/Aus

---

## Updates & Maintenance

**F: Wie aktualisiere ich das Addon?**
A: Mit HACS:
1. HACS → Integrationen
2. "Violet Pool Controller" finden
3. Wenn verfügbar: "Aktualisieren"
4. Home Assistant neu starten

**F: Was ist vor einem Update zu tun?**
A:
1. Backup erstellen
2. Changelog lesen
3. Breaking Changes prüfen

**F: Was wenn Update Probleme macht?**
A:
1. Home Assistant neu starten (nicht nur Reload!)
2. Integration neu laden
3. Bei Problemen: zur alten Version zurück

**F: Wie stelle ich zur alten Version zurück?**
A:
```bash
cd /config/custom_components/violet_pool_controller
git checkout v0.2.0  # Beispiel
```

---

## Deinstallation

**F: Wie deinstalliere ich das Addon?**
A:
1. Einstellungen → Geräte & Dienste
2. Violet auswählen → ⋮ → Entfernen
3. Dateien löschen: `/config/custom_components/violet_pool_controller`
4. Home Assistant neu starten

**F: Bleiben meine Automatisierungen nach Deinstallation?**
A: Ja! Sie sind separat gespeichert. Funktionieren aber nicht ohne Addon.

---

## Besondere Anwendungen

**F: Kann ich eine Pool-Party automatisieren?**
A: Ja! Mit Services:
```yaml
service: violet_pool_controller.control_dmx_scenes
data:
  action: party_mode
```

**F: Wie nutze ich Solar-Überschuss?**
A:
```yaml
service: violet_pool_controller.manage_pv_surplus
data:
  mode: activate
  pump_speed: 3
```

**F: Kann ich Temperaturgrenzen setzen?**
A: Ja mit Climate-Entities:
```yaml
service: climate.set_temperature
target:
  entity_id: climate.violet_heater
data:
  temperature: 28
  hvac_mode: heat
```

---

## Support & Weitere Hilfe

Fragen noch nicht beantwortet?

- 📖 **Wiki durchsuchen** - Wahrscheinlich hier
- 🐛 **[GitHub Issues](https://github.com/xerolux/violet-hass/issues)** - Bug-Reports
- 💬 **[Community Forum](https://community.home-assistant.io/)** - Nutzer-Fragen
- 🎮 **[Discord](https://discord.gg/Qa5fW2R)** - Live-Chat
- 📧 **Email**: git@xerolux.de

---

## Weitere Seiten

- 📖 [[Installation-Setup]] - Installation Schritt-für-Schritt
- 🎯 [[Device-States]] - States 0-6 erklärt
- 🤖 [[Services]] - Alle Services
- 🚨 [[Troubleshooting]] - Fehlersuche
