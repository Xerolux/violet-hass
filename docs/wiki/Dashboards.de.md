> 🇩🇪 **Deutsch** | 🇬🇧 **[English](Dashboards)**

---

# 🎨 Dashboards & Pool-Karten

Im Ordner [`Dashboard/`](https://github.com/Xerolux/violet-hass/tree/main/Dashboard)
liegen fertige Lovelace-Dashboards und -Karten. Sie werden **nicht** automatisch
von der Integration installiert — du kopierst dir das gewünschte YAML selbst in
dein Dashboard.

---

## 📋 Inhaltsverzeichnis

1. [Die Violet Pool Card](#-die-violet-pool-card)
2. [Welche Karte soll ich nehmen?](#-welche-karte-soll-ich-nehmen)
3. [Karte einbinden](#-karte-einbinden)
4. [Komplettes Dashboard importieren](#-komplettes-dashboard-importieren)
5. [Benötigte Custom Cards (HACS)](#-benötigte-custom-cards-hacs)
6. [Entity-IDs anpassen](#-entity-ids-anpassen)
7. [Fehlerbehebung](#-fehlerbehebung)

---

## 💎 Die Violet Pool Card

Neben den YAML-Beispielen in diesem Repository gibt es eine **eigens für diese
Integration entwickelte Lovelace-Karte**:

**➡️ [Xerolux/violet-pool-card](https://github.com/Xerolux/violet-pool-card)**

Sie bietet 28 Kartentypen (Pumpe, Heizung, Solar, Dosierung, Abdeckung, Licht,
Filter, Chemie, Rückspülung, Nachfüllung, Durchfluss, Digital Rules,
Diagnostics und mehr), sieben Themes, einen grafischen Editor und automatische
Entity-Erkennung.

> **Wichtig:** Die Karte ist ein **eigenständiges Projekt** mit eigenem
> Repository und eigenem Release-Zyklus. Sie wird **nicht** zusammen mit der
> Integration installiert — du musst sie in HACS selbst hinzufügen.

### Installation

1. Die Violet-Pool-Controller-Integration (dieses Repository) installieren und einrichten.
2. **HACS → Frontend → ⋮ (Drei-Punkte-Menü) → Eigene Repositories**
3. Repository: `https://github.com/Xerolux/violet-pool-card`
   Kategorie: **Dashboard** → **Hinzufügen**
4. Nach **Violet Pool Card** suchen und herunterladen.
5. **Home Assistant neu starten** und den Browser hart neu laden (Strg/Cmd + Umschalt + R).
6. Im Dashboard eine Karte hinzufügen und **Violet Pool Card** auswählen.

Konfigurationsbeispiele stehen in
[`Dashboard/VIOLET_CARD_EXAMPLES.yaml`](https://github.com/Xerolux/violet-hass/blob/main/Dashboard/VIOLET_CARD_EXAMPLES.yaml)
und in der README der Karte.

> Du willst nichts zusätzlich installieren? Alle übrigen Dateien in `Dashboard/`
> funktionieren mit den Standardkarten von Home Assistant — siehe Tabelle unten.

---

## 🧭 Welche Karte soll ich nehmen?

| Datei | Was es ist | Custom Cards nötig |
|-------|-----------|--------------------|
| [`pool_control_simple_blocks.yaml`](https://github.com/Xerolux/violet-hass/blob/main/Dashboard/pool_control_simple_blocks.yaml) | Einfache Entity-Blöcke — der beste Einstieg | ❌ Keine |
| [`pool_control_card.yaml`](https://github.com/Xerolux/violet-hass/blob/main/Dashboard/pool_control_card.yaml) | Übersichtskarte mit Steuerung und Überwachung | ❌ Keine |
| [`pool_control_compact.yaml`](https://github.com/Xerolux/violet-hass/blob/main/Dashboard/pool_control_compact.yaml) | Kompakte Karte für Handy und Tablet | ❌ Keine |
| [`pool_control_status.yaml`](https://github.com/Xerolux/violet-hass/blob/main/Dashboard/pool_control_status.yaml) | Schalter mit Modus, Laufzeit und Drehzahl darunter | ⚠️ `secondaryinfo-entity-row` (optional) |
| [`pool_control_ultimate.yaml`](https://github.com/Xerolux/violet-hass/blob/main/Dashboard/pool_control_ultimate.yaml) | Alle Steuerungen für jedes Gerät auf einen Blick | ✅ Mushroom, Slider Entity Row, Card Mod |
| [`pool-dashboard.yaml`](https://github.com/Xerolux/violet-hass/blob/main/Dashboard/pool-dashboard.yaml) | Komplettes Dashboard mit mehreren Ansichten | ⚠️ Siehe Dateikopf |
| [`VIOLET_CARD_EXAMPLES.yaml`](https://github.com/Xerolux/violet-hass/blob/main/Dashboard/VIOLET_CARD_EXAMPLES.yaml) | Konfigurationen für die Violet Pool Card | ✅ [Violet Pool Card](#-die-violet-pool-card) |

> **Zum ersten Mal dabei?** Fang mit `pool_control_simple_blocks.yaml` an. Die
> Karte funktioniert ohne Zusatzinstallationen.

---

## 🃏 Karte einbinden

1. Die gewünschte YAML-Datei auf GitHub öffnen und den Inhalt kopieren.
2. In Home Assistant das Dashboard öffnen → **✏️ Dashboard bearbeiten**.
3. **➕ Karte hinzufügen** → ganz nach unten scrollen → **Manuell**.
4. Den Platzhalter löschen und das YAML einfügen.
5. Vorschau prüfen, dann **Speichern**.

Zeigt die Vorschau `Entität nicht verfügbar`, siehe
[Entity-IDs anpassen](#-entity-ids-anpassen).

---

## 🗂️ Komplettes Dashboard importieren

Für `pool-dashboard.yaml` mit mehreren Ansichten:

1. **Einstellungen → Dashboards → ➕ Dashboard hinzufügen → Neues Dashboard von Grund auf.**
2. Neues Dashboard öffnen → **✏️ Dashboard bearbeiten**.
3. **⋮ (drei Punkte) → Raw-Konfigurationseditor.**
4. Dateiinhalt einfügen, dann **Speichern**.

---

## 📦 Benötigte Custom Cards (HACS)

Die aufwändigeren Karten nutzen Community-Karten. Installation über
**HACS → Frontend → ➕ Repositories durchsuchen & herunterladen**, danach den
Browser neu laden (Strg/Cmd + Umschalt + R):

| Karte | Suchbegriff in HACS | Wird verwendet von |
|-------|---------------------|--------------------|
| Mushroom | `Mushroom` | `pool_control_ultimate.yaml` |
| Slider Entity Row | `Slider Entity Row` | `pool_control_ultimate.yaml` |
| Card Mod | `card-mod` | `pool_control_ultimate.yaml` |
| Secondary Info Entity Row | `secondaryinfo-entity-row` | `pool_control_status.yaml` (optional) |
| Violet Pool Card | eigenes Repository, siehe [oben](#-die-violet-pool-card) | `VIOLET_CARD_EXAMPLES.yaml` |

Eine fehlende Custom Card erscheint als roter Kasten
`Custom element doesn't exist: mushroom-template-card`.

---

## 🔤 Entity-IDs anpassen

Alle Beispiele verwenden das Standard-Präfix `violet_pool_controller`, also z. B.
`sensor.violet_pool_controller_pool_temperature`.

Deine Entity-IDs weichen ab, wenn:

- **du das Gerät bei der Einrichtung anders benannt hast** — der Gerätename wird
  zum Präfix der Entity-ID;
- **du mehrere Controller betreibst** — siehe [Multi-Controller](Multi-Controller.de);
- **die Integration vor v2.3.4 auf einem deutschsprachigen Home Assistant
  eingerichtet wurde** — siehe Hinweis unten.

Deine tatsächlichen IDs findest du unter **Entwicklerwerkzeuge → Zustände**,
Filter `violet`. Danach im eingefügten YAML per Suchen-und-Ersetzen anpassen.

### ℹ️ Entity-IDs und die Home-Assistant-Sprache

Home Assistant bildet die Entity-ID aus dem *übersetzten* Namen der Entität —
für Deutsch und einige weitere Sprachen. Auf einer deutschen Installation hieß
der Pool-Temperatursensor deshalb bisher
`sensor.violet_pool_controller_wassertemperatur`, während die Beispiele in
diesem Repository — und jedes von anderen geteilte Dashboard — die englische ID
`sensor.violet_pool_controller_pool_temperature` verwenden.

**Seit v2.3.4 bildet die Integration die Entity-IDs immer aus dem englischen
Namen**, unabhängig von der Sprache von Home Assistant. Die angezeigten Namen
bleiben übersetzt — nur die technische ID ist jetzt überall gleich.

Bereits vorhandene Entitäten behalten ihre registrierte Entity-ID, weil ein
Umbenennen deine bestehenden Automationen, Skripte und Dashboards zerstören
würde. Du hast drei Möglichkeiten:

| Möglichkeit | Auswirkung |
|-------------|-----------|
| **Alles so lassen** | Die Entity-IDs im kopierten YAML anpassen (Suchen & Ersetzen). Sonst ändert sich nichts. |
| **Einzelne Entitäten umbenennen** | ⚙️ Entitätseinstellungen → Entity-ID ändern. Praktikabel bei wenigen Entitäten. |
| **Integration neu einrichten** | Integrationseintrag löschen und neu anlegen — alle Entitäten werden mit englischen IDs neu erstellt. ⚠️ Dabei gehen Verlauf, Anpassungen und Verweise in Automationen verloren. |

---

## 🩺 Fehlerbehebung

| Symptom | Ursache | Lösung |
|---------|---------|--------|
| `Entität nicht verfügbar` | Entity-ID passt nicht zu deiner Installation | [Entity-IDs anpassen](#-entity-ids-anpassen) |
| `Custom element doesn't exist: ...` | Custom Card nicht installiert | [Über HACS installieren](#-benötigte-custom-cards-hacs), danach Browser hart neu laden |
| Karte bleibt leer | Das Feature ist in den Integrationsoptionen deaktiviert | Einstellungen → Geräte & Dienste → Violet Pool Controller → **Konfigurieren → Features aktivieren/deaktivieren** |
| Eine erwartete Entität fehlt | Feature deaktiviert, Sensor abgewählt oder der Controller liefert den Wert nicht | Siehe [Konfiguration](Configuration.de) und [Entitäten](Entities.de) |

---

## 🔗 Verwandte Seiten

- [Entitäten](Entities.de) — alle Entitäten der Integration
- [Konfiguration](Configuration.de) — Features und Sensorauswahl
- [Automationsbeispiele](Automations.de)
- [Fehlerbehebung](Troubleshooting.de)
