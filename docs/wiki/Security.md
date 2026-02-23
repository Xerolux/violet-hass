# Security & SSL – Sicherheit der Integration

> Sicherheitsarchitektur, SSL/TLS-Konfiguration und Best Practices.

---

## Sicherheits-Überblick

Die Violet Pool Controller Integration wurde mit mehreren Sicherheits-Schichten entwickelt:

```
┌─────────────────────────────────────────────┐
│           SECURITY LAYERS                   │
├─────────────────────────────────────────────┤
│  1. Input Sanitization (XSS, Injection)     │
│  2. SSL/TLS Certificate Verification        │
│  3. Token Bucket Rate Limiting              │
│  4. Thread-Safe Locking                     │
│  5. Auto-Recovery mit Backoff               │
└─────────────────────────────────────────────┘
```

---

## SSL/TLS Konfiguration

### Standard-Einstellung: SSL aktiviert

SSL-Zertifikats-Verifikation ist **standardmäßig aktiv** (`verify_ssl=True`).

### Konfigurationsoptionen

| Option | Standard | Beschreibung |
|--------|---------|-------------|
| `use_ssl` | `False` | HTTPS statt HTTP verwenden |
| `verify_ssl` | `True` | Zertifikat verifizieren |

### Wann SSL deaktivieren?

Nur wenn der Controller ein **selbstsigniertes Zertifikat** verwendet und du im **vertrauenswürdigen Heimnetzwerk** bist:

```
Einstellungen → Geräte & Dienste → Violet Pool Controller
→ Konfigurieren → SSL-Zertifikat prüfen: Nein
```

> **Warnung:** Deaktiviere SSL-Verifikation niemals in öffentlichen Netzwerken!

### SSL mit eigenem Zertifikat

Für selbstsignierte Zertifikate in Production-Umgebungen:

1. Zertifikat dem Home Assistant CA-Store hinzufügen
2. `verify_ssl: true` beibehalten
3. Zertifikat regelmäßig erneuern

---

## Input Sanitization

Alle Benutzereingaben werden durch `InputSanitizer` validiert, bevor sie die API erreichen.

### Geschützte Angriffsvektoren

| Angriff | Schutz |
|---------|--------|
| **XSS** (Cross-Site-Scripting) | HTML-Escaping aller Eingaben |
| **SQL Injection** | Pattern-basierte Validierung |
| **Command Injection** | Whitelist-Validierung für Befehle |
| **Path Traversal** | Pfad-Normalisierung und Validierung |
| **Parameter Tampering** | Bereichsprüfung für numerische Werte |

### Validierte Wertebereiche

| Parameter | Minimum | Maximum |
|-----------|---------|---------|
| pH-Wert | 6.0 | 8.0 |
| ORP-Wert | 200 mV | 900 mV |
| Temperatur | 10°C | 40°C |
| Dosier-Dauer | 5s | 300s |
| Pump-Geschwindigkeit | 0 | 3 |

---

## Rate Limiting

Der Token-Bucket-Algorithmus schützt den Controller vor Überlastung:

```
Token Bucket:
├── Max. Tokens: konfigurierbar
├── Auffüllrate: konstant
├── Prioritäts-Queue: kritische Anfragen zuerst
└── Bei leerem Bucket: Anfrage verzögert
```

### Warum Rate Limiting?

Der Violet Pool Controller ist ein **Embedded-System** mit begrenzter CPU-Leistung. Zu viele gleichzeitige API-Anfragen können:
- Den Controller zum Absturz bringen
- Messwerte verfälschen
- Die Steuerung verlangsamen

### Empfohlene Polling-Intervalle

| Anzahl Controller | Empfohlenes Intervall |
|-------------------|----------------------|
| 1 | 15–20 Sekunden |
| 2–3 | 25–30 Sekunden |
| 4+ | 45–60 Sekunden |

---

## Thread Safety

Die Integration verwendet zwei dokumentierte Locks mit fester Reihenfolge:

```python
_api_lock:       Schützt API-Aufrufe und Daten-Updates
_recovery_lock:  Schützt Recovery-State und Versuche

Reihenfolge: NIEMALS verschachtelt!
```

**Warum wichtig?** Home Assistant ist multi-threaded. Ohne Locks könnten gleichzeitige Anfragen zu inkonsistenten Zuständen führen.

---

## Auto-Recovery & Backoff

Bei Verbindungsverlust versucht die Integration automatisch die Verbindung wiederherzustellen:

```
Versuch 1:  Sofort
Versuch 2:  10 Sekunden warten
Versuch 3:  20 Sekunden warten
Versuch 4:  40 Sekunden warten
...
Max. Wartezeit: 300 Sekunden (5 Minuten)
Max. Versuche:  10

Nach 10 Fehlversuchen: Manuelle Intervention erforderlich
```

### Recovery nach maximalem Fehlschlag

```
Einstellungen → Geräte & Dienste → Violet Pool Controller
→ Neu laden
```

Oder in der `configuration.yaml`:

```yaml
# Integration manuell neu starten
homeassistant:
  customize:
    violet_pool_controller.*:
      assumed_state: false
```

---

## Netzwerk-Sicherheit

### Empfohlene Netzwerk-Konfiguration

```
┌─────────────────────────────────────────┐
│  Heimnetzwerk (192.168.1.0/24)          │
│                                         │
│  Home Assistant  ←→  Violet Controller  │
│  (192.168.1.10)       (192.168.1.55)   │
│                                         │
│  Beide im selben VLAN (kein Internet)   │
└─────────────────────────────────────────┘
```

### Firewall-Empfehlungen

```
# Empfohlen: Controller vom Internet isolieren
# Nur Home Assistant darf auf Controller zugreifen

iptables -A INPUT -s 192.168.1.10 -d 192.168.1.55 -j ACCEPT
iptables -A INPUT -d 192.168.1.55 -j DROP
```

### Port-Anforderungen

| Port | Protokoll | Verwendung |
|------|-----------|-----------|
| `80` | HTTP | Unverschlüsselte API |
| `443` | HTTPS | Verschlüsselte API (wenn SSL aktiviert) |

---

## Sicherheits-Checkliste

### Grundkonfiguration

- [ ] Controller hat statische IP-Adresse
- [ ] Controller ist nicht direkt aus dem Internet erreichbar
- [ ] Home Assistant ist aktuell
- [ ] Integration auf aktueller Version

### SSL/TLS

- [ ] SSL aktiviert wenn möglich
- [ ] Zertifikat gültig (nicht abgelaufen)
- [ ] `verify_ssl` nur deaktiviert bei selbstsigniertem Zertifikat im Heimnetz

### Zugangsdaten

- [ ] Controller-Passwort ist stark und einzigartig
- [ ] Zugangsdaten nur in HA-Konfiguration gespeichert (nicht in YAML-Dateien)

### Monitoring

- [ ] Automatisierung für kritische Fehlercodes
- [ ] Log-Level auf `warning` gesetzt für Produktionsbetrieb

---

## Sicherheitslücken melden

Wenn du eine Sicherheitslücke entdeckst:

1. **Nicht öffentlich melden** (kein GitHub Issue)
2. **Email:** git@xerolux.de
3. **Beschreibung** der Lücke mit Proof-of-Concept
4. **Erwartetes Verhalten** vs. tatsächliches Verhalten

Wir antworten innerhalb von 48 Stunden und koordinieren eine verantwortungsvolle Offenlegung.

---

## Logging & Datenschutz

Die Integration loggt **keine** sensiblen Daten:
- Keine Passwörter in Logs
- Keine vollständigen API-Antworten im Debug-Modus
- Keine persönlichen Daten

### Log-Level konfigurieren

```yaml
# configuration.yaml
logger:
  default: warning
  logs:
    custom_components.violet_pool_controller: warning
    # Für Debugging:
    # custom_components.violet_pool_controller: debug
```

---

*Zurück: [Troubleshooting](Troubleshooting) | Weiter: [FAQ](FAQ)*
