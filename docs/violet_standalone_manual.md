# VIOLET Standalone – User Manual

> **Dosing Module with Control via Raspberry PI 3B / 3B+**
> Software Version: 1.1.7 | As of: 07.2025
> Manufacturer: PoolDigital GmbH & Co. KG | Kapellenstraße 10a | 86441 Zusmarshausen | Tel.: 08291 / 1699-495

---

## Table of Contents

1. [Installation Requirements / Installation Planning](#1-installation-requirements--installation-planning)
2. [Introduction](#2-introduction)
3. [Initial Startup / Basic Configuration](#3-initial-startup--basic-configuration)
4. [Dashboard, Statistics, Dosing Quantities](#4-dashboard-statistics-dosing-quantities)
5. [General Information on Dosing Options](#5-general-information-on-dosing-options)
6. [pH Dosing (Raise/Lower)](#6-ph-dosing-raiselower)
7. [Chlorine Dosing (Liquid Chlorine)](#7-chlorine-dosing-liquid-chlorine)
8. [Electrolysis Control](#8-electrolysis-control)
9. [Flocculant Dosing](#9-flocculant-dosing)
10. [Electrode Calibration](#10-electrode-calibration)
11. [Regular Inspection of All Dosing-Relevant Components](#11-regular-inspection-of-all-dosing-relevant-components)
12. [Decommissioning the Dosing Control in Winter](#12-decommissioning-the-dosing-control-in-winter)
13. [System Settings](#13-system-settings)
14. [System Logfiles](#14-system-logfiles)
15. [Restoring Factory Settings](#15-restoring-factory-settings)
16. [Integration with Home Automation Systems](#16-integration-with-home-automation-systems)
17. [Notifications via HTTP Request to External Systems](#17-notifications-via-http-request-to-external-systems)
18. [VIOLET Declaration of Conformity](#18-violet-declaration-of-conformity)
19. [GPL License Statement](#19-gpl-license-statement)

---

## 1 Installation Requirements / Installation Planning

Electronic components and electrochemical sensors (pH / Redox / Chlorine) are sensitive to electromagnetic interference (EMIs) and high-frequency fields. Power-intensive consumers such as filter pumps, heat pumps, or counter-current systems generate strong electromagnetic fields.

> **Important:** Never route sensor cables (pH, Redox, Chlorine) and control lines parallel to 230 V / 400 V cables. Observe VDE regulations regarding spatial separation.

- Minimum distance from frequency converters, variable filter pumps, inverter heat pumps: **at least 1 m**
- Do not extend sensor cables with connectors or uninsulated cabinet feedthroughs (signal level: mV range, pA–nA)
- Prefer wired network connection (LAN); WiFi and DLan are interference-prone in industrial environments
- Network connection must be VDE-compliant and **galvanically isolated**; remove shielded RJ45 connectors at the VIOLET end or use galvanically isolated adapters

### 1.1 Power Supply / Communication Connection

- 24 V power supply (min. 15 W) **exclusively** for VIOLET – do not connect any other loads
- 5 V power supply **exclusively** for the Raspberry Pi
- If 24 V DC is needed elsewhere: use a **separate** power supply
- Communication connection between Raspberry and dosing module: **USB cable** (any USB port on the Raspberry)

---

## 2 Introduction

### 2.1 Basic Configuration

VIOLET Standalone is a dosing controller for all common dosing options. After basic configuration, unused menu items are hidden.

**Configuration Wizard:** When the user interface is first accessed, a wizard is launched. All settings can be adjusted at any time under **MENU → CONFIGURATION** and **MENU → SYSTEM**.

**UIA (Violet-Inline-Assist):** For every control function, the UIA button is available in the top right corner, which leads directly to the corresponding section of the user manual.

Current versions of all manuals: **MENU → SYSTEM → DOCUMENTATION**

---

## 3 Initial Startup / Basic Configuration

### 3.1 Accessing the User Interface in the Browser

1. Connect Raspberry to the network and via USB to the dosing module
2. Turn on 5 V supply (Raspberry) and 24 V supply (dosing module)
3. Startup time: approx. 30 seconds

**URL:** `http://violet.local` (with Bonjour support) or direct IP address from the router's device list

**Default Credentials:**

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `violet` |

**Fallback IP (without DHCP server):**

| Parameter | Value |
|---|---|
| IPv4 Address | `192.168.1.111` |
| Subnet Mask | `255.255.0.0` |
| Gateway | `192.168.1.1` |

The web interface can be saved as a **bookmark to the home screen** on mobile devices.

### 3.2 Changing Credentials

`MENU → CONFIGURATION → CREDENTIALS`

- Minimum password length: **8 characters**
- Case-sensitive
- If password is forgotten: Reset via [Section 15.1](#15-restoring-factory-settings)

> **Important with port forwarding:** A secure password is mandatory.

### 3.3 Adjusting Network Settings

`MENU → SYSTEM → NETWORK`

- Default: **DHCP client** (router assigns IP automatically)
- Static IP address: Set `Use DHCP` to **NO**, then enter IP, subnet, gateway, and DNS
- Static IP must be outside the router's DHCP range

> **Recommendation for home automation:** Assign a static IP address and direct all queries to this IP (not to `http://violet.local`) to ensure reliable reachability and fast name resolution.

**WiFi Direct-Access (HotSpot):**

| Parameter | Value |
|---|---|
| SSID | `Violet` |
| Password | `violet2023` |

> **Security notice:** Default credentials must be changed if the hotspot is used permanently.

### 3.4 Configuring Pool Data

`MENU → CONFIGURATION → POOL DATA`

Set the following parameters:

- `Pool Location` (Indoor / Outdoor)
- `Pool Type` (Skimmer / Overflow)
- `Pool Cover`
- `Pool Surface` in m²
- `Pool Volume` in m³
- Type of use

> These values form the basis for automatic parameterization of all dosing controllers.

### 3.5 Notification Settings

`MENU → CONFIGURATION → NOTIFICATIONS`

Available notification channels:
- **Email** (up to 5 recipient addresses; via VIOLET mail service or own SMTP)
- **Push Notifications** (Pushover.net or Telegram)
- **HTTP Requests** to external systems (e.g. home automation)

**Email:**
- `Send email via`: VIOLET mail service or own SMTP
- Test email via `SEND TEST EMAIL` button

**PUSH – Pushover.net:**
- Requires account and APP from http://www.pushover.net
- `Push Provider User Key`: User key from Pushover account
- `Push Provider API Token`: API token of the registered device

**PUSH – Telegram:**
- Telegram app with username required
- Enter username (with `@`) → click `CONNECT` → send a message to the VIOLET Telegram bot within 3 minutes

**Daily Status Notification:** Sends all current measured values and switching states daily at a configurable time.

### 3.6 Configuring Dosing Options

`MENU → CONFIGURATION → DOSING OPTIONS`

| Option | Description |
|---|---|
| `Chlorine Dosing (liquid)` | Liquid chlorine (sodium hypochlorite); specify dosing pump delivery rate; combinable with electrolysis |
| `Salt Electrolysis` | Salt electrolysis system; specify production capacity in g/h; requires relay expansion; combinable with liquid chlorine |
| `Chlorine Measurement` | Direct chlorine measurement via potentiostatic chlorine electrode (optional); only activate if electrode is installed |
| `pH Dosing` | pH reducer dosing; specify delivery rate; combinable with pH+ |
| `pH+ Dosing` | pH raiser / alkalinity raiser; specify delivery rate; combinable with pH- |
| `Flocculant Dosing` | Flocculant dosing; specify delivery rate |

### 3.7 Configuring Pulse Input

`MENU → CONFIGURATION → PULSE INPUT`

**Pulse Input 1** is used for measurement water monitoring / flow monitoring at the electrodes.

| Sensor Type | Description |
|---|---|
| `Hall Sensor` | Flow sensor from Violet accessories |
| `Proximity Switch` | Proximity/flow switch with normally-open contact (terminals GND + DATA to IMP1) |

---

## 4 Dashboard, Statistics, Dosing Quantities

### 4.1 Dashboard

`MENU → HOME → DASHBOARD`

Complete overview of all water parameters. Displayed widgets depend on activated dosing options.

Login: `[LOGIN]` button top right (default: `admin` / `violet`)

#### 4.1.1 Informational, Warning, and Alarm Messages

The first line shows current messages – color-coded by severity:

| Symbol | Color | Meaning |
|---|---|---|
| ▲ | Green | Reminder / Information |
| ▲ | Yellow | Warning (e.g. canister fill level, limit exceeded) |
| ▲ | Red | Alarm (monitoring function triggered) |

- Acknowledge individual message: `ACKNOWLEDGE` button
- Acknowledge all messages: `ACKNOWLEDGE ALL` button
- An active **alarm (red)** must be acknowledged before VIOLET releases the locked function
- Messages whose trigger is still active will be immediately re-triggered → resolve the cause first, then acknowledge

#### 4.1.2 Dashboard Widgets

Each widget shows measured value + additional info. Clicking the text area opens the context menu.

**Flow Widget:**

| Display | Description |
|---|---|
| Main value | Flow in cm/s (including daily min/max since 00:00) |
| Runtime | Daily runtime with flow > 0 |
| Flocculant dosing | Operating state (if active) |
| Status | Dosing controller operating state |
| Daily dosing quantity | ml since 00:00 |
| Canister remaining content | in ml |

> **After power failure:** "MANUAL OFF" functions remain deactivated after restart. "MANUAL ON" functions are reset to AUTO after an interruption > 5 minutes. Manually triggered dosing is not resumed.

#### 4.1.3 Context Menu for pH- / pH+ / Redox / Electrolysis / Flocculant

| Button | Function |
|---|---|
| `[ - ]` / `[ + ]` | Change setpoint within defined limits (applied immediately) |
| `[ MAN ]` | Start manual dosing; format MM:SS (HH:MM for electrolysis) |
| `[ AUTO ]` | Return to automatic operation |
| `[ OFF ]` | Permanently disable dosing control or for a selectable period |
| `[ CONTAINER CHANGE ]` | Reset canister content after change (enter ml) |

> `MANUAL OFF` takes priority – the dosing pump will under no circumstances be activated by the automation. Suitable for maintenance or long-term deactivation.

**Dosing Option Widget (example):**

| Display | Description |
|---|---|
| Main value | Water parameter including daily min/max |
| Dosing control | Operating state |
| Status | Dosing controller operating state |
| Daily dosing quantity | ml since 00:00 |
| Canister remaining content | ml + estimated remaining days (basis: Ø last 5 days chlorine / 7 days pH) |

### 4.2 Statistics

`MENU → HOME → STATISTICS`

- Snapshot every 5 minutes
- Time period selectable; start day and number of past days adjustable
- Measured values selectable left/right → left/right Y-axis
- Selection is saved
- Export as `.csv` (Excel) via `DOWNLOAD` button

### 4.3 Dosing Statistics

`MENU → HOME → DOSING QUANTITIES`

- Daily total dosing quantities in tabular form
- Time period selectable; columns configurable
- Export as `.csv` via `DOWNLOAD` button
- Individual dosing events: in the configuration area of the respective dosing option under "Information"

---

## 5 General Information on Dosing Options

- Basic control parameters are automatically determined based on pool data
- **Quantity Adjustment**: Slider (+/- 50%) for fine-tuning the dosing quantity per cycle
- Dosing only occurs with **flow** at the electrodes and when no blocking reason is present
- On **limit violation**: Dosing is blocked until the measured value is back in range; manual dosing is always possible (with existing flow)
- Notification on limit violation: when limit is consistently exceeded/fallen below for > 10 minutes
- On **reaching the daily dosing limit**: Block until 23:59; reset at 00:00; manual dosing still possible
- The daily dosing limit is **not a normal limiter**, but an error detector (e.g. defective pump, clogged injection valve)
- Canister remaining content: Calculation from delivery rate × runtime; dosing does **not** stop automatically at remaining content = 0
- Optional: Suction lance with empty contact for definitive pump shutoff

---

## 6 pH Dosing (Raise/Lower)

### 6.1 pH- Dosing Control

`MENU → DOSING → PH-`

Controls the pH value in the direction of **lowering pH**.

**Adjustable Parameters:**

| Parameter | Description | Recommendation |
|---|---|---|
| `Dosing Control` | Enable/disable automatic | – |
| `pH Setpoint` | Setpoint for pH- control | 7.2–7.4 (general), 7.4–7.5 (tile/natural stone) |
| `Quantity Adjustment` | Dosing quantity +/- 50% | 0 % |
| `Release Delay` | Lock time after filter pump start (MM:SS) | 20:00–30:00 |
| `Max. Daily Dosing Capacity` | Maximum daily dosing quantity in ml | 300–500 ml per 10 m³ |
| `Lower Warning Limit` | Falling below → dosing blocked | 0.4 pH below setpoint |
| `Upper Warning Limit` | Exceeding → dosing blocked | 0.4 pH above setpoint |
| `Canister Content Warning Limit` | Notification on low remaining content | – |
| `Use Empty Contact` | Suction lance contact for pump shutoff | – |
| `Empty Contact Type` | Normally open or normally closed | – |

> When using pH- and pH+ simultaneously: pH- setpoint must be at least 0.05 pH units **above** the pH+ setpoint.

**Information Area:**

| Display | Description |
|---|---|
| pH dosing status | Why dosing may not be released |
| Current measured value | Current pH value |
| Next dosing cycle | Remaining time until next cycle |
| Dosing quantity last cycle | Dosing quantity of last active cycle |
| Today's dosing quantity | Total dosing quantity today; click opens detail history (up to 1000 entries) |
| Canister remaining content | Remaining content in ml; gear icon = adjust; arrows = container change |

### 6.2 pH+ Dosing Control

`MENU → DOSING → PH+`

Controls the pH value in the direction of **raising pH**. Parameters and functions identical to pH- dosing (see section 6.1).

---

## 7 Chlorine Dosing (Liquid Chlorine)

`MENU → DOSING → LIQUID CHLORINE`

Doses sodium hypochlorite via a dosing pump. Control is based on redox potential or combined redox + chlorine content.

> **Combined Control (Redox + Chlorine):** Reduces chemical demand by up to 25% compared to pure chlorine control; maintains DIN-compliant limit values.

**Adjustable Parameters:**

| Parameter | Description | Recommendation |
|---|---|---|
| `Dosing Control` | Enable/disable automatic | – |
| `Control Type` | Redox-based or redox- and chlorine-based | – |
| `Redox Setpoint` | Setpoint in mV | 750–800 mV (standalone); ~20–30 mV below electrolysis setpoint (when combined) |
| `Min. Chlorine Content (mg/l)` | Minimum chlorine content (only with chlorine measurement) | 0.15–0.3 mg/l |
| `Max. Chlorine Content Day (mg/l)` | Upper limit 08:00–21:00 (only with chlorine measurement) | 0.45–0.60 mg/l |
| `Max. Chlorine Content Night (mg/l)` | Upper limit 22:00–06:00 (only with chlorine measurement) | 0.6–1.0 mg/l |
| `Release Delay` | Lock time after filter pump start (MM:SS) | 20:00–30:00 |
| `Max. Daily Dosing Capacity` | Maximum daily dosing quantity in ml | 300–500 ml/10 m³ (outdoor); 80–100 ml/10 m³ (indoor) |
| `Lower Redox Warning Limit` | Falling below → dosing blocked | 150–200 mV below setpoint |
| `Upper Redox Warning Limit` | Exceeding → dosing blocked | 30–50 mV above setpoint |
| `Lower Cl Warning Limit` | Falling below → dosing blocked | 0.05–0.15 mg/l |
| `Upper Cl Warning Limit` | Exceeding → dosing blocked | 1.2–1.5 mg/l |
| `Canister Content Warning Limit` | Notification on low remaining content | – |
| `Use Empty Contact` | Suction lance contact | – |

---

## 8 Electrolysis Control

`MENU → DOSING → SALT ELECTROLYSIS`

Controls salt electrolysis systems (existing or self-assembled). Separate outputs for cell control and polarity reversal.

> **Combined Control (Redox + Chlorine):** Identical benefits as with liquid chlorine; recommended for inline electrolysis systems (redox measurement not always reliable).

**Adjustable Parameters:**

| Parameter | Description | Recommendation |
|---|---|---|
| `Dosing Control` | Enable/disable automatic | – |
| `Control Type` | Redox-based or redox- and chlorine-based | – |
| `Redox Setpoint` | Setpoint in mV | 650–750 mV; ~20–30 mV above liquid chlorine setpoint (when combined) |
| `Min. Chlorine Content (mg/l)` | Minimum chlorine content (only with chlorine measurement) | 0.15–0.3 mg/l |
| `Max. Chlorine Content Day (mg/l)` | Upper limit (only with chlorine measurement) | 0.45–0.60 mg/l |
| `Max. Chlorine Content Night (mg/l)` | Upper limit (only with chlorine measurement) | 0.6–1.0 mg/l |
| `Release Delay` | Lock time after filter pump start (MM:SS) | 05:00–10:00 |
| `Polarity Reversal Interval (HH:MM)` | Interval for cell polarity reversal | 4–6 hours |
| `Max. Daily Production (g)` | Maximum daily chlorine production | 50–80 g/10 m³ (outdoor); 10–15 g/10 m³ (indoor) |
| `Lower Redox Warning Limit` | Falling below → dosing blocked | 250–300 mV below setpoint |
| `Upper Redox Warning Limit` | Exceeding → dosing blocked | 100–150 mV above setpoint |
| `Lower Cl Warning Limit` | (only with chlorine measurement) | 0.05–0.15 mg/l |
| `Upper Cl Warning Limit` | (only with chlorine measurement) | 1.2–1.5 mg/l |
| `Cell Runtime Warning Limit` | Notification on remaining cell runtime | – |

**Information Area (additional to pH/Chlorine):**

| Display | Description |
|---|---|
| Polarity Reversal (HH:MM:SS) | Remaining time until next polarity reversal |
| Today's Production Capacity | Total production today in g |
| Cell Remaining Runtime | Remaining cell runtime; gear icon = adjust; arrows = cell change |

---

## 9 Flocculant Dosing

`MENU → DOSING → FLOCCULANT`

Doses constant small amounts of flocculant distributed throughout the day. Release occurs without delay with pump start.

**Adjustable Parameters:**

| Parameter | Description | Recommendation |
|---|---|---|
| `Dosing Control` | Enable/disable automatic | – |
| `Daily Dosing Quantity` | Total daily dosing quantity in ml | 20–30 ml per 10 m³ per day |
| `Divide across` | Time span over which the daily dosing quantity is distributed | – |
| `Canister Content Warning Limit` | Notification on low remaining content | – |
| `Use Empty Contact` | Suction lance contact | – |

---

## 10 Electrode Calibration

### 10.1 General Information on Calibration

- Electrochemical sensors are wear parts and must be checked regularly
- Test water parameters at least **weekly** with a photometer (disinfectant + pH)
- New electrodes must be conditioned: **pH/Redox** at least 4–6 hours, **Chlorine** at least 24 hours in pool water
- Do **not** calibrate directly after cleaning the electrode – wait for conditioning period again
- Keep buffer solutions clean; rinse electrode with tap water before immersion and gently pat dry
- Close buffer solutions tightly after opening; protect from light; observe expiration date

### 10.2 Calibrating the pH Electrode

`MENU → DOSING → ELECTRODE CALIBRATION`

**Method:** 2-point calibration (pH 7 + second buffer solution with at least 2 pH units difference)

**Procedure:**
1. Click on heading `Calibrate pH Electrode (2-Point)`
2. Enter temperature of the buffer solution
3. Immerse electrode in buffer solution 1 (pH 7); allow `Measured Raw Value (mV)` to stabilize
4. Enter value of buffer solution 1 → click `NEXT`
5. Rinse/dry electrode → immerse in buffer solution 2; allow raw value to stabilize
6. Enter value of buffer solution 2 → click `CALIBRATE`

**Expected Raw Values:**

| Buffer Solution | Expected Raw Value |
|---|---|
| pH 7 | approx. 0 mV (± 15 mV) |
| pH 4 | approx. 177.5 mV (± 25 mV, temperature-dependent) |

> Reminder for next calibration is configurable (7 days to 6 months).

### 10.3 Calibrating the Redox Electrode

`MENU → DOSING → ELECTRODE CALIBRATION`

**Method:** 1-point calibration with any redox buffer solution

**Procedure:**
1. Click on heading `Calibrate Redox Electrode`
2. Enter value of the buffer solution
3. Immerse electrode; allow `Measured Raw Value (mV)` to stabilize
4. Click `CALIBRATE`

> Can be performed simultaneously with pH calibration.

### 10.4 Calibrating the Chlorine Electrode

`MENU → DOSING → ELECTRODE CALIBRATION`

**Method:** 2-point calibration (0-point + DPD1 reference measurement)

> **Prerequisite:** Electrode must be mounted and electrically connected for at least 24 hours (do not connect in storage solution).

**Determining the 0-Point** (only with filter pump OFF / no flow > 60 min):
1. Click on heading `Calibrate Chlorine Electrode`
2. Save the displayed 0-point by clicking `Save 0-Point`
3. Process complete (can be repeated if needed)

**Calibration via DPD1 Reference Measurement:**
1. Filter pump must run for at least 15 minutes
2. Take water sample as close to the electrode as possible → click `WATER SAMPLE TAKEN`
3. Perform DPD1 reference measurement with photometer
4. Enter result in field `Reference Measurement DPD1 (mg/l)`
5. Click `CALIBRATE`

**Validity Range:** Chlorine content between **0.2 mg/l and 3.0 mg/l**

> Chlorine electrode: even without a configured reminder, a dashboard notice is automatically displayed after 3 weeks (cannot be disabled).

**Correction Factor for Different Flow Velocities:**

Visible immediately after calibration. Change flow velocity (e.g. change pump speed) → allow value to stabilize → click `Compensate Flow` button.

- New flow must differ by at least 2 cm/s from the calibration flow
- Range: 5–20 cm/s
- One-time determination is sufficient

More information: https://www.poolsteuerung.de/viewtopic.php?f=99&t=2074

### 10.5 Calibration History

Available for each electrode via the "Statistics" icon in the `Last Calibration` row.

| Marker | Meaning |
|---|---|
| Green dot | Calibration error-free |
| Red dot | Parameters outside limits (notice was displayed) |

Previous error-free calibrations can be restored by clicking.

---

## 11 Regular Inspection of All Dosing-Relevant Components

| Task | Interval |
|---|---|
| Check water parameters (pH + disinfectant) with photometer (pH 7.0–7.5; Chlorine 0.3–1.5 mg/l) | At least 1× weekly |
| Check alkalinity (30–100 ppm / 2–6 °kH) and if applicable salt content (electrolysis) | Every 2–4 weeks |
| Calibrate chlorine electrode | Every 1–2 weeks |
| Calibrate pH and redox electrodes | Every 1–3 months |
| Visual inspection of peristaltic tubing of dosing pumps (leaks, damage) | Every 3–4 weeks |
| Check injection valves for chlorine and pH raiser for crust formation | Every 4–6 weeks |
| Check injection valves for pH reducer and flocculant | Every 5–6 months |
| Check dosing hoses for damage and aging | Every 5–6 months |
| Check turnstile of dosing pumps for wear; if needed, lubricate with commercially available grease | Every 5–6 months |

---

## 12 Decommissioning the Dosing Control in Winter

**Winterizing dosing pumps:**
1. Place suction hose in clear water
2. Trigger manual dosing for 2–3 minutes (flush hoses)
3. If there is risk of frost: Remove suction hose and briefly dose manually again (remove residual water)
4. Disassembly not necessary; pumps and hoses are frost-proof

**Winterizing electrodes:**
1. Place electrodes in cleaning solution for 15–20 minutes (electrically disconnected)
2. If visible soiling is present, leave longer; mechanical cleaning (soft brush) possible with caution
3. Rinse with clear water
4. Store in storage cover with **fresh 3M KCl solution** (standing upright, electrode immersed)

> Normal water, distilled water, calibration solution, or other liquids are **not** suitable. Do not leave electrodes electrically connected.

**Winterizing measurement cell:**
- Remove water from measurement cell and hoses (especially if there is risk of frost)
- Disassembly not necessary
- If filter pump continues running: Set all dosing controls to **MANUAL OFF** via the dashboard

---

## 13 System Settings

### 13.1 Network Settings

`MENU → SYSTEM → NETWORK`

#### 13.1.1 Network Settings (LAN)

| Parameter | Description |
|---|---|
| `Use DHCP` | DHCP on/off; when OFF: manual entry of IP, subnet, gateway, DNS |
| `IPv4 Address` | Only visible when DHCP=NO |
| `Subnet` | Only visible when DHCP=NO |
| `Gateway` | Only visible when DHCP=NO |
| `DNS Server` | Only visible when DHCP=NO |

#### 13.1.2 WiFi Direct-Access

VIOLET provides a 2.4 GHz WiFi hotspot.

- Reachable at: `http://violet.local` or `http://172.16.1.200`
- No internet access via this connection; no access to the LAN network
- Default SSID: `Violet` | Default password: `violet2023`

| Parameter | Description |
|---|---|
| `WiFi Direct-Access` | Enable/disable hotspot |
| `SSID` | Name of the hotspot |
| `Password` | Min. 8 characters |
| `Channel` | WiFi channel 1–11 |

#### 13.1.3 Current Data (LAN)

Shows current network configuration (IPv4, IPv6, subnet, gateway, MAC address, controller ID) – read-only.

### 13.2 Language / Color / Clock of the User Interface

`MENU → SYSTEM → USER INTERFACE`

- Language and color scheme selectable
- Set timezone (e.g. `EUROPE/Berlin`); daylight saving time is automatically adjusted
- After changing clock settings: automatic restart (~20 seconds)

### 13.3 Services

`MENU → SYSTEM → SERVICES`

#### 13.3.1 FTP Server

Access to statistics files and configuration backups on the SD card.

| Parameter | Value |
|---|---|
| Host | `violet.local` or IP address |
| Port | 21 |
| Username | `backupuser` |
| Password | `backupuser` |

> Password changeable via lock icon; also applies to CIFS/SAMBA. Username cannot be changed. Only accessible on local network (no remote access).

#### 13.3.2 CIFS/SAMBA Share

Network drive for statistics files and backups.

| Parameter | Value |
|---|---|
| Folder | `\\violet.local` or `\\<IP-Address>` |
| Username | `backupuser` |
| Password | `backupuser` |

Subfolders in the share:
- `/backup` – Configuration backups
- `/history` – Statistics files

**Windows 10 Setup (Quick Guide):**
1. Open Windows Explorer → "This PC" → "Computer" tab
2. "Map network drive" → select drive letter
3. Enter folder: `\\violet.local` → "Browse"
4. Select network folder → OK
5. Enter credentials → "Save credentials" → OK
6. Select "Pool" folder → OK → "Finish"

### 13.4 Update

`MENU → SYSTEM → UPDATE`

| Update Type | Notification Text | Procedure |
|---|---|---|
| Automatic Update | "No action required" | VIOLET installs automatically at night between 02:00–06:00; manual installation possible earlier |
| Manual Update | "Installation required" | Must be triggered manually via `Install Update` button; observe release notes |

> After update: VIOLET restarts (~brief unavailability). Remote access is temporarily disconnected.

### 13.5 Configuration Backup

`MENU → SYSTEM → BACKUP`

- Credentials and network settings are **not** saved/modified in backups
- Backups contain only configuration data (no statistics)
- Older backups can always be restored (missing parameters are preserved)

#### 13.5.1 Backup on Local SD Card

- Daily or weekly (specific day of the week)
- Max. 100 backups; oldest are overwritten (except manual backups)
- Manual backup: `Create Manual Backup Now` button

#### 13.5.2 Backup on USB Storage Media

- FAT32 or HFS+ formatted USB stick
- Storage location: `/VIOLET/config` (created automatically)
- Functionality identical to SD card backup

### 13.6 Documentation

`MENU → SYSTEM → DOCUMENTATION`

All available manuals as PDF; language selectable; updated with software updates.

---

## 14 System Logfiles

### 14.1 Logfile "Actions"

`MENU → LOGFILES → ACTIONS`

Max. 5000 entries; oldest are deleted.

| Category | Content |
|---|---|
| `USERACTION` | Configuration changes, manual switching |
| `CONTROLTASK` | Switching actions by configured rules |
| `SYSTEMTASK` | Notifications, restarts, backups |

- Show/hide categories via `CONFIGURE` button
- Export as text file via `DOWNLOAD` button
- Logfile cannot be deleted / edited

### 14.2 Logfile "Notifications"

`MENU → LOGFILES → NOTIFICATIONS`

Last 500 notifications; date, time, subject, notification channel.

| Channel | Description |
|---|---|
| `MAIL` | Email sent via VIOLET mail service |
| `SMTP` | Email sent via own SMTP |
| `PUSH` | Push notifications |
| `HTTP` | HTTP requests |

| Color | Meaning |
|---|---|
| Green | Successfully sent |
| Orange | Unsuccessful; retry pending |
| Red | Not sent or globally disabled; no retry |
| Strikethrough | Channel not activated in configuration |

> Click on channel text: Show response from the interface for diagnosis.

### 14.3 Testing Outputs

`MENU → LOGFILES → TEST OUTPUTS`

- Display switching state of all dosing outputs / empty contacts
- Manually switch relay output for max. 5 seconds (no continuous operation)
- Naming of empty contacts is customizable

> Dosing outputs (pH, Chlorine, Electrolysis, Flocculant) active for max. 4 seconds; only use if dosing pumps are not yet connected to the canister.

---

## 15 Restoring Factory Settings

### 15.1 Resetting to Factory State

**Method:** Disconnect and reconnect the USB connection between Raspberry and dosing module **5 times within 30 seconds**.

**Procedure:**
1. Unplug USB connector → immediately plug back in
2. Wait 3 seconds
3. Repeat the process a total of 5× (all within 30 seconds)
4. 30 seconds after first disconnection: Reset is executed → system shuts down (LAN LEDs go off)
5. Briefly disconnect Raspberry from power → reconnect
6. After approx. 30 seconds: VIOLET is accessible again with factory settings

**Reset Settings:**
- DHCP activated
- Credentials: `admin` / `violet`
- All configuration settings reset

---

## 16 Integration with Home Automation Systems

> **Recommendation:** Configure a static IP address for VIOLET (outside the DHCP range); direct all queries to the IP (not to `http://violet.local`).

### 16.1 JSON-API – Querying Measured Values

VIOLET provides all measured values via a JSON-API.

**Base URL:** `http://<VIOLET-IP>/getReadings?<PARAMETER>`

**API Description (complete list):**
https://www.pooldigital.de/_red/paperwork/api_description/getReadings.xlsx

**Example Queries:**

```
GET /getReadings?ALL
→ All measured values and states

GET /getReadings?pH_value
→ pH value + daily min/max

GET /getReadings?IMP1_value
→ Flow sensor measured value

GET /getReadings?pH_value,orp_value,pot_value
→ pH, ORP (Redox) and Potentiostat (Chlorine)

GET /getReadings?_value
→ All values containing "_value"

GET /getReadings?DOSING
→ Daily dosing quantities

GET /getReadings?ALL,DOSAGE,RUNTIMES
→ All maximum available values
```

**Example Response `/getReadings?pH_value`:**
```json
{
  "pH_value_min": 7.22,
  "pH_value_max": 7.30,
  "pH_value": 7.30
}
```

**Example Response `/getReadings?DOSING`:**
```json
{
  "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": "2204",
  "DOS_2_ELO_DAILY_DOSING_AMOUNT_ML": "0.0",
  "DOS_4_PHM_DAILY_DOSING_AMOUNT_ML": "144",
  "DOS_5_PHP_DAILY_DOSING_AMOUNT_ML": "0",
  "DOS_6_FLOC_DAILY_DOSING_AMOUNT_ML": "84"
}
```

---

## 17 Notifications via HTTP Request to External Systems

### 17.1 Configuring the HTTP Request

`MENU → CONFIGURATION → NOTIFICATIONS`

VIOLET sends notifications as GET or POST requests with the following fields:

| Field Name | Value |
|---|---|
| `ERRORCODE` | Four-digit error code |
| `SUBJECT` | Brief description of the error |

**Adjustable Parameters:**

| Parameter | Description |
|---|---|
| `HTTP Requests` | Enable/disable globally |
| `URL/IP for Receiver API` | IP address or domain name (without `http://`); port must be 80 |
| `Path to Receiver API` | Complete path including `/` (e.g. `/myScript/violet.php`) |
| `Base Query` | Optional additional field=value pairs (separate multiple with `&`) |
| `Method` | GET or POST |
| `API Response Body (success)` | String that the API returns on success (pattern matching) |
| `API Response Body (error)` | String that the API returns on error |

> With unknown or missing response: retry every 60 minutes, max. 10×. Acknowledging the error message in VIOLET stops retries.

**Example GET Request (Error Code 0020):**
```
http://192.168.1.100/myScript/violet_messaging.php?ERRORCODE=0020&SUBJECT=Alarm,Filter Pressure Monitoring (Pressure too low)&user=Violet
```

### 17.2 Error Code List for HTTP Requests

| ERRORCODE | SUBJECT |
|---|---|
| 0000 | Test message |
| 0001 | Status message |
| 0008 | CPU temperature high (> 83 °C) |
| 0009 | CPU temperature too high (> 95 °C) |
| 0010 | Update ready for installation. No action required. |
| 0011 | Update ready for installation. Installation required. |
| 0012 | Update ready for installation. Installation required. |
| 0022 | Warning, Measurement water monitoring (no flow) |
| 0023 | Warning, Measurement water monitoring (flow too high) |
| 0120 | Warning, Chlorine dosing: Redox limit reached |
| 0121 | Warning, Chlorine dosing: Chlorine limit reached |
| 0122 | Warning, Chlorine dosing: max. daily dosing capacity reached |
| 0123 | Warning, Chlorine canister remaining content low |
| 0124 | Warning, Chlorine canister empty |
| 0125 | Warning, Empty contact: Chlorine canister |
| 0130 | Warning, Electrolysis: Redox limit reached |
| 0131 | Warning, Electrolysis: Chlorine limit reached |
| 0132 | Warning, Electrolysis: maximum daily production reached |
| 0133 | Warning, Electrolysis: Cell runtime warning |
| 0134 | Warning, Electrolysis: maximum total operating time reached |
| 0150 | Warning, pH-minus dosing: pH limit reached |
| 0152 | Warning, pH-minus dosing: max. daily dosing capacity reached |
| 0153 | Warning, pH-minus dosing: Canister remaining content low |
| 0154 | Warning, pH-minus dosing: Canister empty |
| 0155 | Warning, Empty contact: pH-minus canister |
| 0160 | Warning, pH-plus dosing: pH limit reached |
| 0162 | Warning, pH-plus dosing: max. daily dosing capacity reached |
| 0163 | Warning, pH-plus dosing: Canister remaining content low |
| 0164 | Warning, pH-plus dosing: Canister empty |
| 0165 | Warning, Empty contact: pH-plus canister |
| 0173 | Warning, Flocculant: Canister remaining content low |
| 0174 | Warning, Flocculant: Canister empty |
| 0175 | Warning, Empty contact: Flocculant canister |
| 0180 | Reminder, Calibrate pH electrode |
| 0181 | Reminder, Calibrate Redox electrode |
| 0182 | Reminder, Calibrate Chlorine electrode |
| 0200 | Warning, Dosing module no longer connected (disconnected) |
| 0201 | Warning, Dosing module, communication lost |
| 0208 | Alarm, Second dosing module detected. Will be ignored. |

---

## 18 VIOLET Declaration of Conformity

**EC Declaration of Conformity**

We hereby declare that the product described below complies with the basic safety and health requirements of the EC Low Voltage Directive.

| Field | Content |
|---|---|
| Product Name | VIOLET |
| Serial Number | See manufacturer label on the device |
| Product Type | Swimming pool controller |
| Manufacturer | PoolDigital GmbH & Co KG, Gablinger Weg 102, D-86156 Augsburg |
| Date | February 1, 2024 |

**Applied Harmonized Standards:**
- EC Low Voltage Directive 2014/35/EU
- EMC Directive 2014/30/EU
- EN 61000-4-3, EN 61000-4-4, EN 61000-4-5, EN 61000-4-6, EN 61000-4-8
- EN 61000-3-2, EN 61000-3-3
- EN 55011

---

## 19 GPL License Statement

Besides VIOLET's application code (closed-source), this product includes software code developed by third parties, including software subject to the GNU GPLv3, LGPL2.1, Apache License 2.0 and MIT License.

Full license information:
https://www.pooldigital.de/_red/paperwork/privacy_policy/LicenseStatement.pdf

**Written Offer for GPL/LGPL Source Code:**
Source code available on request (USB stick; nominal cost for shipping/media; valid 3 years).

Contact:
> PoolDigital GmbH & Co. KG
> – GPL Request VIOLET –
> Kapellenstraße 10a
> 86441 Zusmarshausen
