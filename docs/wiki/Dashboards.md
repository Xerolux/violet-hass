> 🇬🇧 **English** | 🇩🇪 **[Deutsch](Dashboards.de)**

---

# 🎨 Dashboards & Pool Cards

The repository ships ready-made Lovelace dashboards and cards in the
[`Dashboard/`](https://github.com/Xerolux/violet-hass/tree/main/Dashboard) folder.
They are **not** installed by the integration — you copy the YAML you want into
your own dashboard.

---

## 📋 Table of Contents

1. [Which card should I use?](#-which-card-should-i-use)
2. [How to install a card](#-how-to-install-a-card)
3. [How to import a full dashboard](#-how-to-import-a-full-dashboard)
4. [Required custom cards (HACS)](#-required-custom-cards-hacs)
5. [Adapting the entity IDs](#-adapting-the-entity-ids)
6. [Troubleshooting](#-troubleshooting)

---

## 🧭 Which card should I use?

| File | What it is | Custom cards needed |
|------|-----------|---------------------|
| [`pool_control_simple_blocks.yaml`](https://github.com/Xerolux/violet-hass/blob/main/Dashboard/pool_control_simple_blocks.yaml) | Plain entity blocks — the best starting point | ❌ None |
| [`pool_control_card.yaml`](https://github.com/Xerolux/violet-hass/blob/main/Dashboard/pool_control_card.yaml) | Single overview card with control and monitoring | ❌ None |
| [`pool_control_compact.yaml`](https://github.com/Xerolux/violet-hass/blob/main/Dashboard/pool_control_compact.yaml) | Compact card for phones and tablets | ❌ None |
| [`pool_control_status.yaml`](https://github.com/Xerolux/violet-hass/blob/main/Dashboard/pool_control_status.yaml) | Switches with mode, runtime and speed underneath | ⚠️ `secondaryinfo-entity-row` (optional) |
| [`pool_control_ultimate.yaml`](https://github.com/Xerolux/violet-hass/blob/main/Dashboard/pool_control_ultimate.yaml) | Every control for every device, in one place | ✅ Mushroom, Slider Entity Row, Card Mod |
| [`pool-dashboard.yaml`](https://github.com/Xerolux/violet-hass/blob/main/Dashboard/pool-dashboard.yaml) | A complete multi-view dashboard | ⚠️ See file header |
| [`VIOLET_CARD_EXAMPLES.yaml`](https://github.com/Xerolux/violet-hass/blob/main/Dashboard/VIOLET_CARD_EXAMPLES.yaml) | Snippets to copy into your own cards | ⚠️ See file header |

> **New to this?** Start with `pool_control_simple_blocks.yaml`. It works on a
> plain Home Assistant installation with no extra downloads.

---

## 🃏 How to install a card

1. Open the raw YAML file on GitHub and copy its contents.
2. In Home Assistant, open your dashboard → **✏️ Edit dashboard**.
3. **➕ Add card** → scroll to the bottom → **Manual**.
4. Delete the placeholder content and paste the YAML.
5. Check the preview, then **Save**.

If the preview shows `Entity not available`, see
[Adapting the entity IDs](#-adapting-the-entity-ids).

---

## 🗂️ How to import a full dashboard

For `pool-dashboard.yaml`, which contains several views:

1. **Settings → Dashboards → ➕ Add dashboard → New dashboard from scratch.**
2. Open the new dashboard → **✏️ Edit dashboard**.
3. **⋮ (three dots) → Raw configuration editor.**
4. Paste the file contents, then **Save**.

---

## 📦 Required custom cards (HACS)

The richer cards use community cards. Install them via
**HACS → Frontend → ➕ Explore & download repositories**, then reload your
browser (Ctrl/Cmd + Shift + R):

| Card | HACS search term | Used by |
|------|------------------|---------|
| Mushroom | `Mushroom` | `pool_control_ultimate.yaml` |
| Slider Entity Row | `Slider Entity Row` | `pool_control_ultimate.yaml` |
| Card Mod | `card-mod` | `pool_control_ultimate.yaml` |
| Secondary Info Entity Row | `secondaryinfo-entity-row` | `pool_control_status.yaml` (optional) |

A missing custom card shows up as a red
`Custom element doesn't exist: mushroom-template-card` box.

---

## 🔤 Adapting the entity IDs

All examples use the default prefix `violet_pool_controller`, for example
`sensor.violet_pool_controller_pool_temperature`.

Your entity IDs differ if:

- **you named the device differently during setup** — the device name becomes
  the entity ID prefix;
- **you run more than one controller** — see [Multi-Controller](Multi-Controller);
- **the integration was set up before v2.3.4 on a non-English Home Assistant** —
  see the note below.

Find your actual IDs under **Developer tools → States**, filter for `violet`.
Then use your editor's search-and-replace on the pasted YAML.

### ℹ️ Entity IDs and the Home Assistant language

Home Assistant builds an entity ID from the entity's *translated* name for a
number of languages, German among them. On a German installation the pool
temperature sensor therefore used to be created as
`sensor.violet_pool_controller_wassertemperatur`, while the examples in this
repository — and every dashboard shared by other users — reference the English
`sensor.violet_pool_controller_pool_temperature`.

**Since v2.3.4 the integration always derives entity IDs from the English
name**, no matter which language Home Assistant runs in. Displayed names stay
translated — only the technical ID is now identical everywhere.

Entities that already exist keep their registered entity ID, because renaming
them would break your existing automations, scripts and dashboards. You have
three options:

| Option | Effect |
|--------|--------|
| **Leave everything as is** | Adapt the entity IDs in the copied YAML (search & replace). Nothing else breaks. |
| **Rename individual entities** | ⚙️ Entity settings → change the entity ID. Fine for a handful of entities. |
| **Re-add the integration** | Delete the integration entry and set it up again — all entities are recreated with English IDs. ⚠️ This also removes their history, customisations and any automation references. |

---

## 🩺 Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Entity not available` | Entity ID does not match your installation | [Adapt the entity IDs](#-adapting-the-entity-ids) |
| `Custom element doesn't exist: ...` | Custom card not installed | [Install it via HACS](#-required-custom-cards-hacs), then hard-refresh the browser |
| Card is empty | The feature is disabled in the integration options | Settings → Devices & Services → Violet Pool Controller → **Configure → Enable/disable features** |
| An entity you expected is missing | Feature disabled, sensor deselected, or the controller does not report it | See [Configuration](Configuration) and [Entities](Entities) |

---

## 🔗 Related pages

- [Entities](Entities) — every entity the integration can create
- [Configuration](Configuration) — features and sensor selection
- [Automation Examples](Automations)
- [Troubleshooting](Troubleshooting)
