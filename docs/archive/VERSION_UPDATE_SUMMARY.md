# Version Update Summary

## ✅ Automatische Versionsaktualisierung

Der Release-Workflow aktualisiert **automatisch** folgende Dateien bei jedem Release:

---

## 📝 Dateien die aktualisiert werden:

### 1. **manifest.json** ✅
**Pfad:** `custom_components/violet_pool_controller/manifest.json`

**Aktualisiert:**
```json
{
  "version": "1.0.7-alpha.1"  ← Wird automatisch gesetzt
}
```

**Warum wichtig:**
- Home Assistant liest Version aus manifest.json
- HACS nutzt diese für Update-Erkennung
- Integration-Version in UI wird angezeigt

---

### 2. **const.py** ✅
**Pfad:** `custom_components/violet_pool_controller/const.py`

**Aktualisiert:**
```python
INTEGRATION_VERSION = "1.0.7-alpha.1"  ← Wird automatisch gesetzt
```

**Warum wichtig:**
- Wird in Logs angezeigt
- Für Debugging und Support
- Wird in System-Info-Sensor angezeigt

---

### 3. **CLAUDE.md** ✅ NEU!
**Pfad:** `CLAUDE.md`

**Aktualisiert:**
```markdown
**Current Version**: `1.0.7-alpha.1` ← Wird automatisch gesetzt
```

**Warum wichtig:**
- Developer-Dokumentation bleibt aktuell
- Claude Code erkennt aktuelle Version
- Verhindert Verwirrung bei Entwicklung

---

### 4. **CHANGELOG.md** ✅
**Pfad:** `CHANGELOG.md`

**Aktualisiert:**
```markdown
## [1.0.7-alpha.1] - 2026-01-03

### ✨ New Features
- Feature 1
- Feature 2

### 🔧 Bug Fixes
- Fix 1
- Fix 2
```

**Warum wichtig:**
- Kumulativer History aller Releases
- Nutzer können alte Änderungen nachvollziehen
- Standard für Open-Source-Projekte

---

### 5. **RELEASE_NOTES.md** ✅
**Pfad:** `RELEASE_NOTES.md`

**Aktualisiert:**
```markdown
## v1.0.7-alpha.1 – Violet Pool Controller

🔴 **ALPHA RELEASE** - Experimental features, use with caution!

### ✨ New Features | Neue Funktionen
...
```

**Warum wichtig:**
- Enthält IMMER die neueste Version
- Wird auf GitHub Release-Seite angezeigt
- Quick Reference für aktuelle Features

---

## 🔄 Workflow-Prozess

### Schritt 1: Tag erstellen
```bash
git tag v1.0.7-alpha.1
git push origin v1.0.7-alpha.1
```

### Schritt 2: Workflow läuft automatisch
```
✅ Erkennt Version: 1.0.7-alpha.1
✅ Aktualisiert manifest.json
✅ Aktualisiert const.py
✅ Aktualisiert CLAUDE.md
✅ Generiert Release Notes
✅ Aktualisiert CHANGELOG.md
✅ Aktualisiert RELEASE_NOTES.md
✅ Erstellt ZIP + SHA256
✅ Committed Änderungen zurück
```

### Schritt 3: Automatischer Git Commit
```
Commit: "📝 Release v1.0.7-alpha.1 - Update changelog and version files"

Geänderte Dateien:
- CHANGELOG.md
- RELEASE_NOTES.md
- CLAUDE.md
- manifest.json
- const.py
```

---

## ⚙️ Technische Details

### Version-Extraktion
```bash
TAG="v1.0.7-alpha.1"
VERSION="${TAG#v}"  # Entfernt 'v' → "1.0.7-alpha.1"
```

### Update-Befehle
```bash
# manifest.json
sed -i 's|"version": "[^"]*"|"version": "1.0.7-alpha.1"|' manifest.json

# const.py
sed -i 's|^INTEGRATION_VERSION = .*|INTEGRATION_VERSION = "1.0.7-alpha.1"|' const.py

# CLAUDE.md
sed -i 's|**Current Version**: `[^*]*`|**Current Version**: `1.0.7-alpha.1`|' CLAUDE.md
```

---

## 📋 Aktuell in Dateien

**Stand: 2026-01-03**

| Datei | Aktuelle Version | Update-Methode |
|-------|------------------|----------------|
| `manifest.json` | `1.0.7-alpha.1` | ✅ Automatisch |
| `const.py` | `1.0.7-alpha.1` | ✅ Automatisch |
| `CLAUDE.md` | `1.0.7-alpha.1` | ✅ Automatisch |
| `CHANGELOG.md` | Alle Versionen | ✅ Automatisch |
| `RELEASE_NOTES.md` | Neueste Version | ✅ Automatisch |

---

## ❓ FAQ

### Q: Muss ich die Version manuell ändern?
**A:** Nein! Der Workflow macht das automatisch beim Tag-Push.

### Q: Was passiert, wenn ich die Version manuell ändere?
**A:** Der Workflow überschreibt sie beim nächsten Release.

### Q: Werden alle Dateien gleichzeitig aktualisiert?
**A:** Ja! Alle 5 Dateien werden im gleichen Commit aktualisiert.

### Q: Was ist, wenn CLAUDE.md nicht existiert?
**A:** Der Workflow prüft das und skippt das Update (kein Fehler).

### Q: Kann ich zusätzliche Dateien hinzufügen?
**A:** Ja! Füge sie einfach im Workflow unter "Update version in files" hinzu.

---

## 🎯 Beispiel: Release v1.0.8

### Vorher:
```
manifest.json:  "version": "1.0.7-alpha.1"
const.py:       INTEGRATION_VERSION = "1.0.7-alpha.1"
CLAUDE.md:      **Current Version**: `1.0.7-alpha.1`
```

### Tag pushen:
```bash
git tag v1.0.8
git push origin v1.0.8
```

### Nachher (automatisch):
```
manifest.json:  "version": "1.0.8"
const.py:       INTEGRATION_VERSION = "1.0.8"
CLAUDE.md:      **Current Version**: `1.0.8`
CHANGELOG.md:   ## [1.0.8] - 2026-01-03 (neu hinzugefügt)
RELEASE_NOTES.md: v1.0.8 Release Notes (überschrieben)
```

---

## ✅ Checkliste vor Release

- [ ] Alle Tests laufen durch
- [ ] Keine offenen kritischen Bugs
- [ ] Code ist auf `main` Branch gemerged
- [ ] Version-Format ist korrekt (SemVer 2.0.0)
- [ ] **NICHT** manuell Version in Dateien ändern!

Dann einfach:
```bash
git tag v1.0.8
git push origin v1.0.8
```

✅ **Der Rest passiert automatisch!**

---

## 🔍 Debugging

### Problem: Version wurde nicht aktualisiert

**Lösung 1: Check Workflow-Logs**
```
GitHub → Actions → Release Management → Workflow-Run
Suche nach: "✅ Updated version to X.Y.Z"
```

**Lösung 2: Manuelles Update (Notfall)**
```bash
# Nur wenn Workflow fehlschlägt:
VERSION="1.0.8"

# manifest.json
sed -i "s|\"version\": \"[^\"]*\"|\"version\": \"$VERSION\"|" custom_components/violet_pool_controller/manifest.json

# const.py
sed -i "s|^INTEGRATION_VERSION = .*|INTEGRATION_VERSION = \"$VERSION\"|" custom_components/violet_pool_controller/const.py

# CLAUDE.md
sed -i "s|**Current Version**: \`[^*]*\`|**Current Version**: \`$VERSION\`|" CLAUDE.md

git add .
git commit -m "fix: Manual version update to v$VERSION"
git push
```

---

## 📊 Version History

Der Workflow erstellt automatisch eine vollständige Version-History in CHANGELOG.md:

```markdown
# Changelog

## [1.0.8] - 2026-01-03
✨ New features...

## [1.0.7-alpha.1] - 2026-01-03
🔴 Alpha testing...

## [1.0.6] - 2026-01-02
🔧 Bug fixes...

## [1.0.5] - 2026-01-01
🚀 Improvements...
```

---

**Zusammenfassung:** 🎉

✅ **5 Dateien** werden automatisch aktualisiert
✅ **Kein manueller Aufwand** erforderlich
✅ **Konsistente Versionierung** überall
✅ **Git-History** wird automatisch gepflegt

**Simply push a tag, and everything is handled! 🚀**
