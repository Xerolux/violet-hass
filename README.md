# 🏊 Violet Pool Controller für Home Assistant / for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![downloads][downloads-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacs-badge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymeacoffee-badge]][buymeacoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

## 🌍 Language / Sprache

**[🇩🇪 Deutsche Version](#-violet-pool-controller-für-home-assistant)** | **[🇺🇸 English Version](#-violet-pool-controller-for-home-assistant-1)**

---

# 🇩🇪 Violet Pool Controller für Home Assistant

Verwandle deinen Pool in einen Smart Pool! Diese umfassende Home Assistant Integration bietet vollständige Kontrolle und Überwachung deines **Violet Pool Controllers** und bringt intelligente Pool-Automatisierung direkt in dein Smart Home Ökosystem.

![Violet Home Assistant Integration][logo]

## ✨ Was macht diese Integration besonders?

🎯 **Komplette Pool-Automatisierung** - Überwache und steuere jeden Aspekt deines Pools  
🌡️ **Intelligente Klimasteuerung** - Smarte Heizungs- und Solar-Verwaltung  
🧪 **Chemisches Gleichgewicht** - Automatische pH- und Chlor-Überwachung/Dosierung  
🏊 **Abdeckungsmanagement** - Wetterabhängige automatische Abdeckungssteuerung  
💧 **Filter-Wartung** - Automatische Rückspülplanung  
📱 **Mobile-Ready** - Vollständige Kontrolle von überall über die Home Assistant App  
🔧 **Keine Cloud erforderlich** - 100% lokale Steuerung und Privatsphäre  

## 📊 Feature-Übersicht

### 🔍 **Umfassende Überwachung**
- **Wasserchemie:** pH, Redox (ORP), Chlorgehalt mit Trend-Tracking
- **Temperatursensoren:** Poolwasser, Umgebungsluft, Solar-Kollektor-Temperaturen  
- **System-Status:** Pumpenbetrieb, Heizungsstatus, Filterdruck, Wasserstände
- **Anlagen-Gesundheit:** Laufzeit-Verfolgung, Fehlererkennung, Wartungsalarme

### 🎛️ **Intelligente Steuerung**
- **Klima-Management:** Dual-Zone-Heizung (Heizung + Solar) mit Zeitplanung
- **Chemische Dosierung:** Automatische pH+/pH- und Chlor-Dosierung mit Sicherheitsgrenzen
- **Pumpensteuerung:** Variable Geschwindigkeitssteuerung, energieeffiziente Planung
- **Beleuchtung:** Vollständige RGB/DMX-Lichtsteuerung mit Szenen und Automatisierung
- **Abdeckungsbetrieb:** Wetterabhängige automatische Abdeckungssteuerung
- **Filtration:** Intelligente Rückspülzyklen basierend auf Druck und Laufzeit

### 🤖 **Smart-Automatisierungs-Features**
- **Energie-Optimierung:** PV-Überschussmodus für solargetriebene Heizung
- **Wetter-Integration:** Automatische Reaktionen auf Regen, Wind, Temperatur
- **Wartungsplanung:** Automatisierte Rückspülung, Wassertests, Anlagenzyklen
- **Sicherheitssysteme:** Notabschaltungen, Überlaufschutz, Chemikalien-Grenzwerte
- **Benutzerdefinierte Szenen:** Pool-Party-Modus, Eco-Modus, Winter-Modus, Urlaubs-Modus

## 📦 Installation

### 🚀 HACS Installation (Empfohlen)

Die Integration ist über HACS (Home Assistant Community Store) verfügbar:

1. **HACS installieren** falls noch nicht vorhanden ([HACS Installationsanleitung](https://hacs.xyz/docs/setup/download))
2. **HACS öffnen** in deiner Home Assistant Oberfläche
3. **Custom Repository hinzufügen:**
   - Klicke auf die drei Punkte (⋮) in der oberen rechten Ecke
   - Wähle "Benutzerdefinierte Repositorys"
   - Hinzufügen: `https://github.com/xerolux/violet-hass`
   - Kategorie: "Integration"
   - Klicke "Hinzufügen"
4. **Integration installieren:**
   - Suche nach "Violet Pool Controller"
   - Klicke "Herunterladen"
   - Starte Home Assistant neu

### 🔧 Manuelle Installation (Erweiterte Benutzer)

Für Entwickler oder erweiterte Benutzer, die die manuelle Installation bevorzugen:

```bash
# Methode 1: Git Clone
cd /config/custom_components/
git clone https://github.com/xerolux/violet-hass.git violet_pool_controller

# Methode 2: Download und Entpacken
wget https://github.com/xerolux/violet-hass/archive/main.zip
unzip main.zip
mv violet-hass-main/custom_components/violet_pool_controller /config/custom_components/
```

**Dann starte Home Assistant neu**

## ⚙️ Konfiguration

Die Konfiguration erfolgt vollständig über die Home Assistant UI - keine YAML-Bearbeitung erforderlich!

### 🚀 Schnell-Setup

1. **Integration hinzufügen:**
   ```
   Einstellungen → Geräte & Dienste → Integration hinzufügen → "Violet Pool Controller"
   ```

2. **Verbindungseinstellungen:**
   ```yaml
   Host: 192.168.1.100          # IP deines Controllers
   Username: admin               # Falls Authentifizierung aktiviert
   Password: dein-passwort       # Falls Authentifizierung aktiviert
   SSL verwenden: ☐/☑           # Ankreuzen bei HTTPS-Nutzung
   Gerätename: Pool Controller   # Anzeigename
   Abfrageintervall: 30s         # Wie oft aktualisiert wird (10-300s)
   ```

3. **Pool-Konfiguration:**
   ```yaml
   Pool-Größe: 50 m³            # Dein Pool-Volumen
   Pool-Typ: Freibad            # Innen-/Außenpool/Whirlpool/etc.
   Desinfektion: Chlor          # Deine Desinfektionsmethode
   ```

4. **Feature-Auswahl:**
   Wähle welche Komponenten du aktivieren möchtest:
   - ✅ Heizungssteuerung
   - ✅ Solar-Management  
   - ✅ pH-Steuerung
   - ✅ Chlor-Steuerung
   - ✅ Abdeckungssteuerung
   - ✅ Rückspülsystem
   - ✅ LED-Beleuchtung
   - ✅ PV-Überschuss-Modus
   - ☐ Erweiterungsausgänge (falls zutreffend)
   - ☐ Digitale Eingänge (falls zutreffend)

## 🧩 Verfügbare Entitäten

Die Integration erstellt Entitäten dynamisch basierend auf den Fähigkeiten deines Controllers und ausgewählten Features:

### 🌡️ **Klima-Entitäten**
```yaml
climate.pool_heater          # Haupt-Poolheizung Steuerung
climate.pool_solar           # Solar-Kollektor Management  
```

### 🔍 **Sensoren**
```yaml
sensor.pool_temperature      # Aktuelle Wassertemperatur
sensor.pool_ph_value         # Aktueller pH-Wert (6.0-8.5)
sensor.pool_orp_value        # Redoxpotential (mV)
sensor.pool_chlorine_level   # Freies Chlor (mg/l)
sensor.filter_pressure       # Filtersystem-Druck
sensor.water_level          # Pool-Wasserstand
# ... und viele mehr basierend auf deiner Einrichtung
```

### 💡 **Schalter**
```yaml
switch.pool_pump            # Hauptfilterpumpe
switch.pool_heater          # Poolheizung ein/aus
switch.pool_solar           # Solar-Zirkulation  
switch.pool_lighting        # Pool-Beleuchtung
switch.backwash             # Filter-Rückspülzyklus
switch.ph_dosing_minus      # pH- Dosierpumpe
switch.ph_dosing_plus       # pH+ Dosierpumpe  
switch.chlorine_dosing      # Chlor-Dosiersystem
# ... plus alle konfigurierten Erweiterungsausgänge
```

## 🔧 Benutzerdefinierte Services

Die Integration bietet spezialisierte Services für erweiterte Automatisierung:

### 🎯 **Kern-Steuerungs-Services**

#### `violet_pool_controller.turn_auto`
Schalte jedes steuerbare Gerät in den Automatikmodus:
```yaml
service: violet_pool_controller.turn_auto
target:
  entity_id: switch.pool_pump
data:
  auto_delay: 30  # Optional: Verzögerung in Sekunden
```

#### `violet_pool_controller.set_pv_surplus`
Aktiviere Solar-Energie-Überschuss-Modus:
```yaml
service: violet_pool_controller.set_pv_surplus  
target:
  entity_id: switch.pv_surplus_mode
data:
  pump_speed: 2   # Geschwindigkeitsstufe 1-3
```

### 🧪 **Chemikalien-Management-Services**

#### `violet_pool_controller.manual_dosing`
Löse manuelle chemische Dosierung aus:
```yaml
service: violet_pool_controller.manual_dosing
target:
  entity_id: switch.ph_dosing_minus
data:
  duration_seconds: 30  # Dosierdauer
```

## 🤖 Automatisierungs-Blueprints

Starte schnell mit unseren vorgefertigten Automatisierungs-Blueprints:

### 📥 **Installation**
Importiere Blueprints direkt in Home Assistant:
```
Einstellungen → Automatisierungen & Szenen → Blueprints → Blueprint importieren
```

### 🌡️ **Intelligente Temperatursteuerung**
- **Tag/Nacht-Planung:** Verschiedene Temperaturen für aktive und ruhige Stunden
- **Solar-Priorität:** Automatische Nutzung der Solarheizung wenn verfügbar
- **Wetter-Integration:** Heizungsanpassung basierend auf Wettervorhersagen
- **Energie-Optimierung:** PV-Überschuss-Modus für maximale Effizienz

## 🚨 Fehlerbehebung

### ⚡ **Schnelle Lösungen**

**Verbindungsprobleme:**
```bash
# Konnektivität testen
ping 192.168.1.100

# HA-Logs prüfen
tail -f /config/home-assistant.log | grep violet_pool_controller

# Controller-API verifizieren
curl http://192.168.1.100/getReadings?ALL
```

**Häufige Lösungen:**
- ✅ **Falsche IP-Adresse:** Controller-IP in Router-Einstellungen verifizieren
- ✅ **SSL-Mismatch:** Stelle sicher dass "SSL verwenden" der Controller-Konfiguration entspricht
- ✅ **Firewall-Blockierung:** Firewall temporär zum Testen deaktivieren
- ✅ **Veraltete Firmware:** Controller-Firmware über PoolDigital aktualisieren
- ✅ **Netzwerk-Probleme:** VLAN/Subnetz-Konfiguration prüfen

## 💝 Dieses Projekt unterstützen

Diese Integration wird in meiner Freizeit entwickelt und gepflegt. Wenn sie deinem Smart Pool Setup einen Mehrwert bietet, zeige etwas Liebe:

[![GitHub Sponsor](https://img.shields.io/github/sponsors/xerolux?logo=github&style=for-the-badge&color=blue)](https://github.com/sponsors/xerolux)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-xerolux-blue?logo=ko-fi&style=for-the-badge)](https://ko-fi.com/xerolux)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-xerolux-yellow?logo=buy-me-a-coffee&style=for-the-badge)](https://www.buymeacoffee.com/xerolux)

**Andere Unterstützungsmöglichkeiten:**
- ⭐ **Gib diesem Repository einen Stern** auf GitHub
- 🐛 **Melde Bugs** und schlage Verbesserungen vor
- 📢 **Teile** mit anderen Pool-Besitzern
- 📝 **Trage bei** mit Code oder Dokumentation
- 💬 **Hilf anderen** in den Community-Foren

---

# 🇺🇸 Violet Pool Controller for Home Assistant

Transform your pool into a smart pool! This comprehensive Home Assistant integration provides complete control and monitoring of your **Violet Pool Controller**, bringing intelligent pool automation directly to your smart home ecosystem.

## ✨ What Makes This Special?

🎯 **Complete Pool Automation** - Monitor and control every aspect of your pool  
🌡️ **Smart Climate Control** - Intelligent heating and solar management  
🧪 **Chemical Balance** - Automated pH and chlorine monitoring/dosing  
🏊 **Cover Management** - Weather-aware automatic cover control  
💧 **Filter Maintenance** - Automatic backwash scheduling  
📱 **Mobile Ready** - Full control from anywhere via Home Assistant app  
🔧 **No Cloud Required** - 100% local control and privacy  

## 📊 Features Overview

### 🔍 **Comprehensive Monitoring**
- **Water Chemistry:** pH, Redox (ORP), Chlorine levels with trend tracking
- **Temperature Sensors:** Pool water, ambient air, solar collector temperatures  
- **System Status:** Pump operation, heater status, filter pressure, water levels
- **Equipment Health:** Runtime tracking, error detection, maintenance alerts

### 🎛️ **Intelligent Controls**
- **Climate Management:** Dual-zone heating (heater + solar) with scheduling
- **Chemical Dosing:** Automated pH+/pH- and chlorine dosing with safety limits
- **Pump Control:** Variable speed control, energy-efficient scheduling
- **Lighting:** Full RGB/DMX lighting control with scenes and automation
- **Cover Operation:** Weather-responsive automatic cover management
- **Filtration:** Smart backwash cycles based on pressure and runtime

### 🤖 **Smart Automation Features**
- **Energy Optimization:** PV-surplus mode for solar-powered heating
- **Weather Integration:** Automatic responses to rain, wind, temperature
- **Maintenance Scheduling:** Automated backwash, water testing, equipment cycles
- **Safety Systems:** Emergency shutdowns, overflow protection, chemical limits
- **Custom Scenes:** Pool party mode, eco mode, winter mode, vacation mode

## 📦 Installation

### 🚀 HACS Installation (Recommended)

The integration is available through HACS (Home Assistant Community Store):

1. **Install HACS** if you haven't already ([HACS Installation Guide](https://hacs.xyz/docs/setup/download))
2. **Open HACS** in your Home Assistant interface
3. **Add Custom Repository:**
   - Click the three dots (⋮) in the top-right corner
   - Select "Custom repositories"
   - Add: `https://github.com/xerolux/violet-hass`
   - Category: "Integration"
   - Click "Add"
4. **Install Integration:**
   - Search for "Violet Pool Controller"
   - Click "Download"
   - Restart Home Assistant

### 🔧 Manual Installation (Advanced Users)

For developers or advanced users who prefer manual installation:

```bash
# Method 1: Git Clone
cd /config/custom_components/
git clone https://github.com/xerolux/violet-hass.git violet_pool_controller

# Method 2: Download and Extract
wget https://github.com/xerolux/violet-hass/archive/main.zip
unzip main.zip
mv violet-hass-main/custom_components/violet_pool_controller /config/custom_components/
```

**Then restart Home Assistant**

## ⚙️ Configuration

Configuration is done entirely through the Home Assistant UI - no YAML editing required!

### 🚀 Quick Setup

1. **Add Integration:**
   ```
   Settings → Devices & Services → Add Integration → "Violet Pool Controller"
   ```

2. **Connection Settings:**
   ```yaml
   Host: 192.168.1.100          # Your controller's IP
   Username: admin               # If authentication enabled
   Password: your-password       # If authentication enabled
   Use SSL: ☐/☑                # Check if using HTTPS
   Device Name: Pool Controller  # Friendly name
   Polling Interval: 30s         # How often to update (10-300s)
   ```

3. **Pool Configuration:**
   ```yaml
   Pool Size: 50 m³             # Your pool volume
   Pool Type: Outdoor Pool      # Indoor/Outdoor/Whirlpool/etc.
   Disinfection: Chlorine       # Your sanitization method
   ```

4. **Feature Selection:**
   Select which components you want to enable:
   - ✅ Heating Control
   - ✅ Solar Management  
   - ✅ pH Control
   - ✅ Chlorine Control
   - ✅ Cover Control
   - ✅ Backwash System
   - ✅ LED Lighting
   - ✅ PV Surplus Mode
   - ☐ Extension Outputs (if applicable)
   - ☐ Digital Inputs (if applicable)

## 🧩 Available Entities

The integration creates entities dynamically based on your controller's capabilities and selected features:

### 🌡️ **Climate Entities**
```yaml
climate.pool_heater          # Main pool heater control
climate.pool_solar           # Solar collector management  
```

### 🔍 **Sensors**
```yaml
sensor.pool_temperature      # Current water temperature
sensor.pool_ph_value         # Current pH level (6.0-8.5)
sensor.pool_orp_value        # Redox potential (mV)
sensor.pool_chlorine_level   # Free chlorine (mg/l)
sensor.filter_pressure       # Filter system pressure
sensor.water_level          # Pool water level
# ... and many more based on your setup
```

### 💡 **Switches**
```yaml
switch.pool_pump            # Main filtration pump
switch.pool_heater          # Pool heater on/off
switch.pool_solar           # Solar circulation  
switch.pool_lighting        # Pool lights
switch.backwash             # Filter backwash cycle
switch.ph_dosing_minus      # pH- dosing pump
switch.ph_dosing_plus       # pH+ dosing pump  
switch.chlorine_dosing      # Chlorine dosing system
# ... plus any configured extension outputs
```

## 🔧 Custom Services

The integration provides specialized services for advanced automation:

### 🎯 **Core Control Services**

#### `violet_pool_controller.turn_auto`
Switch any controllable device to automatic mode:
```yaml
service: violet_pool_controller.turn_auto
target:
  entity_id: switch.pool_pump
data:
  auto_delay: 30  # Optional: delay in seconds
```

#### `violet_pool_controller.set_pv_surplus`
Activate solar energy surplus mode:
```yaml
service: violet_pool_controller.set_pv_surplus  
target:
  entity_id: switch.pv_surplus_mode
data:
  pump_speed: 2   # Speed level 1-3
```

### 🧪 **Chemical Management Services**

#### `violet_pool_controller.manual_dosing`
Trigger manual chemical dosing:
```yaml
service: violet_pool_controller.manual_dosing
target:
  entity_id: switch.ph_dosing_minus
data:
  duration_seconds: 30  # Dosing duration
```

## 🤖 Automation Blueprints

Get started quickly with our pre-built automation blueprints:

### 📥 **Installation**
Import blueprints directly in Home Assistant:
```
Settings → Automations & Scenes → Blueprints → Import Blueprint
```

### 🌡️ **Smart Temperature Control**
- **Day/Night Scheduling:** Different temperatures for active and quiet hours
- **Solar Priority:** Automatically use solar heating when available
- **Weather Integration:** Adjust heating based on weather forecasts
- **Energy Optimization:** PV-surplus mode for maximum efficiency

### 🧪 **Intelligent pH Management**
- **Automatic Dosing:** Maintain perfect pH levels (6.8-7.8) automatically
- **Safety Limits:** Maximum dosing limits to prevent over-treatment
- **Pump Integration:** Only dose when filtration is active
- **Smart Scheduling:** Avoid dosing during high-usage periods

## 🚨 Troubleshooting

### ⚡ **Quick Fixes**

**Connection Issues:**
```bash
# Test connectivity
ping 192.168.1.100

# Check HA logs
tail -f /config/home-assistant.log | grep violet_pool_controller

# Verify controller API
curl http://192.168.1.100/getReadings?ALL
```

**Common Solutions:**
- ✅ **Wrong IP Address:** Verify controller IP in router settings
- ✅ **SSL Mismatch:** Ensure "Use SSL" matches controller configuration  
- ✅ **Firewall Blocking:** Temporarily disable firewall for testing
- ✅ **Outdated Firmware:** Update controller firmware via PoolDigital
- ✅ **Network Issues:** Check VLAN/subnet configuration

## 🏊 About the Violet Pool Controller

![Violet Pool Controller][pbuy]

The **VIOLET Pool Controller** by [PoolDigital GmbH & Co. KG](https://www.pooldigital.de/) is a premium, German-engineered smart pool automation system. It's designed for pool owners who want professional-grade control and monitoring without the complexity.

**Key Capabilities:**
- 🔧 **Complete Pool Management:** Filtration, heating, lighting, chemical dosing
- 📱 **Remote Access:** Control from anywhere via web interface or API
- 🌐 **Smart Home Ready:** JSON API for seamless integration
- 🛡️ **Safety First:** Multiple protection systems and monitoring
- 📊 **Advanced Analytics:** Detailed logging and performance tracking
- ⚡ **Energy Efficient:** Smart scheduling and PV integration

**Where to Get One:**
- **Official Shop:** [pooldigital.de](https://www.pooldigital.de/poolsteuerungen/violet-poolsteuerung/74/violet-basis-modul-poolsteuerung-smart)
- **Community Support:** [PoolDigital Forum](http://forum.pooldigital.de/)
- **Technical Docs:** Available with purchase

## 💝 Supporting This Project

This integration is developed and maintained in my free time. If it adds value to your smart pool setup, consider showing some love:

[![GitHub Sponsor](https://img.shields.io/github/sponsors/xerolux?logo=github&style=for-the-badge&color=blue)](https://github.com/sponsors/xerolux)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-xerolux-blue?logo=ko-fi&style=for-the-badge)](https://ko-fi.com/xerolux)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-xerolux-yellow?logo=buy-me-a-coffee&style=for-the-badge)](https://www.buymeacoffee.com/xerolux)

**Other Ways to Support:**
- ⭐ **Star this repository** on GitHub
- 🐛 **Report bugs** and suggest improvements
- 📢 **Share** with other pool owners
- 📝 **Contribute** code or documentation
- 💬 **Help others** in the community forums

## 🤝 Contributing

We welcome contributions from the community! Whether it's:

- 🐛 **Bug fixes** and improvements
- ✨ **New features** and enhancements  
- 📚 **Documentation** updates
- 🧪 **Testing** on different controller models
- 🌍 **Translations** to other languages

**Getting Started:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and test thoroughly
4. Commit with clear messages (`git commit -m 'Add amazing feature'`)
5. Push to your branch (`git push origin feature/amazing-feature`)  
6. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📋 Changelog

### Version 0.1.0 (Current Development)
- ✨ Initial release with comprehensive pool control
- 🌡️ Climate control for heating and solar systems  
- 🧪 Chemical monitoring and automated dosing
- 🏊 Pool cover integration with weather awareness
- 🔄 Intelligent backwash automation
- 📱 Full Home Assistant UI integration
- 🤖 Smart automation blueprints
- 🌍 Multi-language support (EN/DE)

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## 📞 Connect & Support

[![GitHub][github-shield]][github]
[![Discord][discord-shield]][discord]  
[![Community Forum][forum-shield]][forum]
[![Email](https://img.shields.io/badge/email-git%40xerolux.de-blue?style=for-the-badge&logo=gmail)](mailto:git@xerolux.de)

---

**Made with ❤️ for the Home Assistant and Pool Automation Community**

*Transform your pool into a smart pool - because life's too short for manual pool maintenance!* 🏊‍♀️🤖

---

<!-- Links -->
[integration_blueprint]: https://github.com/ludeeus/integration_blueprint
[buymeacoffee]: https://www.buymeacoffee.com/xerolux
[buymeacoffee-badge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/xerolux/violet-hass.svg?style=for-the-badge
[commits]: https://github.com/xerolux/violet-hass/commits/main
[hacs]: https://hacs.xyz
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[logo]: https://github.com/xerolux/violet-hass/raw/main/logo.png
[picture]: https://github.com/xerolux/violet-hass/raw/main/picture.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/xerolux/violet-hass.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Xerolux%20(%40xerolux)-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/xerolux/violet-hass.svg?style=for-the-badge
[releases]: https://github.com/xerolux/violet-hass/releases
[user_profile]: https://github.com/xerolux
[issues]: https://github.com/xerolux/violet-hass/issues
[github]: https://github.com/xerolux/violet-hass
[github-shield]: https://img.shields.io/badge/GitHub-xerolux/violet--hass-blue?style=for-the-badge&logo=github
[pbuy]: https://github.com/xerolux/violet-hass/raw/main/screenshots/violetbm.jpg
[downloads-shield]: https://img.shields.io/github/downloads/xerolux/violet-hass/latest/total.svg?style=for-the-badge
Use my Tesla referral link: [Referral Link](https://ts.la/sebastian564489)
