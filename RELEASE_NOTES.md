## v1.0.0 – Violet Pool Controller

**STABLE RELEASE** - Production-ready with extensive testing on live hardware!

---

### Highlights

Die erste stabile Version der komplett überarbeiteten Violet Pool Controller Integration.
Getestet auf echtem Controller-Hardware mit HA 2026.

---

### Critical Bug Fixes | Kritische Fehlerbehebungen

- **API Query Parameter Fix**: `getReadings` Endpunkt nutzte fehlerhafte `params={"ALL": ""}` statt korrekte `query="ALL"` - **dies war die Ursache für fehlende Sensordaten**
- **Firmware-Extraktion**: Firmware-Version wird jetzt korrekt aus der API-Antwort extrahiert
- **Switch State Handling**: Leere Strings (`""`) werden nicht mehr als `True` interpretiert
- **Composite State Parsing**: Pipe-separierte Zustände wie `"2|BLOCKED_BY_OUTSIDE_TEMP"` werden jetzt korrekt aufgelöst
- **Empty State Arrays**: `SOLARSTATE = "[]"` wird als fehlender Wert erkannt und Fallback auf Basiszustand genutzt
- **Status-Sensor Deutsch**: Alle Status-Sensoren zeigen jetzt deutsche Beschreibungen statt englischer Texte

### New Features | Neue Funktionen

- **Deutsche Status-Beschreibungen**: Switches zeigen detaillierte deutsche Zustandsinformationen in `extra_state_attributes` (Modus, Geschwindigkeit, Laufzeit)
- **Pumpen-Details**: Aktive Drehzahlstufe (0-3) wird automatisch erkannt und angezeigt
- **Heizungs-Details**: Zieltemperatur und Nachlaufzeit in Attributen sichtbar
- **Solar-Details**: Zieltemperatur als Attribut verfügbar
- **Dosierungs-Details**: Status, Reichweite, Tagesmenge und Kanistervolumen als Attribute
- **Rückspülungs-Details**: Rückspülschritt und Info als Attribute
- **Dashboard Template**: `Dashboard/pool_control_status.yaml` mit `secondaryinfo-entity-row` für Status-Anzeige direkt unter Schaltern
- **Circuit Breaker Pattern**: Automatische Absicherung gegen API-Ausfälle mit Retry und Recovery

### Improvements | Verbesserungen

- **Startup Performance**: 3-Sekunden-Sleep beim Start entfernt - Integration startet sofort
- **Vereinfachtes Data Fetching**: Immer Full Refresh statt komplexer Partial/Full-Logik
- **Composite State Sensoren**: PUMPSTATE, HEATERSTATE, SOLARSTATE korrekt als Sensoren verfügbar
- **Dosing State Sensoren**: DOS_*_STATE Arrays werden korrekt geparst und angezeigt
- **API Rate Limiting**: Token Bucket Algorithmus schützt den Controller vor Überlastung
- **Auto-Recovery**: Exponentieller Backoff (10s-300s) bei Verbindungsverlust
- **Input Sanitization**: Schutz gegen XSS, SQL Injection und Command Injection
- **SSL/TLS Security**: Zertifikatsverifizierung standardmäßig aktiviert
- **HA 2026 Kompatibilität**: Getestet mit Home Assistant 2025.12.0+

### Dashboard | Dashboard-Vorlagen

- Neue `pool_control_status.yaml` mit zwei Varianten:
  - **Variante 1**: Mit `custom:secondaryinfo-entity-row` (HACS) - Status direkt unter Schaltern
  - **Variante 2**: Ohne Custom Card - Status als separate Zeilen

---

### Technische Details

- **Minimum HA Version**: 2025.12.0
- **Python**: 3.12+
- **Dependencies**: aiohttp >= 3.10.0

---

### 📦 Installation

**HACS (Recommended):**
1. Add custom repository: `Xerolux/violet-hass`
2. Search for "Violet Pool Controller"
3. Click Install

**Manual:**
1. Download `violet_pool_controller.zip`
2. Extract to `custom_components/violet_pool_controller`
3. Restart Home Assistant

---

📋 [Full changelog: v1.0.7-alpha.3...v1.0.0](https://github.com/Xerolux/violet-hass/compare/v1.0.7-alpha.3...v1.0.0)

---

### ❤️ Support | Unterstützung

If you find this integration useful, consider supporting the developer:

- ☕ **[Buy Me a Coffee](https://buymeacoffee.com/xerolux)**
- 🚗 **[Tesla Referral Code](https://ts.la/sebastian564489)**
- ⭐ **Star this repository**

Every contribution, no matter how small, is a huge motivation! Thank you! 🙏

Jeder Beitrag, egal wie klein, ist eine große Motivation! Vielen Dank! 🙏

---

### 💬 Feedback & Contributions

- 🐛 **[Report a bug](https://github.com/Xerolux/violet-hass/issues/new?template=bug_report.md)**
- 💡 **[Request a feature](https://github.com/Xerolux/violet-hass/issues/new?template=feature_request.md)**
- 🤝 **[Contribute](https://github.com/Xerolux/violet-hass/blob/main/CONTRIBUTING.md)**

---

### 📄 Credits

**Developed by:** [Xerolux](https://github.com/Xerolux)
**Integration for:** Violet Pool Controller by PoolDigital GmbH & Co. KG
**License:** MIT
