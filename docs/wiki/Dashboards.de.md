> 🇩🇪 **Deutsch** | 🇬🇧 **[English](Dashboards)**

---

# 🎨 Dashboards & Pool-Karten

Im Ordner [`Dashboard/`](https://github.com/Xerolux/violet-hass/tree/main/Dashboard)
liegen fertige Lovelace-Dashboards und -Karten. Sie werden **nicht** automatisch
von der Integration installiert — du kopierst dir das gewünschte YAML selbst in
dein Dashboard.

---

## 📋 Inhaltsverzeichnis

1. [Welche Karte soll ich nehmen?](#-welche-karte-soll-ich-nehmen)
2. [Karte einbinden](#-karte-einbinden)
3. [Komplettes Dashboard importieren](#-komplettes-dashboard-importieren)
4. [Benötigte Custom Cards (HACS)](#-benötigte-custom-cards-hacs)
5. [Entity-IDs anpassen](#-entity-ids-anpassen)
6. [Fehlerbehebung](#-fehlerbehebung)

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
| [`VIOLET_CARD_EXAMPLES.yaml`](https://github.com/Xerolux/violet-hass/blob/main/Dashboard/VIOLET_CARD_EXAMPLES.yaml) | Bausteine zum Kopieren in eigene Karten | ⚠️ Siehe Dateikopf |

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
