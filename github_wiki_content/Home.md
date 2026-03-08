# 🏊 Willkommen zur Violet Pool Controller Integration!

## 📢 Letzte Änderungen (März 2025)

### ✨ Neue Funktionen & Verbesserungen

#### 🔒 Sicherheit & Haftung (NEU!)
- **Umfassender Disclaimer**: Haftungsausschluss für Sicherheit und Nutzung
- **Deutsch & Englisch**: Vollständige Sicherheitshinweise in beiden Sprachen
- **Setup-Integration**: Verbindlicher Haftungsausschluss im Konfigurationsprozess
- 📖 [Konfigurationshilfe (DE)](../docs/help/configuration-guide.de.md)
- 📖 [Konfigurationshilfe (EN)](../docs/help/configuration-guide.en.md)

#### 🎨 Icon-Optimierung (NEU!)
- **68+ Icons optimisiert**: Alle Entities jetzt mit konsistenten, professionellen MDI-Icons
- **Bessere Erkennbarkeit**: Spezielle Icons statt generischer Symbole
- **Beispiele**:
  - pH-Wert: `mdi:ph` statt `mdi:flask`
  - Beckenwasser: `mdi:pool`
  - Überlaufbehälter: `mdi:water-sync`
  - Wärmetauscher: `mdi:radiator`
  - Rückspülung: `mdi:autorenew`
  - Flockung: `mdi:water`
- 📖 [Icon-Referenz](Icon-Reference) | 📊 [Alle Icons](../ICON_UPGRADE_SUMMARY.md)

#### 🛠️ Qualität & Stabilität
- **Home Assistant 2025.12+**: Getestet und kompatibel
- **100% Lokal**: Keine Cloud-Abhängigkeiten
- **SSL/TLS Support**: Sichere Kommunikation
- **Multi-Controller**: Mehrere Pools in einer HA-Instanz

---

## 🚀 Schnellstart

### 1. Installation (via HACS)
```
HACS → Integrationen → ⋮ → Benutzerdefinierte Repositories
URL: https://github.com/xerolux/violet-hass
Kategorie: Integration
```

### 2. Einrichtung
```
Einstellungen → Geräte & Dienste → Integration hinzufügen
→ "Violet Pool Controller" auswählen
→ Host IP eingeben (z.B. 192.168.1.100)
→ Features auswählen
→ Fertig! 🎉
```

> ⚠️ **WICHTIG**: Lies und bestätige den Haftungsausschluss im Setup!

---

## 📖 Dokumentation

### 📚 Wichtige Guides

| Thema | Beschreibung | Link |
|-------|-------------|------|
| **Installation** | Vollständige Installationsanleitung | [Installation Guide](Installation) |
| **Konfiguration** | Schritt-für-Schritt Einrichtung | [Configuration](Configuration) |
| **Entities** | Alle Sensoren, Schalter, Klima | [Entities](Entities) |
| **Services** | Automation & Scripts | [Services](Services) |
| **Troubleshooting** | Probleme lösen | [Troubleshooting](Troubleshooting) |

### 🌍 Mehrsprachige Unterstützung

- 🇩🇪 **Deutsch**: [Konfigurationshilfe (DE)](../docs/help/configuration-guide.de.md)
- 🇬🇧 **English**: [Configuration Guide (EN)](../docs/help/configuration-guide.en.md)

---

## 🌟 Features

| Kategorie | Features |
|-----------|----------|
| **🌡️ Klimasteuerung** | Heizung & Solar mit Thermostat und Zeitplanung |
| **🧪 Chemie-Dosierung** | Automatisches pH & Chlor mit Sicherheitsgrenzen |
| **💧 Filter & Pumpe** | 3-Stufen-Pumpe, automatische Rückspülung |
| **🏊 Abdeckung** | Wetterabhängige Cover-Automatisierung |
| **💡 LED / DMX** | 8 steuerbare Szenen, RGB-Beleuchtung |
| **📊 Überwachung** | pH, ORP, Temperaturen, Druck, Durchfluss, Laufzeiten |
| **⚡ Energie** | PV-Überschuss-Modus für Solarheizung |
| **🔒 Sicherheit** | 100% lokal, SSL/TLS, Rate Limiting |
| **🔧 Multi-Controller** | Mehrere Pools in einer HA-Instanz |

---

## 💝 Unterstützung

Diese Integration wird in meiner Freizeit entwickelt. Unterstütze das Projekt:

- ⭐ [Repository auf GitHub sternen](https://github.com/xerolux/violet-hass)
- 🐛 [Bugs melden](https://github.com/xerolux/violet-hass/issues)
- 💬 [Community Forum](https://community.home-assistant.io/)
- 💰 [Sponsor](https://github.com/sponsors/xerolux) | [Ko-fi](https://ko-fi.com/xerolux)

---

## 📋 Systemvoraussetzungen

- **Home Assistant**: 2025.12.0+ (getestet bis 2026.x)
- **Python**: 3.12+
- **Netzwerk**: Violet Pool Controller im lokalen Netzwerk erreichbar
- **Browser**: Moderne Browser mit JavaScript-Unterstützung

---

## 🔐 Sicherheitshinweise

⚠️ **WICHTIG**: Diese Integration steuert echte Poolausrüstung!

- ✅ Lies den **Haftungsausschluss** im Setup-Prozess sorgfältig
- ✅ Stelle sicher, dass du alle Sicherheitsmechanismen verstehst
- ✅ Halte jederzeit manuelle Not-Abschalter bereit
- ✅ Überwache deine Anlage regelmäßig persönlich
- ✅ Beachte die Sicherheitsdatenblätter aller verwendeten Chemikalien
- ✅ Befolge die Dokumentation deines Pool-Herstellers

> 📖 **Details**: [Sicherheit & Haftung](../docs/help/configuration-guide.de.md#-sicherheit--haftung)

---

## 📞 Hilfe & Community

Brauchst du Hilfe?

1. 📖 **Dokumentation lesen**: [Konfigurationsguide](../docs/help/configuration-guide.de.md)
2. 🔍 **Suche im Forum**: [Community Home Assistant](https://community.home-assistant.io/)
3. 🐛 **Problem melden**: [GitHub Issues](https://github.com/xerolux/violet-hass/issues)
4. 💬 **Discord**: [Home Assistant Discord](https://discord.gg/cAwGJU3)

---

**Viel Spaß mit deinem Smart Pool! 🏊✨**
