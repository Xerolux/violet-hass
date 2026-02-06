# 🚀 Violet Pool Card - Quick Start Guide

**Schnellstart für neue Sessions - Einfach Copy & Paste!**

---

## 📋 Pre-Session Checklist

Bevor du mit einer Development Session startest:

- [ ] VIOLET_CARD_ROADMAP.md gelesen
- [ ] Passende Session ausgewählt (1-10)
- [ ] Claude Code gestartet
- [ ] Session Prompt kopiert

---

## 🎯 Session 1: Repository Setup

### Copy-Paste Prompt:
```
Ich möchte eine Custom Lovelace Card für Home Assistant erstellen: "Violet Pool Card"

KONTEXT:
- Integration: Violet Pool Controller (violet_pool_controller)
- GitHub: https://github.com/YOUR_USERNAME/violet-pool-card
- Style: Mushroom Cards ähnlich
- Tech: Lit Element + TypeScript + Rollup

ZIEL:
Vollständiges Repository Setup mit HACS Kompatibilität

TASKS:
1. Repository Struktur erstellen (siehe VIOLET_CARD_ROADMAP.md)
2. package.json mit Dependencies
3. tsconfig.json
4. rollup.config.js
5. hacs.json
6. .gitignore
7. README.md mit Installation
8. Basis violet-pool-card.ts mit Card Registration
9. Build-System testen

WICHTIG:
- Verwende Code-Vorlagen aus VIOLET_CARD_ROADMAP.md
- HACS-kompatibel von Anfang an
- TypeScript strict mode
- ESLint konfigurieren

DELIVERABLES:
- ✅ npm install funktioniert
- ✅ npm run build erstellt dist/violet-pool-card.js
- ✅ Card registriert sich in HA
- ✅ README mit Installation
```

### Nach der Session:
```bash
# Testen
npm install
npm run build

# Git init
git init
git add .
git commit -m "🎉 Initial commit - Violet Pool Card setup"
git remote add origin https://github.com/YOUR_USERNAME/violet-pool-card.git
git push -u origin main
```

---

## 🎨 Session 2: Status Components

### Copy-Paste Prompt:
```
Weiter mit Violet Pool Card - Status Components

KONTEXT:
Repository aus Session 1 ist fertig. Jetzt Components bauen.

ZIEL:
Status-Anzeige Components für alle Card Types

TASKS:
1. Status Badge Component (src/components/status-badge.ts)
   - States: off, on, auto, manual, blocked, error
   - Farben aus VIOLET_CARD_ROADMAP.md
   - Icon Support (MDI)
   - Pulse Animation

2. Value Display Component (src/components/value-display.ts)
   - Temperatur (°C)
   - pH Wert (0-14)
   - ORP (mV)
   - Formatierung mit Unit
   - Min/Max Range Indicator

3. Detail Status Component (src/components/detail-status.ts)
   - Parse "3|PUMP_ANTI_FREEZE" → "Pump Anti Freeze"
   - Parse Arrays: ["BLOCKED_BY_TRESHOLDS", "TRESHOLDS_REACHED"]
   - Readable Formatting

4. Warning Chips Component (src/components/warning-chips.ts)
   - Multiple Warnings als Chips
   - Color-coded (Info/Warning/Error)
   - Dismissable optional

CODE VORLAGEN:
Verwende Code aus VIOLET_CARD_ROADMAP.md "Code Snippets" Section!

DELIVERABLES:
- ✅ Alle 4 Components funktionieren standalone
- ✅ Import in violet-pool-card.ts
- ✅ Storybook/Demo Page (optional)
```

### Testen:
```typescript
// In violet-pool-card.ts temporär testen:
protected render() {
  return html`
    <ha-card>
      <status-badge state="auto" label="AUTO"></status-badge>
      <value-display value="24.5" unit="°C"></value-display>
      <detail-status raw="3|PUMP_ANTI_FREEZE"></detail-status>
      <warning-chips warnings=${['BLOCKED_BY_TRESHOLDS']}></warning-chips>
    </ha-card>
  `;
}
```

---

## 🎚️ Session 3: Slider & Service Calls

### Copy-Paste Prompt:
```
Weiter mit Violet Pool Card - Slider Controls & Service Integration

KONTEXT:
Status Components sind fertig. Jetzt Steuerung implementieren.

ZIEL:
Funktionale Slider + Service Calls an Home Assistant

TASKS:
1. Slider Control Component (src/components/slider-control.ts)
   - Range Slider (continuous)
   - Discrete Slider (snap-to-value)
   - Touch-optimiert
   - Labels (optional)
   - Value Change Events
   - Live Update während Drag

2. Service Caller Utility (src/utils/service-caller.ts)
   - violet_pool_controller.control_pump
   - climate.set_temperature
   - number.set_value
   - switch.turn_on / turn_off
   - violet_pool_controller.smart_dosing
   - Error Handling
   - Toast Notifications

3. Entity Helper (src/utils/entity-helper.ts)
   - Get entity state
   - Parse attributes
   - Get PUMPSTATE detail (pipe-separated)
   - Get DOS_*_STATE (arrays)
   - Format values

CODE VORLAGEN:
VIOLET_CARD_ROADMAP.md enthält vollständige Implementierungen!

BEISPIEL INTEGRATION:
```typescript
// Pump Speed Slider
<slider-control
  .hass=${this.hass}
  entity="switch.violet_pool_pump"
  min="0"
  max="3"
  step="1"
  .labels=${['OFF', 'ECO', 'Normal', 'Boost']}
  @value-changed=${this._handleSpeedChange}
></slider-control>

private async _handleSpeedChange(e: CustomEvent) {
  const speed = e.detail.value;
  const caller = new ServiceCaller(this.hass);
  await caller.controlPump(this.config.entity, 'on', speed);
}
```

DELIVERABLES:
- ✅ Slider funktioniert
- ✅ Services werden aufgerufen
- ✅ Fehler werden behandelt
- ✅ Toast Notifications
```

### Live Test:
1. Card in HA laden
2. Slider bewegen
3. DevTools → Network → prüfe Service Call
4. Entity State sollte sich ändern

---

## ⚡ Session 4: Quick Actions

### Copy-Paste Prompt:
```
Weiter mit Violet Pool Card - Quick Action Buttons

KONTEXT:
Slider funktionieren. Jetzt Quick Actions für schnelle Steuerung.

ZIEL:
Button-Grid für häufige Aktionen (OFF/AUTO/ON, Speed Presets)

TASKS:
1. Quick Actions Component (src/components/quick-actions.ts)
   - Button Grid Layout
   - Icon + Label
   - Click Handler
   - Active State
   - Disabled State
   - Loading State

2. Action Types:
   - State Actions: OFF / AUTO / ON
   - Speed Presets: ECO / Normal / Boost
   - Manual Dosing: "Dosieren (30s)" Button
   - Custom Actions (tap_action config)

3. Confirmation Dialog (optional)
   - Bei kritischen Aktionen
   - "Wirklich ausschalten?"

CODE VORLAGE:
```typescript
interface QuickAction {
  icon: string;
  label: string;
  action: () => Promise<void>;
  active?: boolean;
  disabled?: boolean;
}

<quick-actions
  .actions=${[
    { icon: 'mdi:stop', label: 'OFF', action: () => this._turnOff() },
    { icon: 'mdi:auto-mode', label: 'AUTO', action: () => this._setAuto(), active: true },
    { icon: 'mdi:play', label: 'ON', action: () => this._turnOn() },
  ]}
></quick-actions>
```

DELIVERABLES:
- ✅ Quick Actions Component
- ✅ Integration in Cards
- ✅ Responsive Layout
- ✅ Feedback bei Click
```

---

## 🔵 Session 5-8: Card Types

### Session 5: Pump Card

```
Weiter mit Violet Pool Card - PUMP CARD implementieren

KONTEXT:
Components sind fertig. Jetzt erste vollständige Card.

REFERENZ MOCK-UP (VIOLET_CARD_ROADMAP.md):
┌─────────────────────────────────────────┐
│ 🔵 Pumpe              [AUTO] [Stufe 2] │
│ Status: Pump Anti Freeze                │
│ ━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ OFF        ECO      Normal      Boost   │
│ [OFF] [AUTO] [ECO] [Normal] [Boost]    │
│ ⏱️ Laufzeit: 2h 34min                   │
└─────────────────────────────────────────┘

ENTITY:
- switch.violet_pool_pump
- Attributes:
  - PUMPSTATE: "3|PUMP_ANTI_FREEZE"
  - PUMP_RPM_*: Speed values
  - runtime (optional)

TASKS:
1. Pump Card Class (src/cards/pump-card.ts)
2. Layout wie Mock-up
3. Status Badge (OFF/ON/AUTO/MANUAL)
4. Detail Status (Parse PUMPSTATE)
5. Speed Slider (0-3 mit Labels)
6. Quick Actions (OFF/AUTO/Speed Presets)
7. Runtime Counter (optional)
8. Icon Animation bei Betrieb

INTEGRATION:
```typescript
// In violet-pool-card.ts
case 'pump':
  return html`<pump-card .hass=${this.hass} .config=${this.config}></pump-card>`;
```

DELIVERABLES:
- ✅ Pump Card funktional
- ✅ Alle Features aus Mock-up
- ✅ Responsive
```

### Session 6-8: Weitere Cards
Analog zu Session 5, aber für:
- **Session 6**: Heater Card (climate.violet_pool_heater)
- **Session 7**: Solar Card (climate.violet_pool_solar)
- **Session 8**: Dosing Card (switch.violet_pool_dos_*)

Mock-ups in VIOLET_CARD_ROADMAP.md verwenden!

---

## 📊 Session 9: Overview & Compact

### Copy-Paste Prompt:
```
Weiter mit Violet Pool Card - OVERVIEW & COMPACT CARDS

KONTEXT:
Alle Detail-Cards (Pump, Heater, Solar, Dosing) sind fertig.

ZIEL:
- Overview Card: Alles auf einen Blick
- Compact Card: Minimale Dashboard-Ansicht

OVERVIEW CARD MOCK-UP:
┌─────────────────────────────────────────┐
│ 🏊 Pool Status                          │
│ 🌡️ 24.5°C  |  🧪 pH 7.2  |  ⚡ 650mV   │
│   ✅ OK        ✅ OK         ⚠️ Low     │
│ Aktive Geräte:                          │
│ 🔵 Pumpe (Auto, Stufe 2, Anti-Freeze)   │
│ ❌ Heizung (Blocked by Outside Temp)    │
│ 💧 Chlor (Blocked by Tresholds)        │
│ Warnungen:                              │
│ ⚠️ ORP zu niedrig - Chlor dosieren      │
└─────────────────────────────────────────┘

COMPACT CARD MOCK-UP:
┌─────────────────────────────────────────┐
│ 🔵 Pumpe        [AUTO] Stufe 2 (Anti-F) │
│ 🔥 Heizung      [AUTO] Blocked (14°C)   │
│ ☀️ Solar        [AUTO] Anti-Freeze      │
└─────────────────────────────────────────┘

TASKS:
1. Overview Card (src/cards/overview-card.ts)
   - Multi-entity Config
   - Wasserchemie Ampel (pH/ORP/Chlorine)
   - Temperatur-Übersicht
   - Aktive Geräte Liste
   - Warnungen prominent
   - Click → Details

2. Compact Card (src/cards/compact-card.ts)
   - Einzeilige Darstellung
   - Status Badge + Value + Detail
   - Click → Modal mit Full Card
   - Dashboard-optimiert

DELIVERABLES:
- ✅ Overview Card funktional
- ✅ Compact Card funktional
- ✅ Modal Dialog
- ✅ Responsive
```

---

## ✨ Session 10: Polish & Release

### Copy-Paste Prompt:
```
Weiter mit Violet Pool Card - FINAL POLISH & RELEASE

KONTEXT:
Alle Card Types funktionieren. Jetzt Production-Ready machen.

TASKS:
1. RESPONSIVE TESTING
   - Desktop (1920px) ✅
   - Tablet (768px) ✅
   - Mobile (375px) ✅

2. THEME SUPPORT
   - Dark Mode funktioniert
   - Light Mode funktioniert
   - Custom Theme Variables
   - CSS Variables nutzen

3. PERFORMANCE
   - Bundle Size < 100KB
   - Lazy Loading für Modal
   - Debounce Slider Updates
   - Optimize Re-renders

4. ACCESSIBILITY
   - ARIA Labels
   - Keyboard Navigation
   - Screen Reader Support
   - Focus States

5. DOCUMENTATION
   - README erweitern
   - Screenshots erstellen
   - Configuration Examples
   - Troubleshooting Section
   - CHANGELOG.md

6. TESTING
   - Test in HA 2024.1+
   - Test mit echtem Controller
   - Test alle Card Types
   - Test Theme Switching

7. GITHUB RELEASE
   - Tag v1.0.0
   - Release Notes
   - Dist files
   - Screenshots

8. HACS SUBMISSION
   - Fork HACS/default
   - Add Repository
   - PR erstellen

DELIVERABLES:
- ✅ Production-ready Code
- ✅ Vollständige Docs
- ✅ GitHub Release
- ✅ HACS verfügbar
```

### Release Checklist:
```bash
# Build
npm run build

# Version bump
npm version 1.0.0

# Git
git add .
git commit -m "🚀 Release v1.0.0"
git tag v1.0.0
git push origin main --tags

# GitHub Release erstellen
# - Tag: v1.0.0
# - Title: "🎉 Violet Pool Card v1.0.0"
# - Attach: dist/violet-pool-card.js
# - Release Notes aus CHANGELOG.md
```

---

## 🔧 Debugging Tipps

### Card lädt nicht
```javascript
// Browser Console
window.customCards
// Sollte violet-pool-card enthalten

// HA Developer Tools → States
// Prüfe ob Entities existieren
```

### Service Call schlägt fehl
```typescript
// In service-caller.ts
console.log('Calling service:', service, data);
```

### Styling Probleme
```css
/* DevTools → Elements → Computed */
/* Prüfe CSS Variables */
--primary-color
--primary-text-color
--card-background-color
```

---

## 📚 Nützliche Links

**Während Development:**
- Lit Playground: https://lit.dev/playground/
- MDI Icons: https://pictogrammers.com/library/mdi/
- HA Frontend Docs: https://developers.home-assistant.io/docs/frontend/

**Testing:**
- HA Dev Environment: http://localhost:8123
- Browser DevTools: F12
- HA Logs: Einstellungen → System → Logs

**Release:**
- HACS Docs: https://hacs.xyz/docs/publish/start
- GitHub Releases: https://docs.github.com/en/repositories/releasing-projects-on-github

---

## 🎯 Success Metrics

### Nach jeder Session prüfen:
- [ ] Code kompiliert ohne Errors
- [ ] ESLint clean (keine Warnings)
- [ ] TypeScript Errors: 0
- [ ] Card rendert in HA
- [ ] Funktionen testen

### Vor Release:
- [ ] Alle Card Types funktionieren
- [ ] Responsive auf allen Geräten
- [ ] Theme Support (Dark/Light)
- [ ] Bundle Size < 100KB
- [ ] README vollständig
- [ ] Screenshots vorhanden
- [ ] HACS-kompatibel

---

## 🚀 Los geht's!

**Next Step:**
1. Öffne neue Claude Code Session
2. Kopiere Session 1 Prompt (oben)
3. Paste & Enter
4. Follow the roadmap! 🎉

**Geschätzte Zeit:**
- Session 1-3: Je 2-3h (Setup & Components)
- Session 4-8: Je 2h (Cards)
- Session 9-10: Je 2-3h (Polish & Release)
- **Total: ~20-25 Stunden**

Viel Erfolg! 💪
