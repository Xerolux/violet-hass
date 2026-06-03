# API Package Contract — `violet-poolController-api`

> **Kurzfassung (DE):** Die Integration `violet_pool_controller` ist ab Version
> 1.2.1 **nicht** mehr darauf angewiesen, dass das externe Paket
> `violet-poolController-api` die Steuer-Konstanten (`COVER_FUNCTIONS`,
> `COVER_STATE_MAP`, `DEVICE_PARAMETERS`, `ACTION_*`) exportiert — diese werden
> jetzt lokal in `const.py` definiert. Es **muss** also nichts am API-Paket
> geändert werden, damit die Integration wieder lädt.
>
> Damit der Fehler *"Integration 'violet_pool_controller' not found"* nicht
> erneut auftritt, beschreibt dieses Dokument den **stabilen Vertrag** zwischen
> dem API-Paket und der Integration: Welche Klassen, Methoden und Module das
> API-Paket bereitstellen muss und was **nicht ohne Major-Version-Bump entfernt
> werden darf.** Dieses Dokument ist auch dafür gedacht, dass eine KI, die am
> API-Paket arbeitet, den Vertrag versteht.

---

## 1. What happened (root cause)

The integration worked on version `1.2.0` and broke after the external
`violet-poolController-api` package was updated to `0.0.24`. Home Assistant
reported:

```
Unable to get manifest for integration violet_pool_controller:
Integration 'violet_pool_controller' not found.
```

This is HA's symptom of the integration failing to **import**, not of missing
files. The cause: `const.py` re-exported control constants via

```python
from violet_poolcontroller_api.const_api import *
from violet_poolcontroller_api.const_devices import *
```

When `0.0.24` dropped several of those constants, the modules that imported them
from `.const` (`cover.py`, `service_control.py`) raised `ImportError`, and the
whole integration failed to load.

## 2. Fix applied in the integration (v1.2.1)

The control constants are now **owned by the integration** and defined locally
in `custom_components/violet_pool_controller/const.py`:

| Constant | Type | Value |
| --- | --- | --- |
| `COVER_FUNCTIONS` | `dict[str, str \| None]` | `{"OPEN": "COVER_OPEN", "CLOSE": "COVER_CLOSE", "STOP": "COVER_STOP"}` |
| `COVER_STATE_MAP` | `dict[str, str]` | `{"0": "open", "1": "opening", "2": "closed", "3": "closing"}` |
| `DEVICE_PARAMETERS` | `dict[str, dict[str, str]]` | `{}` |
| `ACTION_PUSH`, `ACTION_ALLAUTO`, `ACTION_ALLOFF`, `ACTION_ALLON`, `ACTION_AUTO`, `ACTION_OFF`, `ACTION_ON` | `str` | `"PUSH"`, `"ALLAUTO"`, … |

The `import *` lines remain (for any other constants the package still ships),
but the integration no longer **depends** on them for these symbols. The
dependency is also pinned to `violet-poolController-api==0.0.24` in
`manifest.json` and `requirements.txt` so a future floating update cannot break
imports again.

> **Conclusion:** No change is required in the API package for the integration
> to load. The remaining sections define the contract so future API releases
> stay compatible.

## 3. The stable contract — what the API package MUST keep exporting

The integration imports the following from `violet-poolController-api` at
runtime. Removing or renaming any of these is a **breaking change** and requires
a **major version bump** plus a coordinated integration update.

### 3.1 Module `violet_poolcontroller_api.api`

| Symbol | Kind | Used by |
| --- | --- | --- |
| `VioletPoolAPI` | class | `device.py`, `config_flow.py`, `__init__.py`, `config_flow_utils/sensor_helper.py` |
| `VioletPoolAPIError` | exception | `climate.py`, `cover.py`, `switch.py`, `number.py`, `select.py`, `service_control.py`, `device.py` |

**`VioletPoolAPI` methods the integration calls** (signatures must stay
backward-compatible):

```
get_readings(...)              get_config(...)
set_config(...)                set_switch_state(key=..., action=..., ...)
set_target_value(...)          set_device_temperature(...)
set_pump_speed(...)            set_pv_surplus(...)
set_dosage_enabled(...)        manual_dosing(...)
set_dosing_parameters(...)     set_ph_target(...)
set_orp_target(...)            set_min_chlorine_level(...)
set_all_dmx_scenes(...)        set_light_color_pulse(...)
set_output_test_mode(...)      set_digital_input_rule_lock(...)
trigger_digital_input_rule(...)
```

### 3.2 Module `violet_poolcontroller_api.utils_sanitizer`

| Symbol | Kind | Used by |
| --- | --- | --- |
| `InputSanitizer` | class | `service_control.py`, `number.py` |

### 3.3 Module `violet_poolcontroller_api.const_devices`

| Symbol | Kind | Used by | Contract |
| --- | --- | --- | --- |
| `VioletState` | class | `sensor_modules/generic.py` | Constructed as `VioletState(raw_value, key)`; must expose `.display_mode` and `.icon` properties |
| `DEVICE_STATE_MAPPING` | mapping | referenced conceptually by `switch.py` / `select.py` state logic | Should map state codes `0–6` (see `CLAUDE.md` §State Handling) |

### 3.4 Modules that must remain importable

`const.py` still executes `from violet_poolcontroller_api.const_api import *`
and `from violet_poolcontroller_api.const_devices import *`. **Both modules must
continue to exist and import cleanly** (even if some individual constants are
removed), otherwise `const.py` itself fails to import and the integration breaks
again.

## 4. Guidance for the API package (and any AI working on it)

1. **Treat the symbols in §3 as a public, stable API.** Do not remove or rename
   them in a patch/minor release.
2. **Use semantic versioning.** Breaking changes (removed/renamed public
   symbols, changed method signatures) require a **major** version bump.
3. **Keep `const_api` and `const_devices` importable** at all times — even an
   empty module is fine, but a missing module breaks `const.py`'s wildcard
   imports.
4. **If you move/retire a constant**, keep a backward-compatible re-export for at
   least one deprecation cycle, and announce it in the package changelog.
5. **Coordinate version bumps** with the integration: the integration pins an
   exact version in `manifest.json`. When the API package releases a new
   version, the integration must be tested and the pin bumped deliberately
   (never via an open `>=` range).

## 5. Checklist before publishing a new `violet-poolController-api` release

- [ ] `violet_poolcontroller_api.api` exports `VioletPoolAPI` and `VioletPoolAPIError`.
- [ ] All `VioletPoolAPI` methods listed in §3.1 exist with compatible signatures.
- [ ] `violet_poolcontroller_api.utils_sanitizer.InputSanitizer` exists.
- [ ] `violet_poolcontroller_api.const_devices.VioletState` exists with `.display_mode` and `.icon`.
- [ ] `const_api` and `const_devices` import without error.
- [ ] Version bumped per semver; integration `manifest.json` pin updated and tests run.
