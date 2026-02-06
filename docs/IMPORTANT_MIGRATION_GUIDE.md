# ⚠️ WICHTIG: Integration muss komplett neu eingerichtet werden!

## Problem
Die aktuelle Installation hat `selected_sensors: []` in der Config gespeichert.
Dadurch werden nur ~108 Entitäten erstellt statt der erwarteten ~156.

## Lösung: Komplette Neueinrichtung

### Schritt 1: Integration komplett löschen
1. Öffne **Einstellungen** → **Geräte & Dienste**
2. Suche **Violet Pool Controller**
3. Klicke auf die **3 Punkte** (⋮) rechts
4. Wähle **Löschen**
5. Bestätige die Löschung

### Schritt 2: Home Assistant neu starten
1. Öffne **Entwicklerwerkzeuge** → **YAML**
2. Klicke **Alle YAML-Konfigurationen neu laden**
3. ODER: **Einstellungen** → **System** → **Neu starten**

### Schritt 3: Integration neu hinzufügen
1. Öffne **Einstellungen** → **Geräte & Dienste**
2. Klicke **+ Integration hinzufügen** (unten rechts)
3. Suche nach **"Violet Pool Controller"**
4. Klicke darauf

### Schritt 4: Setup durchlaufen

#### 4.1 Verbindung (Connection)
- **IP-Adresse**: 192.168.178.55 (oder deine IP)
- **SSL verwenden**: false (oder true, je nach Setup)
- **Benutzername/Passwort**: (falls benötigt)
- **Device ID**: 1 (Standard)
- **Polling Intervall**: 10 Sekunden (Standard)
- **Timeout**: 10 Sekunden
- **Retry Versuche**: 3
- Klicke **Weiter**

#### 4.2 Pool-Setup
- **Pool-Größe**: 50 m³ (oder deine Größe)
- **Pool-Typ**: Freibad, Hallenbad, etc.
- **Desinfektionsmethode**: Chlor, Salz, etc.
- Klicke **Weiter**

#### 4.3 Feature-Auswahl
✅ **Aktiviere die Features die du nutzt**:
- [x] Heizungssteuerung
- [x] Solarabsorber
- [x] pH-Kontrolle
- [x] Chlor-Management
- [x] Abdeckungssteuerung (falls vorhanden)
- [x] Rückspül-Automatik
- [x] Filterpumpe
- [ ] PV-Überschuss (nur wenn du PV hast)
- [ ] LED-Beleuchtung (nur wenn vorhanden)
- [ ] Wassernachfüllung (nur wenn vorhanden)
- [ ] Digitale Eingänge (nur wenn genutzt)
- [ ] Erweiterungsmodule (nur wenn vorhanden)

Klicke **Weiter**

#### 4.4 Sensor-Auswahl
⚠️ **WICHTIG**:

**Option A - ALLE Sensoren (Empfohlen):**
- Lasse **ALLE Dropdown-Felder LEER**
- Wähle **NICHTS** aus
- Klicke einfach **Fertigstellen**
- → Es werden **ALLE verfügbaren Sensoren** erstellt (~156 Entitäten)

**Option B - Spezifische Sensoren:**
- Wähle nur die Sensor-Gruppen die du brauchst
- Zum Beispiel: PUMP, SOLAR, HEATER, onewire1-12, etc.
- Klicke **Fertigstellen**

### Schritt 5: Ergebnis prüfen

Nach dem Setup solltest du sehen:
- **~156 Entitäten** (bei Option A - alle Sensoren)
- **Firmware**: 1.1.8 (wird korrekt angezeigt)
- **Pumpe Binary Sensor**: ON (wenn PUMP=3)
- **Pumpe Switch**: ON (wenn PUMP=3)
- **Alle Temperatursensoren** (onewire1-12)
- **Chemie-Sensoren** (pH, ORP, Chlor)
- **System-Sensoren** (CPU-Temp, Memory, etc.)
- **Runtime-Sensoren**
- **Status-Sensoren**

## Warum nur neu laden NICHT funktioniert

Das Problem ist dass die alte Config `selected_sensors: []` enthält.
Selbst mit dem Fix wird diese alte Config weiterverwendet.
Nur eine **Neueinrichtung** erstellt eine frische Config mit `selected_sensors: None`.

## Nach der Neueinrichtung

### Pumpe sollte korrekt anzeigen:
- **PUMP**: 3 (Wert aus API)
- **PUMP Binary Sensor**: ON (interpretiert als STATE_MAP[3] = True)
- **PUMP Switch**: ON (interpretiert als STATE_MAP[3] = True)
- **PUMPSTATE**: "3|PUMP_ANTI_FREEZE" (erweiterte Info)

### Alle Sensoren sollten vorhanden sein:
- onewire1 bis onewire12 (Temperaturen)
- pH_value, orp_value, pot_value
- PUMP_RUNTIME, SOLAR_RUNTIME, etc.
- CPU_TEMP, SYSTEM_MEMORY, etc.
- Alle DOS_* Sensoren
- Alle EXT1_*, EXT2_* Sensoren
- Alle Timestamp-Sensoren

---

**Wenn du immer noch Probleme hast nach der Neueinrichtung, melde dich!**
