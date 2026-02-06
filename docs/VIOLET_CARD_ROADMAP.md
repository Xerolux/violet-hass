# 🎨 Violet Pool Controller Card - HACS Custom Lovelace Card
**Roadmap & Implementation Plan**

---

## 📋 Projekt-Übersicht

### Ziel
Eine dedizierte, visuell ansprechende Lovelace Card für die Violet Pool Controller Integration, die alle Funktionen in einer kompakten, benutzerfreundlichen UI darstellt.

### Inspiration
- **Multiple Entity Row**: Kompakte Multi-Entity-Darstellung
- **Mushroom Cards**: Moderne, cleane UI mit Icons
- **Better Sliders**: Intuitive Slider-Steuerung

### Besonderheit
**All-in-One Card pro Entity**: Jede Entität (Pumpe, Heizung, Solar, Dosierung) bekommt eine eigene Card, die:
- ✅ Aktuellen State anzeigt (ON/OFF/AUTO/MANUAL)
- ✅ Blockierungsgründe visualisiert (Frost, Außentemp, etc.)
- ✅ Speed/Geschwindigkeit steuert (Slider für Pumpe)
- ✅ Zielwerte einstellt (pH, ORP, Temperatur)
- ✅ Grenzwerte anzeigt (Min/Max)
- ✅ Lesen UND Schreiben ermöglicht
- ✅ Responsive Design (Desktop/Tablet/Mobile)

---

## 🎯 Features & Funktionen

### 1. **Pump Card** 🚀
```yaml
type: custom:violet-pool-card
entity: switch.violet_pool_pump
card_type: pump

Features:
  - Status Badge (OFF/ON/AUTO/MANUAL) mit Farbe
  - Detail-Status (z.B. "Pump Anti Freeze" in Stufe 2)
  - Speed Slider (0-3) mit Labels (OFF/ECO/Normal/Boost)
  - Quick Actions: OFF / AUTO / ECO / Normal / Boost
  - Runtime Counter
  - Icon Animation bei Betrieb
```

**Visual Mock-up:**
```
┌─────────────────────────────────────────┐
│ 🔵 Pumpe              [AUTO] [Stufe 2] │
│                                         │
│ Status: Pump Anti Freeze                │
│                                         │
│ ━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ OFF        ECO      Normal      Boost   │
│                                         │
│ [OFF] [AUTO] [ECO] [Normal] [Boost]    │
│                                         │
│ ⏱️ Laufzeit: 2h 34min                   │
└─────────────────────────────────────────┘
```

### 2. **Heater Card** 🔥
```yaml
type: custom:violet-pool-card
entity: climate.violet_pool_heater
card_type: heater

Features:
  - Status Badge (OFF/HEAT/AUTO)
  - Blockierungsgrund (z.B. "Blocked By Outside Temp")
  - Zieltemperatur Slider (18-35°C)
  - Aktuelle Temperatur groß angezeigt
  - Außentemperatur Indikator
  - Quick Actions: OFF / AUTO / HEAT
```

**Visual Mock-up:**
```
┌─────────────────────────────────────────┐
│ 🔥 Heizung            [AUTO] [Blocked]  │
│                                         │
│ 🌡️ 24.5°C → 26.0°C                     │
│                                         │
│ Status: Blocked By Outside Temp         │
│ Außen: 14.0°C (Min: 14.5°C)            │
│                                         │
│ Ziel: ━━━━━━━●━━━━━━━━━━━━━━━━━━━━━━━ │
│      18°C          26°C            35°C │
│                                         │
│ [OFF] [AUTO] [HEAT]                     │
└─────────────────────────────────────────┘
```

### 3. **Solar Card** ☀️
```yaml
type: custom:violet-pool-card
entity: climate.violet_pool_solar
card_type: solar

Features:
  - Status Badge (OFF/ON/AUTO)
  - Detail-Status (z.B. "Solar Anti Freeze")
  - Absorber-Temperatur vs Pool-Temperatur
  - Zieltemperatur Slider
  - Temperatur-Differenz Anzeige
  - Quick Actions: OFF / AUTO / ON
```

**Visual Mock-up:**
```
┌─────────────────────────────────────────┐
│ ☀️ Solar              [AUTO] [OFF]      │
│                                         │
│ 🌡️ Pool: 24.5°C  Absorber: 18.3°C      │
│ Δ -6.2°C (zu kalt für Heizen)          │
│                                         │
│ Status: Solar Anti Freeze               │
│                                         │
│ Ziel: ━━━━━━━●━━━━━━━━━━━━━━━━━━━━━━━ │
│      18°C          25°C            32°C │
│                                         │
│ [OFF] [AUTO] [ON]                       │
└─────────────────────────────────────────┘
```

### 4. **Dosing Card** 💧
```yaml
type: custom:violet-pool-card
entity: switch.violet_pool_dos_1_cl
card_type: dosing
dosing_type: chlorine  # or ph_minus, ph_plus, flocculant

Features:
  - Status Badge (OFF/ON/AUTO) mit Blockierungsgründen
  - Aktueller Wert (ORP/pH) groß angezeigt
  - Zielwert Slider
  - Grenzwerte (Min/Max) visualisiert
  - Dosiermengen-History
  - Blockierungsgründe als Chips
  - Quick Actions: OFF / AUTO / Manual Dose
```

**Visual Mock-up (Chlor):**
```
┌─────────────────────────────────────────┐
│ 💧 Chlor Dosierung    [AUTO] [Blocked]  │
│                                         │
│ 🧪 650.5 mV → 700 mV                    │
│                                         │
│ ⚠️ Blocked By Tresholds                │
│ ⚠️ Tresholds Reached                   │
│                                         │
│ Ziel: ━━━━━━━━━━━●━━━━━━━━━━━━━━━━━━━ │
│      600mV        700mV          800mV  │
│                                         │
│ Min: 650mV  |  Max: 750mV              │
│                                         │
│ [OFF] [AUTO] [Dosieren (30s)]          │
│                                         │
│ 📊 Letzte 24h: 450ml                    │
└─────────────────────────────────────────┘
```

**Visual Mock-up (pH):**
```
┌─────────────────────────────────────────┐
│ 🧪 pH- Dosierung      [AUTO] [Active]   │
│                                         │
│ 📊 7.8 → 7.2                            │
│                                         │
│ ✅ OK - Aktive Dosierung                │
│                                         │
│ Ziel: ━━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│      6.8          7.2              7.8  │
│                                         │
│ Min: 7.0  |  Max: 7.4                  │
│                                         │
│ [OFF] [AUTO] [Dosieren (30s)]          │
│                                         │
│ 📊 Letzte 24h: 120ml                    │
└─────────────────────────────────────────┘
```

### 5. **Overview Card** 📊
```yaml
type: custom:violet-pool-card
card_type: overview

Features:
  - Alle wichtigen Status auf einen Blick
  - Wasserchemie (pH, ORP, Chlor) mit Ampel
  - Temperaturen (Pool, Solar, Heizung)
  - Aktive Geräte mit Icons
  - Warnungen/Blockierungen prominent
  - Quick Actions für alle Geräte
```

**Visual Mock-up:**
```
┌─────────────────────────────────────────┐
│ 🏊 Pool Status                          │
│                                         │
│ 🌡️ 24.5°C  |  🧪 pH 7.2  |  ⚡ 650mV   │
│   ✅ OK        ✅ OK         ⚠️ Low     │
│                                         │
│ Aktive Geräte:                          │
│ 🔵 Pumpe (Auto, Stufe 2, Anti-Freeze)   │
│ ❌ Heizung (Blocked by Outside Temp)    │
│ ❌ Solar (Anti-Freeze)                  │
│ 💧 Chlor (Blocked by Tresholds)        │
│ ✅ pH- (Active Dosing)                  │
│                                         │
│ Warnungen:                              │
│ ⚠️ ORP zu niedrig - Chlor dosieren      │
│ ℹ️ Frostschutz aktiv (14°C)            │
└─────────────────────────────────────────┘
```

### 6. **Compact Card** (für Dashboards)
```yaml
type: custom:violet-pool-card
entity: switch.violet_pool_pump
card_type: compact
show_controls: false  # Nur Status, keine Steuerung

Features:
  - Eine Zeile pro Entity
  - Status Badge + Wert + Detail
  - Click → Modal mit Full Card
  - Perfekt für Übersichts-Dashboards
```

**Visual Mock-up:**
```
┌─────────────────────────────────────────┐
│ 🔵 Pumpe        [AUTO] Stufe 2 (Anti-F) │
│ 🔥 Heizung      [AUTO] Blocked (14°C)   │
│ ☀️ Solar        [AUTO] Anti-Freeze      │
│ 💧 Chlor        [AUTO] Blocked (650mV)  │
│ 🧪 pH-          [AUTO] Active (7.8)     │
└─────────────────────────────────────────┘
```

---

## 🏗️ Technische Architektur

### Repository Struktur
```
violet-pool-card/
├── src/
│   ├── violet-pool-card.ts          # Main card class
│   ├── cards/
│   │   ├── pump-card.ts              # Pump-spezifische Card
│   │   ├── heater-card.ts            # Heater-spezifische Card
│   │   ├── solar-card.ts             # Solar-spezifische Card
│   │   ├── dosing-card.ts            # Dosing-spezifische Card
│   │   ├── overview-card.ts          # Overview Card
│   │   └── compact-card.ts           # Compact Card
│   ├── components/
│   │   ├── status-badge.ts           # Status Badge Component
│   │   ├── slider-control.ts         # Slider Component
│   │   ├── quick-actions.ts          # Quick Action Buttons
│   │   ├── value-display.ts          # Wert-Anzeige Component
│   │   ├── detail-status.ts          # Detail-Status Component
│   │   └── warning-chips.ts          # Warning Chips Component
│   ├── utils/
│   │   ├── entity-helper.ts          # Entity State Helper
│   │   ├── service-caller.ts         # HA Service Aufrufe
│   │   ├── formatter.ts              # Wert-Formatierung
│   │   └── icons.ts                  # Icon Mappings
│   └── styles/
│       ├── card-styles.ts            # Card Styling
│       ├── theme-support.ts          # HA Theme Integration
│       └── animations.ts             # Animationen
├── dist/                             # Build Output
├── hacs.json                         # HACS Configuration
├── package.json
├── tsconfig.json
├── rollup.config.js
└── README.md
```

### Technologie-Stack

**Framework & Build:**
- **Lit** (wie Mushroom) - Moderne Web Components
- **TypeScript** - Type Safety
- **Rollup** - Bundling
- **SCSS** - Styling

**Dependencies:**
```json
{
  "dependencies": {
    "lit": "^3.1.0",
    "home-assistant-js-websocket": "^9.1.0"
  },
  "devDependencies": {
    "@rollup/plugin-node-resolve": "^15.2.0",
    "@rollup/plugin-typescript": "^11.1.0",
    "rollup": "^4.9.0",
    "typescript": "^5.3.0",
    "rollup-plugin-terser": "^7.0.2",
    "rollup-plugin-serve": "^2.0.2"
  }
}
```

### Card Configuration Schema

```typescript
interface VioletPoolCardConfig {
  type: 'custom:violet-pool-card';
  entity: string;
  card_type: 'pump' | 'heater' | 'solar' | 'dosing' | 'overview' | 'compact';

  // Optional
  name?: string;
  icon?: string;
  show_state?: boolean;
  show_detail_status?: boolean;
  show_controls?: boolean;
  show_runtime?: boolean;
  show_history?: boolean;
  dosing_type?: 'chlorine' | 'ph_minus' | 'ph_plus' | 'flocculant';

  // Styling
  theme?: string;
  accent_color?: string;
  icon_color?: string;

  // Advanced
  tap_action?: ActionConfig;
  hold_action?: ActionConfig;
  double_tap_action?: ActionConfig;
}
```

---

## 🎨 Design System

### Farbschema (basierend auf State)

```typescript
const STATE_COLORS = {
  // Pump/Switch States
  off: '#757575',           // Gray
  on: '#4CAF50',            // Green
  auto: '#2196F3',          // Blue
  manual: '#FF9800',        // Orange
  error: '#F44336',         // Red
  blocked: '#FFC107',       // Amber

  // Status Indicators
  ok: '#4CAF50',            // Green
  warning: '#FF9800',       // Orange
  critical: '#F44336',      // Red

  // Value Ranges
  low: '#2196F3',           // Blue (niedrig)
  normal: '#4CAF50',        // Green (optimal)
  high: '#FF9800',          // Orange (hoch)
  critical: '#F44336',      // Red (kritisch)
};
```

### Icons (Material Design Icons)

```typescript
const ICONS = {
  pump: 'mdi:pump',
  heater: 'mdi:radiator',
  solar: 'mdi:solar-power',
  chlorine: 'mdi:flask-outline',
  ph_minus: 'mdi:flask-minus',
  ph_plus: 'mdi:flask-plus',
  flocculant: 'mdi:flask',

  // States
  auto: 'mdi:auto-mode',
  manual: 'mdi:hand-back-right',
  blocked: 'mdi:alert-circle',
  frost: 'mdi:snowflake',

  // Actions
  play: 'mdi:play',
  pause: 'mdi:pause',
  stop: 'mdi:stop',
  speed: 'mdi:speedometer',

  // Values
  temperature: 'mdi:thermometer',
  ph: 'mdi:ph',
  orp: 'mdi:flash',
  chlorine_level: 'mdi:test-tube',
};
```

### Animationen

```scss
// Icon Spin bei Betrieb
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.pump-running .icon {
  animation: spin 2s linear infinite;
}

// Pulsing bei Warnung
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.warning-badge {
  animation: pulse 2s ease-in-out infinite;
}

// Slide-in für Details
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

## 🔧 Implementation Steps

### Phase 1: Setup & Grundgerüst (Session 1)
**Dauer**: ~2-3 Stunden

**Tasks:**
1. ✅ Repository erstellen (`violet-pool-card`)
2. ✅ Build-System einrichten (Rollup + TypeScript)
3. ✅ HACS Manifest (`hacs.json`) erstellen
4. ✅ Basis Card-Klasse implementieren
5. ✅ Theme Integration vorbereiten
6. ✅ README mit Installation-Anleitung

**Deliverables:**
- Funktionierendes Repository
- Minimale Card die rendert
- HACS-kompatibel
- Build-System funktioniert

---

### Phase 2: Status Badge & Display (Session 2)
**Dauer**: ~2-3 Stunden

**Tasks:**
1. ✅ Status Badge Component
   - OFF/ON/AUTO/MANUAL States
   - Farbcodierung
   - Icon Support
2. ✅ Value Display Component
   - Aktuelle Werte anzeigen
   - Formatierung (Temperatur, pH, mV)
   - Min/Max Indicators
3. ✅ Detail Status Component
   - Pipe-separierte Strings parsen
   - Blockierungsgründe anzeigen
   - Array-States darstellen
4. ✅ Warning Chips Component
   - Dosing State Arrays
   - Multiple Warnungen
   - Dismissable optional

**Deliverables:**
- Status Badge funktioniert
- Werte werden korrekt angezeigt
- Detail-Status wird geparst
- Warnungen sichtbar

---

### Phase 3: Slider Controls (Session 3)
**Dauer**: ~2-3 Stunden

**Tasks:**
1. ✅ Slider Control Component
   - Touch-optimiert
   - Snap-to-value (Speed 0-3)
   - Range Slider (Temperatur)
   - Labels anzeigen
2. ✅ Service Caller implementieren
   - `violet_pool_controller.control_pump`
   - `climate.set_temperature`
   - `number.set_value`
   - Error Handling
3. ✅ Live-Update auf Änderungen
   - Entity State Subscription
   - Optimistic UI Updates
   - Debouncing

**Deliverables:**
- Slider funktional
- Werte können geändert werden
- HA Services werden aufgerufen
- UI aktualisiert sich live

---

### Phase 4: Quick Actions (Session 4)
**Dauer**: ~2 Stunden

**Tasks:**
1. ✅ Quick Action Buttons
   - OFF / AUTO / ON
   - Speed Presets (ECO/Normal/Boost)
   - Manual Dosing
   - Icon + Label
2. ✅ Action Confirmation
   - Optional Confirm Dialog
   - Toast Notifications
   - Error Messages
3. ✅ Tap Actions
   - tap_action
   - hold_action
   - double_tap_action

**Deliverables:**
- Buttons funktionieren
- Services werden aufgerufen
- Feedback für User
- Customizable Actions

---

### Phase 5: Card Types implementieren (Session 5-8)
**Dauer**: ~4-6 Stunden

**Session 5: Pump Card**
1. ✅ Pump Card Layout
2. ✅ Speed Slider Integration
3. ✅ Runtime Counter
4. ✅ Detail Status (Anti-Freeze)

**Session 6: Heater Card**
1. ✅ Temperature Display
2. ✅ Target Temperature Slider
3. ✅ Outside Temperature Indicator
4. ✅ Blockierung Anzeige

**Session 7: Solar Card**
1. ✅ Absorber vs Pool Temp
2. ✅ Delta Calculation
3. ✅ Target Temperature
4. ✅ Anti-Freeze Status

**Session 8: Dosing Card**
1. ✅ Current Value (pH/ORP)
2. ✅ Target Slider
3. ✅ Min/Max Grenzwerte
4. ✅ Blockierungsgründe
5. ✅ Manual Dosing Button
6. ✅ History Graph (optional)

**Deliverables:**
- Alle Card Types funktional
- Spezifische Features pro Type
- Responsive Design
- Fehlerbehandlung

---

### Phase 6: Overview & Compact Cards (Session 9)
**Dauer**: ~2-3 Stunden

**Tasks:**
1. ✅ Overview Card
   - Alle Entities auf einen Blick
   - Wasserchemie-Ampel
   - Aktive Geräte Liste
   - Warnungen prominent
2. ✅ Compact Card
   - Minimale Darstellung
   - Click → Modal
   - Dashboard-optimiert

**Deliverables:**
- Overview Card funktional
- Compact Card funktional
- Modal Dialog für Details
- Dashboard-Integration

---

### Phase 7: Polish & Release (Session 10)
**Dauer**: ~2-3 Stunden

**Tasks:**
1. ✅ Responsive Design testen
   - Desktop (1920px)
   - Tablet (768px)
   - Mobile (375px)
2. ✅ Theme Support
   - Dark Mode
   - Light Mode
   - Custom Themes
3. ✅ Accessibility
   - ARIA Labels
   - Keyboard Navigation
   - Screen Reader Support
4. ✅ Performance
   - Lazy Loading
   - Debouncing
   - Bundle Size Optimierung
5. ✅ Documentation
   - README erweitern
   - Screenshots
   - Configuration Examples
   - Troubleshooting
6. ✅ HACS Submission
   - Repository Tags
   - GitHub Release
   - HACS Default aufnehmen

**Deliverables:**
- Produktionsreife Card
- Vollständige Dokumentation
- HACS-verfügbar
- Release v1.0.0

---

## 📝 Code Snippets für schnellen Start

### 1. Main Card Class (src/violet-pool-card.ts)

```typescript
import { LitElement, html, css, TemplateResult } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { HomeAssistant, LovelaceCardConfig } from 'custom-card-helpers';

import { PumpCard } from './cards/pump-card';
import { HeaterCard } from './cards/heater-card';
import { SolarCard } from './cards/solar-card';
import { DosingCard } from './cards/dosing-card';
import { OverviewCard } from './cards/overview-card';
import { CompactCard } from './cards/compact-card';

export interface VioletPoolCardConfig extends LovelaceCardConfig {
  type: string;
  entity: string;
  card_type: 'pump' | 'heater' | 'solar' | 'dosing' | 'overview' | 'compact';
  name?: string;
  icon?: string;
  show_state?: boolean;
  show_detail_status?: boolean;
  show_controls?: boolean;
  dosing_type?: 'chlorine' | 'ph_minus' | 'ph_plus' | 'flocculant';
}

@customElement('violet-pool-card')
export class VioletPoolCard extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @state() private config!: VioletPoolCardConfig;

  public setConfig(config: VioletPoolCardConfig): void {
    if (!config.entity) {
      throw new Error('You need to define an entity');
    }
    if (!config.card_type) {
      throw new Error('You need to define a card_type');
    }
    this.config = config;
  }

  protected render(): TemplateResult {
    if (!this.config || !this.hass) {
      return html``;
    }

    const entity = this.hass.states[this.config.entity];
    if (!entity) {
      return html`
        <ha-card>
          <div class="error">Entity ${this.config.entity} not found</div>
        </ha-card>
      `;
    }

    switch (this.config.card_type) {
      case 'pump':
        return html`<pump-card .hass=${this.hass} .config=${this.config}></pump-card>`;
      case 'heater':
        return html`<heater-card .hass=${this.hass} .config=${this.config}></heater-card>`;
      case 'solar':
        return html`<solar-card .hass=${this.hass} .config=${this.config}></solar-card>`;
      case 'dosing':
        return html`<dosing-card .hass=${this.hass} .config=${this.config}></dosing-card>`;
      case 'overview':
        return html`<overview-card .hass=${this.hass} .config=${this.config}></overview-card>`;
      case 'compact':
        return html`<compact-card .hass=${this.hass} .config=${this.config}></compact-card>`;
      default:
        return html`
          <ha-card>
            <div class="error">Unknown card_type: ${this.config.card_type}</div>
          </ha-card>
        `;
    }
  }

  static get styles() {
    return css`
      .error {
        display: block;
        color: var(--error-color);
        padding: 16px;
      }
    `;
  }

  public getCardSize(): number {
    return 3;
  }

  public static getConfigElement() {
    return document.createElement('violet-pool-card-editor');
  }

  public static getStubConfig(): VioletPoolCardConfig {
    return {
      type: 'custom:violet-pool-card',
      entity: 'switch.violet_pool_pump',
      card_type: 'pump',
    };
  }
}

// Register card for card picker
(window as any).customCards = (window as any).customCards || [];
(window as any).customCards.push({
  type: 'violet-pool-card',
  name: 'Violet Pool Card',
  description: 'Custom card for Violet Pool Controller',
  preview: true,
});
```

### 2. Status Badge Component (src/components/status-badge.ts)

```typescript
import { LitElement, html, css, TemplateResult } from 'lit';
import { customElement, property } from 'lit/decorators.js';

export type BadgeState = 'off' | 'on' | 'auto' | 'manual' | 'blocked' | 'error';

const STATE_CONFIG = {
  off: { color: '#757575', icon: 'mdi:stop', label: 'OFF' },
  on: { color: '#4CAF50', icon: 'mdi:play', label: 'ON' },
  auto: { color: '#2196F3', icon: 'mdi:auto-mode', label: 'AUTO' },
  manual: { color: '#FF9800', icon: 'mdi:hand-back-right', label: 'MANUAL' },
  blocked: { color: '#FFC107', icon: 'mdi:alert-circle', label: 'BLOCKED' },
  error: { color: '#F44336', icon: 'mdi:alert', label: 'ERROR' },
};

@customElement('status-badge')
export class StatusBadge extends LitElement {
  @property() public state!: BadgeState;
  @property() public label?: string;
  @property({ type: Boolean }) public pulse = false;

  protected render(): TemplateResult {
    const config = STATE_CONFIG[this.state] || STATE_CONFIG.off;
    const displayLabel = this.label || config.label;

    return html`
      <div class="badge ${this.state} ${this.pulse ? 'pulse' : ''}"
           style="--badge-color: ${config.color}">
        <ha-icon icon="${config.icon}"></ha-icon>
        <span>${displayLabel}</span>
      </div>
    `;
  }

  static get styles() {
    return css`
      .badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 12px;
        border-radius: 12px;
        background: var(--badge-color);
        color: white;
        font-size: 12px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .badge ha-icon {
        --mdc-icon-size: 16px;
      }

      .badge.pulse {
        animation: pulse 2s ease-in-out infinite;
      }

      @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
      }
    `;
  }
}
```

### 3. Slider Control Component (src/components/slider-control.ts)

```typescript
import { LitElement, html, css, TemplateResult } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { HomeAssistant } from 'custom-card-helpers';

@customElement('slider-control')
export class SliderControl extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @property() public entity!: string;
  @property({ type: Number }) public min = 0;
  @property({ type: Number }) public max = 100;
  @property({ type: Number }) public step = 1;
  @property({ type: Number }) public value = 0;
  @property() public unit = '';
  @property({ type: Array }) public labels?: string[];

  @state() private isDragging = false;

  private _handleChange(e: Event) {
    const value = Number((e.target as HTMLInputElement).value);
    this.value = value;

    this.dispatchEvent(new CustomEvent('value-changed', {
      detail: { value },
      bubbles: true,
      composed: true,
    }));
  }

  protected render(): TemplateResult {
    const percentage = ((this.value - this.min) / (this.max - this.min)) * 100;

    return html`
      <div class="slider-container">
        <div class="value-display">
          ${this.value}${this.unit}
        </div>

        <div class="slider-wrapper">
          <input
            type="range"
            min="${this.min}"
            max="${this.max}"
            step="${this.step}"
            .value="${this.value.toString()}"
            @input="${this._handleChange}"
            @mousedown="${() => this.isDragging = true}"
            @mouseup="${() => this.isDragging = false}"
            @touchstart="${() => this.isDragging = true}"
            @touchend="${() => this.isDragging = false}"
            style="--percentage: ${percentage}%"
          />

          ${this.labels ? html`
            <div class="labels">
              ${this.labels.map(label => html`<span>${label}</span>`)}
            </div>
          ` : ''}
        </div>
      </div>
    `;
  }

  static get styles() {
    return css`
      .slider-container {
        width: 100%;
      }

      .value-display {
        text-align: center;
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 12px;
        color: var(--primary-text-color);
      }

      .slider-wrapper {
        position: relative;
        padding: 8px 0;
      }

      input[type="range"] {
        width: 100%;
        height: 6px;
        -webkit-appearance: none;
        appearance: none;
        background: linear-gradient(
          to right,
          var(--primary-color) 0%,
          var(--primary-color) var(--percentage),
          var(--disabled-text-color) var(--percentage),
          var(--disabled-text-color) 100%
        );
        border-radius: 3px;
        outline: none;
        cursor: pointer;
      }

      input[type="range"]::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: var(--primary-color);
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
      }

      input[type="range"]::-moz-range-thumb {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: var(--primary-color);
        cursor: pointer;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
      }

      .labels {
        display: flex;
        justify-content: space-between;
        margin-top: 8px;
        font-size: 12px;
        color: var(--secondary-text-color);
      }
    `;
  }
}
```

### 4. Service Caller Utility (src/utils/service-caller.ts)

```typescript
import { HomeAssistant } from 'custom-card-helpers';

export class ServiceCaller {
  constructor(private hass: HomeAssistant) {}

  async controlPump(
    entity: string,
    action: 'on' | 'off' | 'auto',
    speed?: number,
    duration?: number
  ): Promise<void> {
    await this.hass.callService('violet_pool_controller', 'control_pump', {
      entity_id: entity,
      action,
      speed,
      duration,
    });
  }

  async setTemperature(entity: string, temperature: number): Promise<void> {
    await this.hass.callService('climate', 'set_temperature', {
      entity_id: entity,
      temperature,
    });
  }

  async setNumberValue(entity: string, value: number): Promise<void> {
    await this.hass.callService('number', 'set_value', {
      entity_id: entity,
      value,
    });
  }

  async turnOn(entity: string): Promise<void> {
    const domain = entity.split('.')[0];
    await this.hass.callService(domain, 'turn_on', {
      entity_id: entity,
    });
  }

  async turnOff(entity: string): Promise<void> {
    const domain = entity.split('.')[0];
    await this.hass.callService(domain, 'turn_off', {
      entity_id: entity,
    });
  }

  async manualDosing(
    dosingType: string,
    duration: number
  ): Promise<void> {
    await this.hass.callService('violet_pool_controller', 'smart_dosing', {
      dosing_type: dosingType,
      duration,
      action: 'on',
    });
  }
}
```

### 5. HACS Manifest (hacs.json)

```json
{
  "name": "Violet Pool Card",
  "hacs": "1.6.0",
  "render_readme": true,
  "filename": "violet-pool-card.js",
  "homeassistant": "2024.1.0"
}
```

### 6. Package.json

```json
{
  "name": "violet-pool-card",
  "version": "1.0.0",
  "description": "Custom Lovelace card for Violet Pool Controller",
  "main": "dist/violet-pool-card.js",
  "repository": {
    "type": "git",
    "url": "https://github.com/YOUR_USERNAME/violet-pool-card.git"
  },
  "keywords": [
    "home-assistant",
    "lovelace",
    "custom-card",
    "pool",
    "violet"
  ],
  "author": "Your Name",
  "license": "MIT",
  "scripts": {
    "build": "rollup -c",
    "watch": "rollup -c --watch",
    "serve": "rollup -c --watch --environment SERVE"
  },
  "dependencies": {
    "custom-card-helpers": "^1.9.0",
    "home-assistant-js-websocket": "^9.1.0",
    "lit": "^3.1.0"
  },
  "devDependencies": {
    "@rollup/plugin-node-resolve": "^15.2.0",
    "@rollup/plugin-typescript": "^11.1.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.0.0",
    "rollup": "^4.9.0",
    "rollup-plugin-serve": "^2.0.2",
    "rollup-plugin-terser": "^7.0.2",
    "typescript": "^5.3.0"
  }
}
```

### 7. Rollup Config (rollup.config.js)

```javascript
import typescript from '@rollup/plugin-typescript';
import resolve from '@rollup/plugin-node-resolve';
import { terser } from 'rollup-plugin-terser';
import serve from 'rollup-plugin-serve';

const dev = process.env.ROLLUP_WATCH || process.env.SERVE;

export default {
  input: 'src/violet-pool-card.ts',
  output: {
    file: 'dist/violet-pool-card.js',
    format: 'es',
    sourcemap: dev ? true : false,
  },
  plugins: [
    resolve(),
    typescript(),
    !dev && terser(),
    dev && serve({
      contentBase: ['./dist'],
      host: '0.0.0.0',
      port: 5000,
      allowCrossOrigin: true,
      headers: {
        'Access-Control-Allow-Origin': '*',
      },
    }),
  ].filter(Boolean),
};
```

---

## 📚 Resources & Links

### Inspiration Projects
- **Mushroom Cards**: https://github.com/piitaya/lovelace-mushroom
- **Better Sliders**: https://github.com/phischdev/lovelace-mushroom-better-sliders
- **Multiple Entity Row**: https://github.com/benct/lovelace-multiple-entity-row
- **Mini Graph Card**: https://github.com/kalkih/mini-graph-card
- **Button Card**: https://github.com/custom-cards/button-card

### Documentation
- **Lit Element**: https://lit.dev/
- **HA Custom Cards**: https://developers.home-assistant.io/docs/frontend/custom-ui/lovelace-custom-card
- **HACS Integration**: https://hacs.xyz/docs/publish/start
- **Custom Card Helpers**: https://github.com/custom-cards/custom-card-helpers

### Tools
- **Rollup**: https://rollupjs.org/
- **TypeScript**: https://www.typescriptlang.org/
- **Material Design Icons**: https://pictogrammers.com/library/mdi/

---

## 🎯 Session-by-Session Copy-Paste Prompts

### Session 1: Initial Setup
```
Ich möchte eine Custom Lovelace Card für Home Assistant erstellen: "Violet Pool Card"

Ziel: HACS-kompatible Card für die Violet Pool Controller Integration

Setup:
- Repository Name: violet-pool-card
- Technologie: Lit Element + TypeScript + Rollup
- Vorlage: Mushroom Cards Style

Bitte erstelle:
1. Vollständige Ordnerstruktur
2. package.json mit allen Dependencies
3. tsconfig.json
4. rollup.config.js
5. hacs.json
6. Basis violet-pool-card.ts mit card registration
7. README.md mit Installation-Anleitung

Referenz-Dateien aus VIOLET_CARD_ROADMAP.md verwenden!
```

### Session 2: Status Components
```
Weiter mit Violet Pool Card - Status Components implementieren

Tasks:
1. Status Badge Component (src/components/status-badge.ts)
   - States: OFF/ON/AUTO/MANUAL/BLOCKED/ERROR
   - Farbcodierung wie in Roadmap
   - Icon Support
   - Pulse Animation optional

2. Value Display Component (src/components/value-display.ts)
   - Temperatur, pH, mV Formatierung
   - Min/Max Indicators
   - Trend Arrow (optional)

3. Detail Status Component (src/components/detail-status.ts)
   - Parse "3|PUMP_ANTI_FREEZE" → "Pump Anti Freeze"
   - Array States ["BLOCKED_BY_TRESHOLDS", ...] anzeigen

4. Warning Chips Component (src/components/warning-chips.ts)
   - Multiple Warnungen als Chips
   - Color-coded (Info/Warning/Error)

Verwende Code aus VIOLET_CARD_ROADMAP.md Section "Code Snippets"!
```

### Session 3: Slider & Controls
```
Weiter mit Violet Pool Card - Slider Controls

Tasks:
1. Slider Control Component implementieren (src/components/slider-control.ts)
   - Touch-optimiert
   - Labels support
   - Value change events
   - Snap-to-value für discrete values

2. Service Caller Utility (src/utils/service-caller.ts)
   - control_pump Service
   - set_temperature Service
   - set_value Service
   - Error Handling

3. Entity Helper (src/utils/entity-helper.ts)
   - Get state from entity
   - Parse attributes
   - Get detail status from PUMPSTATE etc.

Code-Vorlagen in VIOLET_CARD_ROADMAP.md verwenden!
```

### Session 4: Quick Actions
```
Weiter mit Violet Pool Card - Quick Action Buttons

Tasks:
1. Quick Actions Component (src/components/quick-actions.ts)
   - Button Grid Layout
   - Icon + Label
   - Click Handler
   - Disabled State

2. Action Integration
   - OFF / AUTO / ON Buttons
   - Speed Presets (Pump)
   - Manual Dosing Button
   - Confirmation Dialog (optional)

3. Toast Notifications
   - Success Messages
   - Error Messages
   - HA Toast Integration

Referenz: Mushroom Cards Button Style
```

### Session 5: Pump Card
```
Weiter mit Violet Pool Card - Pump Card implementieren

Tasks:
1. Pump Card Class (src/cards/pump-card.ts)
   - Layout wie in Mock-up
   - Status Badge Integration
   - Speed Slider (0-3)
   - Labels: OFF/ECO/Normal/Boost
   - Quick Actions: OFF/AUTO/ECO/Normal/Boost
   - Runtime Counter
   - Detail Status (Anti-Freeze)

Entity Example:
- switch.violet_pool_pump
- Attributes: PUMPSTATE, PUMP_RPM_*, runtime

Mock-up und Code in VIOLET_CARD_ROADMAP.md verwenden!
```

### Session 6: Heater Card
```
Weiter mit Violet Pool Card - Heater Card implementieren

Tasks:
1. Heater Card Class (src/cards/heater-card.ts)
   - Layout wie in Mock-up
   - Temperature Display groß
   - Target Temperature Slider (18-35°C)
   - Outside Temp Indicator
   - Blockierung Status
   - Quick Actions: OFF/AUTO/HEAT

Entity Example:
- climate.violet_pool_heater
- Attributes: HEATERSTATE, current_temperature, temperature, etc.

Mock-up in VIOLET_CARD_ROADMAP.md verwenden!
```

### Session 7: Solar Card
```
Weiter mit Violet Pool Card - Solar Card implementieren

Tasks:
1. Solar Card Class (src/cards/solar-card.ts)
   - Layout wie in Mock-up
   - Pool Temp vs Absorber Temp
   - Delta Calculation
   - Target Temperature Slider
   - Anti-Freeze Status
   - Quick Actions: OFF/AUTO/ON

Entity Example:
- climate.violet_pool_solar
- Sensors: onewire1_value (Pool), onewire3_value (Absorber)
- Attributes: SOLARSTATE

Mock-up in VIOLET_CARD_ROADMAP.md verwenden!
```

### Session 8: Dosing Card
```
Weiter mit Violet Pool Card - Dosing Card implementieren

Tasks:
1. Dosing Card Class (src/cards/dosing-card.ts)
   - Layout wie in Mock-up
   - Current Value Display (pH/ORP/Chlorine)
   - Target Slider
   - Min/Max Grenzwerte
   - Blockierungsgründe als Chips
   - Manual Dosing Button
   - History (optional)

Entity Examples:
- switch.violet_pool_dos_1_cl (Chlor)
- sensor.violet_pool_orp_value
- number.violet_pool_target_orp
- Attributes: DOS_1_CL_STATE (Array)

Dosing Types: chlorine, ph_minus, ph_plus, flocculant

Mock-ups in VIOLET_CARD_ROADMAP.md verwenden!
```

### Session 9: Overview & Compact
```
Weiter mit Violet Pool Card - Overview & Compact Cards

Tasks:
1. Overview Card (src/cards/overview-card.ts)
   - Alle Entities auf einen Blick
   - Wasserchemie Ampel (pH/ORP/Chlorine)
   - Temperaturen
   - Aktive Geräte Liste
   - Warnungen prominent

2. Compact Card (src/cards/compact-card.ts)
   - Eine Zeile pro Entity
   - Status Badge + Value + Detail
   - Click → Modal mit Full Card
   - Dashboard-optimiert

Mock-ups in VIOLET_CARD_ROADMAP.md verwenden!
```

### Session 10: Polish & Release
```
Weiter mit Violet Pool Card - Final Polish & Release

Tasks:
1. Responsive Design testen
   - Desktop (1920px)
   - Tablet (768px)
   - Mobile (375px)

2. Theme Support
   - Dark Mode testen
   - Light Mode testen
   - Custom Theme Variablen

3. Performance
   - Bundle Size optimieren
   - Lazy Loading
   - Debouncing

4. Documentation
   - README erweitern
   - Screenshots erstellen
   - Configuration Examples
   - Troubleshooting Section

5. HACS Release
   - GitHub Release erstellen
   - Tag v1.0.0
   - HACS Default Submission

Checkliste in VIOLET_CARD_ROADMAP.md verwenden!
```

---

## ✅ Success Criteria

### Funktionale Anforderungen
- ✅ Alle Card Types (Pump, Heater, Solar, Dosing, Overview, Compact) funktionieren
- ✅ Status Badges zeigen korrekte States an
- ✅ Sliders können Werte ändern
- ✅ Quick Actions rufen HA Services auf
- ✅ Detail Status wird geparst (Pipe-separated, Arrays)
- ✅ Responsive auf allen Geräten
- ✅ Theme Support (Dark/Light)

### Qualitätsanforderungen
- ✅ TypeScript ohne Errors
- ✅ ESLint clean
- ✅ Bundle Size < 100KB
- ✅ Funktioniert mit HA 2024.1+
- ✅ HACS-kompatibel
- ✅ Dokumentation vollständig

### User Experience
- ✅ Intuitive Bedienung
- ✅ Smooth Animationen
- ✅ Klare Fehlermeldungen
- ✅ Feedback bei Actions
- ✅ Accessibility (ARIA, Keyboard)

---

## 🚀 Ready to Start!

Diese Roadmap enthält ALLES was du brauchst:
1. ✅ Vollständige technische Spezifikation
2. ✅ Design Mock-ups für alle Card Types
3. ✅ Code-Vorlagen zum Copy-Paste
4. ✅ Session-by-Session Prompts
5. ✅ Build-System Configuration
6. ✅ HACS Integration Guide

**Nächster Schritt:**
Einfach Session 1 Prompt kopieren und in einer neuen Claude Code Session einfügen! 🎉

---

**Erstellt**: 2026-01-04
**Für**: Violet Pool Controller HACS Card
**Status**: Ready to Implement
**Geschätzte Gesamtdauer**: 20-25 Stunden (10 Sessions à 2-3h)
