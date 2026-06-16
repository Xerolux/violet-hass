# Changelog - Violet Pool Controller

> **Language Note:** This changelog is available in German. For English release notes, see the GitHub releases page.

## ⚠️ BREAKING CHANGES - Version 2.0.0-beta.10

### 🚨 **SICHERHEIT: Automatische Deaktivierung kritischer Schalter**

**WICHTIG:** Ab dieser Version werden folgende Schalter **automatisch deaktiviert** für Sicherheit:

- **Dosierungsschalter** (Chlor, pH-, pH+, Flockmittel, Elektrolyse)
- **Rückspülung/Spülung** (Backwash/Rinse)
- **Wassernachfüllung** (Refill)

**Grund:** Diese Operationen können zu schweren Schäden führen, wenn sie ohne Zeitlimit laufen:
- ⚠️ **Chemische Überdosierung** → Wasserqualität beeinträchtigt, Gesundheitsrisiko
- ⚠️ **Ausrüstungsschaden** → Pumpen, Filter, Ventile zerstört
- ⚠️ **Überflutung** → Tank überläuft, Wasserschaden im Haus

**Neue Sicherheitslogik:**
1. ✅ Alle unsicheren Schalter sind **standardmäßig deaktiviert**
2. ✅ Services erfordern **Pflicht-Zeitangabe** für sichere Kontrolle
3. ✅ Benutzer können in Sicherheitseinstellungen manuell aktivieren (mit Warnung!)
4. ✅ Ausführliche Warnmeldungen im Log, wenn Schalter deaktiviert werden

**Was ändert sich für dich?**

| Vorher | Nachher |
|--------|---------|
| ❌ Schalter kann unbegrenzt laufen | ✅ Schalter deaktiviert (sicher) |
| ❌ Risiko von Schäden | ✅ Risiko minimiert |
| ❌ Manuelle Kontrolle ohne Limits | ✅ Services mit Pflicht-Zeitlimit |

**Wie nutze ich diese Schalter weiterhin?**

Nutze die **Services** stattdessen - sie erfordern eine Zeitangabe:
- `violet_pool_controller.smart_dosing` - für Dosierungen (pH-, pH+, Chlor, Flockmittel)
- `violet_pool_controller.control_pump` - für Pumpensteuerung
- `violet_pool_controller.manage_pv_surplus` - für PV-Überschuss-Steuerung
- Zusätzliche Services: `control_dmx_scenes`, `set_light_color_pulse`, `manage_digital_rules`, `test_output`

**Oder: Schalter manuell aktivieren (Experten)**

Wenn du die Risiken kennst und akzeptierst, kannst du die unsicheren Schalter aktivieren:
1. Gehe zu **Einstellungen → Geräte & Services → Violet Pool Controller**
2. Öffne **Optionen → 🚨 Sicherheitseinstellungen**
3. Aktiviere "Manuelle Steuerung kritischer Schalter erlauben"
4. ⚠️ Akzeptiere die Warnung und nutze Schalter mit Vorsicht!

---

## Version 2.0.0-beta.10

### ✨ Neue Funktionen

- **Sicherheitseinstellungen im Reconfigure-Flow** - Sicherheit kann jetzt ohne vollständige Neukonfiguration angepasst werden
- **Auto-Disable für unsichere Schalter** - Automatische Migration für bestehende Installationen

### 🐛 Bugfixes

- Behobener AttributeError bei `RegistryEntry.enabled` (sollte `disabled` sein)
- Korrekte Speicherung von Sicherheitseinstellungen in Config-Optionen
- Re-Enable-Logik für Schalter, wenn Sicherheitsüberschreibung aktiviert wird

### 🔧 Technische Verbesserungen

- Sicherheitseinstellungen jetzt in `options` statt `data` gespeichert
- Fallback-Prüfung (options → data) für Rückwärtskompatibilität
- Separate Reconfigure-Flows für Verbindung und Sicherheit
- SSL-Verifikation im Reconfigure-Flow konfigurierbar

---

## Version 2.0.0-beta.9

### ✨ Neue Funktionen

- OneWire-ROM-Code-Sensorunterstützung (zeigt Adresse statt °C)
- DI-Rule Verbleibzeit-Anzeige in lesbarem Format (1d 2h 30m 45s)
- Verbesserte Hardware-Modul-Erkennung (aktuell statt cached)

### 🐛 Bugfixes

- OneWire-ROM-Code zeigt jetzt korrekt Adresse statt Temperatur
- DI-Rule-Stoppuhr als Text-Sensor (nicht numerisch)
- Hardware-Module werden basierend auf aktuellen Daten erkannt

### 📦 Dependencies

- Aktualisiert auf violet-poolController-api 0.0.24

---

## Sicherheitsrichtlinie

Diese Integration kontrolliert kritische Poolausrüstung mit strikter Sicherheit:

**Siehe auch:** [⚠️ BREAKING CHANGES - Version 2.0.0-beta.10](#breaking-changes---version-200-0-beta10) für vollständige Informationen zur Sicherheitsimplementierung, automatischen Deaktivierung kritischer Schalter und erforderlichen Services mit Zeitlimits.

**Sicherheitsmerkmale:**
- ✅ Automatische Deaktivierung unsicherer Schalter (standardmäßig)
- ✅ Services erfordern obligatorische Zeitangaben
- ✅ Explizite Benutzer-Opt-in für manuelle Kontrolle (mit Warnungen)
- ✅ Umfassendes Logging bei kritischen Operationen

**Kontakt & Support:**
- GitHub Issues: https://github.com/Xerolux/violet-hass/issues
- E-Mail: git@xerolux.de
