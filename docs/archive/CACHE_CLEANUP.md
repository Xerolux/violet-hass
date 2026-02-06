# 🧹 Cache Cleanup Instructions

## Problem

Wenn du den Fehler siehst:
```
Error occurred loading flow for integration violet_pool_controller:
cannot import name 'CONF_POOL_VOLUME' from 'custom_components.violet_pool_controller.const'
```

Das ist ein **Python Cache Problem**. Home Assistant hat alte `.pyc` Dateien die nicht mehr mit dem aktuellen Code übereinstimmen.

## Lösung

### Option 1: Home Assistant Neustart (Einfachste Methode)

1. Gehe zu **Einstellungen** → **System** → **Neu starten**
2. Warte bis Home Assistant vollständig neu gestartet ist
3. Versuche die Integration erneut einzurichten

### Option 2: Manuelle Cache-Bereinigung

Wenn Option 1 nicht funktioniert, lösche die Cache-Dateien manuell:

```bash
# SSH/Terminal-Zugriff auf Home Assistant:
rm -rf /config/custom_components/violet_pool_controller/__pycache__/
rm -f /config/custom_components/violet_pool_controller/*.pyc

# Dann Home Assistant neu starten
```

### Option 3: Integration neu installieren

1. **Einstellungen** → **Geräte & Dienste**
2. Finde "Violet Pool Controller"
3. Klicke auf die drei Punkte → **Löschen**
4. Home Assistant neu starten
5. Integration neu hinzufügen

## Warum passiert das?

Python erstellt `.pyc` Cache-Dateien für bessere Performance. Wenn der Code sich ändert (z.B. `CONF_POOL_VOLUME` → `CONF_POOL_SIZE`), aber die Cache-Dateien nicht gelöscht werden, versucht Python die alten Konstanten zu importieren.

## Verhindern

Die `.gitignore` enthält bereits `__pycache__/` und `*.pyc`, sodass diese Dateien nicht ins Repository commitet werden. Bei Updates sollte Home Assistant die Caches automatisch neu erstellen.

## Status der Fixes

Alle Commits auf dem Branch `claude/fix-violet-pool-logger-01GrXWMNUnsRLnJNm8477LZk` verwenden:
- ✅ `CONF_POOL_SIZE` (korrekt)
- ❌ `CONF_POOL_VOLUME` (existiert nicht mehr)

Wenn du den Branch pullst und Home Assistant neu startest, sollte alles funktionieren!
