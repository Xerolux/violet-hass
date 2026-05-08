# 🎨 Violet Pool Controller Card - HACS Custom Lovelace Card
**Roadmap & Implementation Plan**

---

## 📋 Project Overview

### Goal
A dedicated, visually appealing Lovelace card for the Violet Pool Controller integration that presents all functions in a compact, user-friendly UI.

### Inspiration
- **Multiple Entity Row**: Compact multi-entity display
- **Mushroom Cards**: Modern, clean UI with icons
- **Better Sliders**: Intuitive slider controls

### Key Feature
**All-in-One Card per Entity**: Each entity (pump, heater, solar, dosing) gets its own card that:
- ✅ Displays current state (ON/OFF/AUTO/MANUAL)
- ✅ Visualizes blocking reasons (frost, outdoor temp, etc.)
- ✅ Controls speed/velocity (slider for pump)
- ✅ Sets target values (pH, ORP, temperature)
- ✅ Shows limits (Min/Max)
- ✅ Enables reading AND writing
- ✅ Responsive design (Desktop/Tablet/Mobile)

---

## 🎯 Features & Functions

### 1. **Pump Card** 🚀
```yaml
type: custom:violet-pool-card
entity: switch.violet_pool_pump
card_type: pump

Features:
  - Status Badge (OFF/ON/AUTO/MANUAL) with color
  - Detail status (e.g. "Pump Anti Freeze" at level 2)
  - Speed Slider (0-3) with labels (OFF/ECO/Normal/Boost)
  - Quick Actions: OFF / AUTO / ECO / Normal / Boost
  - Runtime Counter
  - Icon animation when running
```

**Visual Mock-up:**
```
┌─────────────────────────────────────────┐
│ 🔵 Pump              [AUTO] [Level 2]  │
│                                         │
│ Status: Pump Anti Freeze                │
│                                         │
│ ━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ OFF        ECO      Normal      Boost   │
│                                         │
│ [OFF] [AUTO] [ECO] [Normal] [Boost]    │
│                                         │
│ ⏱️ Runtime: 2h 34min                    │
└─────────────────────────────────────────┘
```

### 2. **Heater Card** 🔥
```yaml
type: custom:violet-pool-card
entity: climate.violet_pool_heater
card_type: heater

Features:
  - Status Badge (OFF/HEAT/AUTO)
  - Blocking reason (e.g. "Blocked By Outside Temp")
  - Target temperature slider (18-35°C)
  - Current temperature displayed large
  - Outdoor temperature indicator
  - Quick Actions: OFF / AUTO / HEAT
```

**Visual Mock-up:**
```
┌─────────────────────────────────────────┐
│ 🔥 Heater            [AUTO] [Blocked]   │
│                                         │
│ 🌡️ 24.5°C → 26.0°C                     │
│                                         │
│ Status: Blocked By Outside Temp         │
│ Outdoor: 14.0°C (Min: 14.5°C)          │
│                                         │
│ Target: ━━━━━━━●━━━━━━━━━━━━━━━━━━━━━━━ │
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
  - Detail status (e.g. "Solar Anti Freeze")
  - Absorber temperature vs pool temperature
  - Target temperature slider
  - Temperature difference display
  - Quick Actions: OFF / AUTO / ON
```

**Visual Mock-up:**
```
┌─────────────────────────────────────────┐
│ ☀️ Solar              [AUTO] [OFF]      │
│                                         │
│ 🌡️ Pool: 24.5°C  Absorber: 18.3°C      │
│ Δ -6.2°C (too cold for heating)         │
│                                         │
│ Status: Solar Anti Freeze               │
│                                         │
│ Target: ━━━━━━━●━━━━━━━━━━━━━━━━━━━━━━━ │
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
  - Status Badge (OFF/ON/AUTO) with blocking reasons
  - Current value (ORP/pH) displayed large
  - Target value slider
  - Limits (Min/Max) visualized
  - Dosing quantity history
  - Blocking reasons as chips
  - Quick Actions: OFF / AUTO / Manual Dose
```

**Visual Mock-up (Chlorine):**
```
┌─────────────────────────────────────────┐
│ 💧 Chlorine Dosing    [AUTO] [Blocked]  │
│                                         │
│ 🧪 650.5 mV → 700 mV                    │
│                                         │
│ ⚠️ Blocked By Thresholds               │
│ ⚠️ Thresholds Reached                   │
│                                         │
│ Target: ━━━━━━━━━━━●━━━━━━━━━━━━━━━━━━━ │
│      600mV        700mV          800mV  │
│                                         │
│ Min: 650mV  |  Max: 750mV              │
│                                         │
│ [OFF] [AUTO] [Dose (30s)]              │
│                                         │
│ 📊 Last 24h: 450ml                      │
└─────────────────────────────────────────┘
```

**Visual Mock-up (pH):**
```
┌─────────────────────────────────────────┐
│ 🧪 pH- Dosing         [AUTO] [Active]   │
│                                         │
│ 📊 7.8 → 7.2                            │
│                                         │
│ ✅ OK - Active Dosing                   │
│                                         │
│ Target: ━━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│      6.8          7.2              7.8  │
│                                         │
│ Min: 7.0  |  Max: 7.4                  │
│                                         │
│ [OFF] [AUTO] [Dose (30s)]              │
│                                         │
│ 📊 Last 24h: 120ml                      │
└─────────────────────────────────────────┘
```

### 5. **Overview Card** 📊
```yaml
type: custom:violet-pool-card
card_type: overview

Features:
  - All important statuses at a glance
  - Water chemistry (pH, ORP, Chlorine) with traffic light
  - Temperatures (Pool, Solar, Heater)
  - Active devices with icons
  - Warnings/Blockages prominent
  - Quick actions for all devices
```

**Visual Mock-up:**
```
┌─────────────────────────────────────────┐
│ 🏊 Pool Status                          │
│                                         │
│ 🌡️ 24.5°C  |  🧪 pH 7.2  |  ⚡ 650mV   │
│   ✅ OK        ✅ OK         ⚠️ Low     │
│                                         │
│ Active Devices:                          │
│ 🔵 Pump (Auto, Level 2, Anti-Freeze)    │
│ ❌ Heater (Blocked by Outside Temp)     │
│ ❌ Solar (Anti-Freeze)                  │
│ 💧 Chlorine (Blocked by Thresholds)    │
│ ✅ pH- (Active Dosing)                  │
│                                         │
│ Warnings:                                │
│ ⚠️ ORP too low - Dose chlorine           │
│ ℹ️ Frost protection active (14°C)       │
└─────────────────────────────────────────┘
```

### 6. **Compact Card** (for Dashboards)
```yaml
type: custom:violet-pool-card
entity: switch.violet_pool_pump
card_type: compact
show_controls: false  # Status only, no controls

Features:
  - One line per entity
  - Status Badge + Value + Detail
  - Click → Modal with full card
  - Perfect for overview dashboards
```

**Visual Mock-up:**
```
┌─────────────────────────────────────────┐
│ 🔵 Pump        [AUTO] Level 2 (Anti-F) │
│ 🔥 Heater      [AUTO] Blocked (14°C)   │
│ ☀️ Solar        [AUTO] Anti-Freeze      │
│ 💧 Chlorine    [AUTO] Blocked (650mV)  │
│ 🧪 pH-          [AUTO] Active (7.8)     │
└─────────────────────────────────────────┘
```

---

## 🏗️ Technical Architecture

### Repository Structure
```
violet-pool-card/
├── src/
│   ├── violet-pool-card.ts          # Main card class
│   ├── cards/
│   │   ├── pump-card.ts              # Pump-specific card
│   │   ├── heater-card.ts            # Heater-specific card
│   │   ├── solar-card.ts             # Solar-specific card
│   │   ├── dosing-card.ts            # Dosing-specific card
│   │   ├── overview-card.ts          # Overview card
│   │   └── compact-card.ts           # Compact card
│   ├── components/
│   │   ├── status-badge.ts           # Status Badge component
│   │   ├── slider-control.ts         # Slider component
│   │   ├── quick-actions.ts          # Quick Action buttons
│   │   ├── value-display.ts          # Value display component
│   │   ├── detail-status.ts          # Detail status component
│   │   └── warning-chips.ts          # Warning chips component
│   ├── utils/
│   │   ├── entity-helper.ts          # Entity state helper
│   │   ├── service-caller.ts         # HA service calls
│   │   ├── formatter.ts              # Value formatting
│   │   └── icons.ts                  # Icon mappings
│   └── styles/
│       ├── card-styles.ts            # Card styling
│       ├── theme-support.ts          # HA theme integration
│       └── animations.ts             # Animations
├── dist/                             # Build output
├── hacs.json                         # HACS configuration
├── package.json
├── tsconfig.json
├── rollup.config.js
└── README.md
```

### Technology Stack

**Framework & Build:**
- **Lit** (like Mushroom) - Modern Web Components
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

### Color Scheme (based on state)

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
  low: '#2196F3',           // Blue (low)
  normal: '#4CAF50',        // Green (optimal)
  high: '#FF9800',          // Orange (high)
  critical: '#F44336',      // Red (critical)
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

### Animations

```scss
// Icon spin when running
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.pump-running .icon {
  animation: spin 2s linear infinite;
}

// Pulsing for warnings
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.warning-badge {
  animation: pulse 2s ease-in-out infinite;
}

// Slide-in for details
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

### Phase 1: Setup & Skeleton (Session 1)
**Duration**: ~2-3 hours

**Tasks:**
1. ✅ Create repository (`violet-pool-card`)
2. ✅ Set up build system (Rollup + TypeScript)
3. ✅ Create HACS manifest (`hacs.json`)
4. ✅ Implement base card class
5. ✅ Prepare theme integration
6. ✅ README with installation instructions

**Deliverables:**
- Working repository
- Minimal card that renders
- HACS-compatible
- Build system works

---

### Phase 2: Status Badge & Display (Session 2)
**Duration**: ~2-3 hours

**Tasks:**
1. ✅ Status Badge Component
   - OFF/ON/AUTO/MANUAL states
   - Color coding
   - Icon support
2. ✅ Value Display Component
   - Display current values
   - Formatting (temperature, pH, mV)
   - Min/Max indicators
3. ✅ Detail Status Component
   - Parse pipe-separated strings
   - Display blocking reasons
   - Represent array states
4. ✅ Warning Chips Component
   - Dosing state arrays
   - Multiple warnings
   - Dismissable optional

**Deliverables:**
- Status badge works
- Values displayed correctly
- Detail status is parsed
- Warnings visible

---

### Phase 3: Slider Controls (Session 3)
**Duration**: ~2-3 hours

**Tasks:**
1. ✅ Slider Control Component
   - Touch-optimized
   - Snap-to-value (Speed 0-3)
   - Range slider (temperature)
   - Show labels
2. ✅ Implement Service Caller
   - `violet_pool_controller.control_pump`
   - `climate.set_temperature`
   - `number.set_value`
   - Error handling
3. ✅ Live update on changes
   - Entity state subscription
   - Optimistic UI updates
   - Debouncing

**Deliverables:**
- Slider functional
- Values can be changed
- HA services are called
- UI updates live

---

### Phase 4: Quick Actions (Session 4)
**Duration**: ~2 hours

**Tasks:**
1. ✅ Quick Action Buttons
   - OFF / AUTO / ON
   - Speed Presets (ECO/Normal/Boost)
   - Manual Dosing
   - Icon + Label
2. ✅ Action Confirmation
   - Optional confirm dialog
   - Toast notifications
   - Error messages
3. ✅ Tap Actions
   - tap_action
   - hold_action
   - double_tap_action

**Deliverables:**
- Buttons work
- Services are called
- Feedback for user
- Customizable actions

---

### Phase 5: Implement Card Types (Session 5-8)
**Duration**: ~4-6 hours

**Session 5: Pump Card**
1. ✅ Pump Card Layout
2. ✅ Speed Slider Integration
3. ✅ Runtime Counter
4. ✅ Detail Status (Anti-Freeze)

**Session 6: Heater Card**
1. ✅ Temperature Display
2. ✅ Target Temperature Slider
3. ✅ Outside Temperature Indicator
4. ✅ Blocking Display

**Session 7: Solar Card**
1. ✅ Absorber vs Pool Temp
2. ✅ Delta Calculation
3. ✅ Target Temperature
4. ✅ Anti-Freeze Status

**Session 8: Dosing Card**
1. ✅ Current Value (pH/ORP)
2. ✅ Target Slider
3. ✅ Min/Max limits
4. ✅ Blocking reasons
5. ✅ Manual Dosing Button
6. ✅ History Graph (optional)

**Deliverables:**
- All card types functional
- Specific features per type
- Responsive design
- Error handling

---

### Phase 6: Overview & Compact Cards (Session 9)
**Duration**: ~2-3 hours

**Tasks:**
1. ✅ Overview Card
   - All entities at a glance
   - Water chemistry traffic light
   - Active devices list
   - Warnings prominent
2. ✅ Compact Card
   - Minimal display
   - Click → Modal
   - Dashboard-optimized

**Deliverables:**
- Overview Card functional
- Compact Card functional
- Modal dialog for details
- Dashboard integration

---

### Phase 7: Polish & Release (Session 10)
**Duration**: ~2-3 hours

**Tasks:**
1. ✅ Test responsive design
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
   - Bundle Size optimization
5. ✅ Documentation
   - Expand README
   - Screenshots
   - Configuration Examples
   - Troubleshooting
6. ✅ HACS Submission
   - Repository tags
   - GitHub Release
   - Add to HACS Default

**Deliverables:**
- Production-ready card
- Complete documentation
- HACS-available
- Release v1.0.0

---

## 📝 Code Snippets for Quick Start

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
I want to create a Custom Lovelace Card for Home Assistant: "Violet Pool Card"

Goal: HACS-compatible card for the Violet Pool Controller integration

Setup:
- Repository Name: violet-pool-card
- Technology: Lit Element + TypeScript + Rollup
- Template: Mushroom Cards style

Please create:
1. Complete folder structure
2. package.json with all dependencies
3. tsconfig.json
4. rollup.config.js
5. hacs.json
6. Base violet-pool-card.ts with card registration
7. README.md with installation instructions

Use reference files from VIOLET_CARD_ROADMAP.md!
```

### Session 2: Status Components
```
Continue with Violet Pool Card - Implement Status Components

Tasks:
1. Status Badge Component (src/components/status-badge.ts)
   - States: OFF/ON/AUTO/MANUAL/BLOCKED/ERROR
   - Color coding as in roadmap
   - Icon support
   - Pulse animation optional

2. Value Display Component (src/components/value-display.ts)
   - Temperature, pH, mV formatting
   - Min/Max indicators
   - Trend arrow (optional)

3. Detail Status Component (src/components/detail-status.ts)
   - Parse "3|PUMP_ANTI_FREEZE" → "Pump Anti Freeze"
   - Display array states ["BLOCKED_BY_TRESHOLDS", ...]

4. Warning Chips Component (src/components/warning-chips.ts)
   - Multiple warnings as chips
   - Color-coded (Info/Warning/Error)

Use code from VIOLET_CARD_ROADMAP.md "Code Snippets" section!
```

### Session 3: Slider & Controls
```
Continue with Violet Pool Card - Slider Controls

Tasks:
1. Implement Slider Control Component (src/components/slider-control.ts)
   - Touch-optimized
   - Labels support
   - Value change events
   - Snap-to-value for discrete values

2. Service Caller Utility (src/utils/service-caller.ts)
   - control_pump service
   - set_temperature service
   - set_value service
   - Error handling

3. Entity Helper (src/utils/entity-helper.ts)
   - Get state from entity
   - Parse attributes
   - Get detail status from PUMPSTATE etc.

Use code templates in VIOLET_CARD_ROADMAP.md!
```

### Session 4: Quick Actions
```
Continue with Violet Pool Card - Quick Action Buttons

Tasks:
1. Quick Actions Component (src/components/quick-actions.ts)
   - Button Grid Layout
   - Icon + Label
   - Click handler
   - Disabled state

2. Action Integration
   - OFF / AUTO / ON Buttons
   - Speed Presets (Pump)
   - Manual Dosing Button
   - Confirmation dialog (optional)

3. Toast Notifications
   - Success messages
   - Error messages
   - HA toast integration

Reference: Mushroom Cards Button style
```

### Session 5: Pump Card
```
Continue with Violet Pool Card - Implement Pump Card

Tasks:
1. Pump Card Class (src/cards/pump-card.ts)
   - Layout as in mock-up
   - Status Badge integration
   - Speed Slider (0-3)
   - Labels: OFF/ECO/Normal/Boost
   - Quick Actions: OFF/AUTO/ECO/Normal/Boost
   - Runtime Counter
   - Detail Status (Anti-Freeze)

Entity Example:
- switch.violet_pool_pump
- Attributes: PUMPSTATE, PUMP_RPM_*, runtime

Use mock-up and code in VIOLET_CARD_ROADMAP.md!
```

### Session 6: Heater Card
```
Continue with Violet Pool Card - Implement Heater Card

Tasks:
1. Heater Card Class (src/cards/heater-card.ts)
   - Layout as in mock-up
   - Temperature display large
   - Target temperature slider (18-35°C)
   - Outdoor temp indicator
   - Blocking status
   - Quick Actions: OFF/AUTO/HEAT

Entity Example:
- climate.violet_pool_heater
- Attributes: HEATERSTATE, current_temperature, temperature, etc.

Use mock-up in VIOLET_CARD_ROADMAP.md!
```

### Session 7: Solar Card
```
Continue with Violet Pool Card - Implement Solar Card

Tasks:
1. Solar Card Class (src/cards/solar-card.ts)
   - Layout as in mock-up
   - Pool temp vs absorber temp
   - Delta calculation
   - Target temperature slider
   - Anti-Freeze status
   - Quick Actions: OFF/AUTO/ON

Entity Example:
- climate.violet_pool_solar
- Sensors: onewire1_value (Pool), onewire3_value (Absorber)
- Attributes: SOLARSTATE

Use mock-up in VIOLET_CARD_ROADMAP.md!
```

### Session 8: Dosing Card
```
Continue with Violet Pool Card - Implement Dosing Card

Tasks:
1. Dosing Card Class (src/cards/dosing-card.ts)
   - Layout as in mock-up
   - Current value display (pH/ORP/Chlorine)
   - Target slider
   - Min/Max limits
   - Blocking reasons as chips
   - Manual dosing button
   - History (optional)

Entity Examples:
- switch.violet_pool_dos_1_cl (Chlorine)
- sensor.violet_pool_orp_value
- number.violet_pool_target_orp
- Attributes: DOS_1_CL_STATE (array)

Dosing types: chlorine, ph_minus, ph_plus, flocculant

Use mock-ups in VIOLET_CARD_ROADMAP.md!
```

### Session 9: Overview & Compact
```
Continue with Violet Pool Card - Overview & Compact Cards

Tasks:
1. Overview Card (src/cards/overview-card.ts)
   - All entities at a glance
   - Water chemistry traffic light (pH/ORP/Chlorine)
   - Temperatures
   - Active devices list
   - Warnings prominent

2. Compact Card (src/cards/compact-card.ts)
   - One line per entity
   - Status Badge + Value + Detail
   - Click → Modal with full card
   - Dashboard-optimized

Use mock-ups in VIOLET_CARD_ROADMAP.md!
```

### Session 10: Polish & Release
```
Continue with Violet Pool Card - Final Polish & Release

Tasks:
1. Test responsive design
   - Desktop (1920px)
   - Tablet (768px)
   - Mobile (375px)

2. Theme Support
   - Test Dark Mode
   - Test Light Mode
   - Custom Theme Variables

3. Performance
   - Optimize bundle size
   - Lazy Loading
   - Debouncing

4. Documentation
   - Expand README
   - Create screenshots
   - Configuration Examples
   - Troubleshooting Section

5. HACS Release
   - Create GitHub Release
   - Tag v1.0.0
   - HACS Default Submission

Use checklist in VIOLET_CARD_ROADMAP.md!
```

---

## ✅ Success Criteria

### Functional Requirements
- ✅ All card types (Pump, Heater, Solar, Dosing, Overview, Compact) work
- ✅ Status badges display correct states
- ✅ Sliders can change values
- ✅ Quick Actions call HA services
- ✅ Detail status is parsed (pipe-separated, arrays)
- ✅ Responsive on all devices
- ✅ Theme support (Dark/Light)

### Quality Requirements
- ✅ TypeScript without errors
- ✅ ESLint clean
- ✅ Bundle Size < 100KB
- ✅ Works with HA 2024.1+
- ✅ HACS-compatible
- ✅ Documentation complete

### User Experience
- ✅ Intuitive operation
- ✅ Smooth animations
- ✅ Clear error messages
- ✅ Feedback on actions
- ✅ Accessibility (ARIA, Keyboard)

---

## 🚀 Ready to Start!

This roadmap contains EVERYTHING you need:
1. ✅ Complete technical specification
2. ✅ Design mock-ups for all card types
3. ✅ Code templates for copy-paste
4. ✅ Session-by-session prompts
5. ✅ Build system configuration
6. ✅ HACS integration guide

**Next Step:**
Simply copy the Session 1 prompt and paste it into a new Claude Code session! 🎉

---

**Created**: 2026-01-04
**For**: Violet Pool Controller HACS Card
**Status**: Ready to Implement
**Estimated Total Duration**: 20-25 hours (10 sessions à 2-3h)
