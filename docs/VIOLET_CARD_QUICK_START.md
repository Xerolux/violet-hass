# 🚀 Violet Pool Card - Quick Start Guide

**Quick start for new sessions - Just Copy & Paste!**

---

## 📋 Pre-Session Checklist

Before starting a development session:

- [ ] Read VIOLET_CARD_ROADMAP.md
- [ ] Select appropriate session (1-10)
- [ ] Start Claude Code
- [ ] Copy session prompt

---

## 🎯 Session 1: Repository Setup

### Copy-Paste Prompt:
```
I want to create a Custom Lovelace Card for Home Assistant: "Violet Pool Card"

CONTEXT:
- Integration: Violet Pool Controller (violet_pool_controller)
- GitHub: https://github.com/YOUR_USERNAME/violet-pool-card
- Style: Similar to Mushroom Cards
- Tech: Lit Element + TypeScript + Rollup

GOAL:
Complete repository setup with HACS compatibility

TASKS:
1. Create repository structure (see VIOLET_CARD_ROADMAP.md)
2. package.json with dependencies
3. tsconfig.json
4. rollup.config.js
5. hacs.json
6. .gitignore
7. README.md with installation
8. Base violet-pool-card.ts with card registration
9. Test build system

IMPORTANT:
- Use code templates from VIOLET_CARD_ROADMAP.md
- HACS-compatible from the start
- TypeScript strict mode
- Configure ESLint

DELIVERABLES:
- ✅ npm install works
- ✅ npm run build creates dist/violet-pool-card.js
- ✅ Card registers in HA
- ✅ README with installation
```

### After the Session:
```bash
# Test
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
Continue with Violet Pool Card - Status Components

CONTEXT:
Repository from Session 1 is ready. Now build components.

GOAL:
Status display components for all card types

TASKS:
1. Status Badge Component (src/components/status-badge.ts)
   - States: off, on, auto, manual, blocked, error
   - Colors from VIOLET_CARD_ROADMAP.md
   - Icon Support (MDI)
   - Pulse Animation

2. Value Display Component (src/components/value-display.ts)
   - Temperature (°C)
   - pH value (0-14)
   - ORP (mV)
   - Formatting with unit
   - Min/Max range indicator

3. Detail Status Component (src/components/detail-status.ts)
   - Parse "3|PUMP_ANTI_FREEZE" → "Pump Anti Freeze"
   - Parse arrays: ["BLOCKED_BY_TRESHOLDS", "TRESHOLDS_REACHED"]
   - Readable formatting

4. Warning Chips Component (src/components/warning-chips.ts)
   - Multiple warnings as chips
   - Color-coded (Info/Warning/Error)
   - Dismissable optional

CODE TEMPLATES:
Use code from VIOLET_CARD_ROADMAP.md "Code Snippets" section!

DELIVERABLES:
- ✅ All 4 components work standalone
- ✅ Import in violet-pool-card.ts
- ✅ Storybook/Demo page (optional)
```

### Testing:
```typescript
// Test temporarily in violet-pool-card.ts:
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
Continue with Violet Pool Card - Slider Controls & Service Integration

CONTEXT:
Status Components are ready. Now implement controls.

GOAL:
Functional sliders + service calls to Home Assistant

TASKS:
1. Slider Control Component (src/components/slider-control.ts)
   - Range Slider (continuous)
   - Discrete Slider (snap-to-value)
   - Touch-optimized
   - Labels (optional)
   - Value change events
   - Live update during drag

2. Service Caller Utility (src/utils/service-caller.ts)
   - violet_pool_controller.control_pump
   - climate.set_temperature
   - number.set_value
   - switch.turn_on / turn_off
   - violet_pool_controller.smart_dosing
   - Error handling
   - Toast notifications

3. Entity Helper (src/utils/entity-helper.ts)
   - Get entity state
   - Parse attributes
   - Get PUMPSTATE detail (pipe-separated)
   - Get DOS_*_STATE (arrays)
   - Format values

CODE TEMPLATES:
VIOLET_CARD_ROADMAP.md contains complete implementations!

EXAMPLE INTEGRATION:
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
- ✅ Slider works
- ✅ Services are called
- ✅ Errors are handled
- ✅ Toast notifications
```

### Live Test:
1. Load card in HA
2. Move slider
3. DevTools → Network → check service call
4. Entity state should change

---

## ⚡ Session 4: Quick Actions

### Copy-Paste Prompt:
```
Continue with Violet Pool Card - Quick Action Buttons

CONTEXT:
Sliders work. Now Quick Actions for fast control.

GOAL:
Button grid for common actions (OFF/AUTO/ON, Speed Presets)

TASKS:
1. Quick Actions Component (src/components/quick-actions.ts)
   - Button Grid Layout
   - Icon + Label
   - Click handler
   - Active state
   - Disabled state
   - Loading state

2. Action Types:
   - State Actions: OFF / AUTO / ON
   - Speed Presets: ECO / Normal / Boost
   - Manual Dosing: "Dose (30s)" Button
   - Custom Actions (tap_action config)

3. Confirmation Dialog (optional)
   - For critical actions
   - "Really turn off?"

CODE TEMPLATE:
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
- ✅ Feedback on Click
```

---

## 🔵 Session 5-8: Card Types

### Session 5: Pump Card

```
Continue with Violet Pool Card - Implement PUMP CARD

CONTEXT:
Components are ready. Now first complete card.

REFERENCE MOCK-UP (VIOLET_CARD_ROADMAP.md):
┌─────────────────────────────────────────┐
│ 🔵 Pump              [AUTO] [Level 2]  │
│ Status: Pump Anti Freeze                │
│ ━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ OFF        ECO      Normal      Boost   │
│ [OFF] [AUTO] [ECO] [Normal] [Boost]    │
│ ⏱️ Runtime: 2h 34min                    │
└─────────────────────────────────────────┘

ENTITY:
- switch.violet_pool_pump
- Attributes:
  - PUMPSTATE: "3|PUMP_ANTI_FREEZE"
  - PUMP_RPM_*: Speed values
  - runtime (optional)

TASKS:
1. Pump Card Class (src/cards/pump-card.ts)
2. Layout like mock-up
3. Status Badge (OFF/ON/AUTO/MANUAL)
4. Detail Status (Parse PUMPSTATE)
5. Speed Slider (0-3 with labels)
6. Quick Actions (OFF/AUTO/Speed Presets)
7. Runtime Counter (optional)
8. Icon animation when running

INTEGRATION:
```typescript
// In violet-pool-card.ts
case 'pump':
  return html`<pump-card .hass=${this.hass} .config=${this.config}></pump-card>`;
```

DELIVERABLES:
- ✅ Pump Card functional
- ✅ All features from mock-up
- ✅ Responsive
```

### Session 6-8: More Cards
Analogous to Session 5, but for:
- **Session 6**: Heater Card (climate.violet_pool_heater)
- **Session 7**: Solar Card (climate.violet_pool_solar)
- **Session 8**: Dosing Card (switch.violet_pool_dos_*)

Use mock-ups from VIOLET_CARD_ROADMAP.md!

---

## 📊 Session 9: Overview & Compact

### Copy-Paste Prompt:
```
Continue with Violet Pool Card - OVERVIEW & COMPACT CARDS

CONTEXT:
All detail cards (Pump, Heater, Solar, Dosing) are ready.

GOAL:
- Overview Card: Everything at a glance
- Compact Card: Minimal dashboard view

OVERVIEW CARD MOCK-UP:
┌─────────────────────────────────────────┐
│ 🏊 Pool Status                          │
│ 🌡️ 24.5°C  |  🧪 pH 7.2  |  ⚡ 650mV   │
│   ✅ OK        ✅ OK         ⚠️ Low     │
│ Active Devices:                          │
│ 🔵 Pump (Auto, Level 2, Anti-Freeze)    │
│ ❌ Heater (Blocked by Outside Temp)     │
│ 💧 Chlorine (Blocked by Thresholds)    │
│ Warnings:                                │
│ ⚠️ ORP too low - Dose chlorine           │
└─────────────────────────────────────────┘

COMPACT CARD MOCK-UP:
┌─────────────────────────────────────────┐
│ 🔵 Pump        [AUTO] Level 2 (Anti-F) │
│ 🔥 Heater      [AUTO] Blocked (14°C)   │
│ ☀️ Solar        [AUTO] Anti-Freeze      │
└─────────────────────────────────────────┘

TASKS:
1. Overview Card (src/cards/overview-card.ts)
   - Multi-entity config
   - Water chemistry traffic light (pH/ORP/Chlorine)
   - Temperature overview
   - Active devices list
   - Warnings prominent
   - Click → Details

2. Compact Card (src/cards/compact-card.ts)
   - Single-line display
   - Status Badge + Value + Detail
   - Click → Modal with full card
   - Dashboard-optimized

DELIVERABLES:
- ✅ Overview Card functional
- ✅ Compact Card functional
- ✅ Modal Dialog
- ✅ Responsive
```

---

## ✨ Session 10: Polish & Release

### Copy-Paste Prompt:
```
Continue with Violet Pool Card - FINAL POLISH & RELEASE

CONTEXT:
All card types work. Now make production-ready.

TASKS:
1. RESPONSIVE TESTING
   - Desktop (1920px) ✅
   - Tablet (768px) ✅
   - Mobile (375px) ✅

2. THEME SUPPORT
   - Dark Mode works
   - Light Mode works
   - Custom Theme Variables
   - Use CSS Variables

3. PERFORMANCE
   - Bundle Size < 100KB
   - Lazy Loading for Modal
   - Debounce Slider Updates
   - Optimize Re-renders

4. ACCESSIBILITY
   - ARIA Labels
   - Keyboard Navigation
   - Screen Reader Support
   - Focus States

5. DOCUMENTATION
   - Expand README
   - Create screenshots
   - Configuration Examples
   - Troubleshooting Section
   - CHANGELOG.md

6. TESTING
   - Test in HA 2024.1+
   - Test with real controller
   - Test all card types
   - Test theme switching

7. GITHUB RELEASE
   - Tag v1.0.0
   - Release notes
   - Dist files
   - Screenshots

8. HACS SUBMISSION
   - Fork HACS/default
   - Add Repository
   - Create PR

DELIVERABLES:
- ✅ Production-ready code
- ✅ Complete docs
- ✅ GitHub Release
- ✅ HACS available
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

# Create GitHub Release
# - Tag: v1.0.0
# - Title: "🎉 Violet Pool Card v1.0.0"
# - Attach: dist/violet-pool-card.js
# - Release notes from CHANGELOG.md
```

---

## 🔧 Debugging Tips

### Card doesn't load
```javascript
// Browser Console
window.customCards
// Should contain violet-pool-card

// HA Developer Tools → States
// Check if entities exist
```

### Service call fails
```typescript
// In service-caller.ts
console.log('Calling service:', service, data);
```

### Styling Issues
```css
/* DevTools → Elements → Computed */
/* Check CSS Variables */
--primary-color
--primary-text-color
--card-background-color
```

---

## 📚 Useful Links

**During Development:**
- Lit Playground: https://lit.dev/playground/
- MDI Icons: https://pictogrammers.com/library/mdi/
- HA Frontend Docs: https://developers.home-assistant.io/docs/frontend/

**Testing:**
- HA Dev Environment: http://localhost:8123
- Browser DevTools: F12
- HA Logs: Settings → System → Logs

**Release:**
- HACS Docs: https://hacs.xyz/docs/publish/start
- GitHub Releases: https://docs.github.com/en/repositories/releasing-projects-on-github

---

## 🎯 Success Metrics

### Check after each session:
- [ ] Code compiles without errors
- [ ] ESLint clean (no warnings)
- [ ] TypeScript Errors: 0
- [ ] Card renders in HA
- [ ] Functions test

### Before Release:
- [ ] All card types work
- [ ] Responsive on all devices
- [ ] Theme support (Dark/Light)
- [ ] Bundle Size < 100KB
- [ ] README complete
- [ ] Screenshots available
- [ ] HACS-compatible

---

## 🚀 Let's Go!

**Next Step:**
1. Open new Claude Code session
2. Copy Session 1 prompt (above)
3. Paste & Enter
4. Follow the roadmap! 🎉

**Estimated Time:**
- Sessions 1-3: ~2-3h each (Setup & Components)
- Sessions 4-8: ~2h each (Cards)
- Sessions 9-10: ~2-3h each (Polish & Release)
- **Total: ~20-25 hours**

Good luck! 💪
