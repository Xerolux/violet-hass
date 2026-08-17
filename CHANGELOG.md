# Changelog - Violet Pool Controller

> **Language Note:** This changelog is available in German. For English release notes, see the GitHub releases page.

## Version 2.4.0 (2026-08-17)

### 🐛 Fehlerbehebungen

- **Abfragen schlugen bei textuellen Zuständen komplett fehl** - die dynamische
  Intervallanpassung verglich `PUMP` und die `DOS_*`-Ausgänge direkt mit `0`.
  Liefert der Controller diese Werte als Text (`"1"`) oder als zusammengesetzten
  Zustand (`"3|PUMP_ANTI_FREEZE"`), warf der Vergleich einen `TypeError` — jeder
  Abrufzyklus endete in `UpdateFailed` und die Integration blieb dauerhaft nicht
  verfügbar. Die Zustände werden jetzt mit demselben Helfer interpretiert wie in
  den Switch-Entitäten.
- **Abrufintervall aus den Optionen wurde ignoriert** - das Intervall wurde bei
  jedem Poll erneut aus `config_entry.data` gelesen. Ein über *Konfigurieren →
  Einstellungen* gesetzter Wert galt damit nur bis zum ersten Abruf und fiel
  danach still auf den Wert der Ersteinrichtung zurück.
- **Nie schneller als konfiguriert** - lief die Pumpe, wurde das Intervall
  halbiert (mindestens 5 s). Der eingestellte Wert ist jetzt die schnellste
  Rate und wird nicht mehr unterschritten.
- **Gültige Einstellungen konnten die Einrichtung blockieren** - Config-Flow und
  Setup-Validierung waren sich über die erlaubten Bereiche uneinig (Intervall
  10-3600 s vs. 5-300 s, Timeout 1-60 s vs. 5-60 s). Ein in der Oberfläche
  angebotener Wert wie 600 s ließ die Integration beim nächsten Start mit
  „Invalid configuration" scheitern. Werte werden jetzt in den unterstützten
  Bereich geklemmt statt die Einrichtung abzubrechen.
- **„Reparieren"-Schaltfläche ohne Funktion** - das Problem „Pool-Controller
  nicht erreichbar" ist als behebbar gemeldet, es gab aber keinen zugehörigen
  Reparatur-Flow. Der Flow lädt die Integration jetzt neu und meldet zurück, ob
  der Controller wieder antwortet.
- **Sicherheits-Cooldown griff bei Schaltern nicht** - `_get_safety_guard()`
  suchte den Service-Manager mit `getattr()` in einem Dictionary, was einen
  Schlüssel niemals findet. Die SafetyGuard-Sperre war beim Schalten der
  Dosier-, Rückspül- und Nachfüll-Schalter damit immer wirkungslos.

### ✨ Neu

- **Abfrage im Ruhezustand reduzieren** (*Konfigurieren → Einstellungen ändern*,
  standardmäßig aktiv) - solange Pumpe, Heizung, Solar, Dosierung, Rückspülung
  und Nachfüllung aus sind, wird das Intervall verdreifacht (maximal 60 s). Das
  entlastet den Webserver des Controllers in den Stunden ohne Aktivität; sobald
  ein Ausgang läuft, gilt wieder das konfigurierte Intervall.

### 🔧 Technisch

- **Setpoints werden nicht mehr bei jedem Poll geholt** - die Werte hinter
  `getConfig` (Heiz-/Solar-Sollwerte, Dosier-Sollwerte, Firmware-Version)
  kosten eine zweite HTTP-Anfrage pro Zyklus, ändern sich aber nur beim
  Schreiben. Sie werden jetzt höchstens alle 60 s neu gelesen — beim
  Standardintervall von 10 s entfallen damit fünf von sechs Anfragen. Ein
  Schreibvorgang aus Home Assistant erzwingt das Nachlesen im nächsten Poll,
  eine fehlgeschlagene Abfrage behält die letzten bekannten Werte.
- **Laufzeitdaten liegen am Config-Entry** - Coordinator, Options-Snapshot,
  vorab angelegte Geräte-IDs, gemeldete Unique-IDs und die manuellen
  Sättigungsindex-Eingaben liegen jetzt in `entry.runtime_data` statt unter
  String-Schlüsseln in `hass.data[DOMAIN]`. Home Assistant räumt sie beim
  Entladen selbst weg, und per-Entry-Daten können nicht mehr mit
  integrationsweiten Objekten wie dem Service-Manager verwechselt werden.
- **mypy ist jetzt Teil der CI** - die zehn bestehenden Typfehler sind behoben
  (tote Zeroconf-Import-Fallbacks entfernt, Definitionslisten annotiert,
  `state_class` auf das Enum eingegrenzt); `tox -e py314` führt mypy aus.
- **Doppelter Registry-Durchlauf entfernt** - `_disable_unsafe_switches` lief
  pro Setup zweimal über die gesamte Entity-Registry. Der zweite Durchlauf war
  überflüssig, weil die Switch-Plattform `entity_registry_enabled_default` aus
  derselben Option ableitet. Die Liste der unsicheren Schalter stand zudem an
  zwei Stellen und liegt jetzt zentral in `const.py`.

## Version 2.3.5 (2026-08-16)

### 🗂️ Entitäten sind jetzt in Untergeräte gruppiert

Ein Controller liefert mehrere hundert Werte, die bisher alle unter einem
einzigen Gerät hingen — die Geräteseite war damit praktisch unbenutzbar. Die
Entitäten verteilen sich jetzt auf **12 Untergeräte**, die unterhalb des
Controllers hängen: Filterpumpe, Heizung, Solarabsorber, Dosierung &
Wasserchemie, Beleuchtung & DMX, Abdeckung, Rückspülung, Wassernachfüllung,
PV-Überschuss, Digitale Eingänge & Regeln, Erweiterungsmodule sowie System &
Diagnose.

Die Gruppen entsprechen den Features, die im Config-Flow an- und abgewählt
werden — die Geräteseite bildet also die gewählte Konfiguration ab. Untergeräte,
die leer bleiben (Hardware-Modul nicht vorhanden oder Feature deaktiviert),
werden automatisch entfernt. Gerätenamen sind auf Deutsch und Englisch übersetzt.

> **Entity-IDs bleiben unverändert.** Home Assistant leitet die Entity-ID aus dem
> Gerät ab, zu dem eine Entität gehört — die Gruppierung allein hätte neu
> angelegte Entitäten zu `sensor.filterpumpe_...` umbenannt und damit erneut die
> Dashboards zerschossen, deren Sprachabhängigkeit in 2.3.4 gerade beseitigt
> wurde. Die Entity-IDs sind deshalb fest an den Controller-Namen gebunden;
> `sensor.violet_pool_controller_pump_runtime` bleibt gültig.

Abschaltbar über **Konfigurieren → Einstellungen ändern → Entitäten in
Untergeräte gruppieren**; dann landen alle Entitäten wieder auf einem Gerät.

### 🐛 Fehlerbehebungen

- **`UNDEFINED`-Sentinel wird nicht mehr zu Text** - `strip_redundant_device_prefix()` prüfte nur auf `None`. `EntityDescription.name` hat als Standardwert aber `UNDEFINED` ("diese Entität hat keinen eigenen Namen"), was durch `str()` zu `"UndefinedType._singleton"` wurde und als Entitätsname gelandet wäre. In keiner veröffentlichten Version erreichbar, da jede Description einen Namen setzt — aber ein vergessenes `name=` davon entfernt.

### 🔧 Technisch

- **Eltern-Verknüpfung versionsabhängig** - `DeviceInfo.via_device` ist seit Home Assistant 2026.8 zugunsten von `via_device_id` deprecated (Entfernung angekündigt für 2027.8), beide gleichzeitig zu übergeben wirft einen Fehler. Da die Integration ab 2026.1 unterstützt wird, wo `via_device_id` noch nicht existiert, wird das passende Feld zur Laufzeit gewählt.
- **Geräte werden vorab angelegt** - Plattformen werden in unbestimmter Reihenfolge geladen; ohne vorab erzeugte Geräte fände die erste Entität ihr Elterngerät unter Umständen nicht. Haupt- und Untergeräte werden deshalb vor dem Laden der Plattformen erzeugt und ihre Registry-IDs zwischengespeichert.

## Version 2.3.4 (2026-08-16)

Diese Version behebt drei Punkte aus dem Nutzer-Feedback im
[poolsteuerung.de-Forum](https://www.poolsteuerung.de/viewtopic.php?t=2227):
die Feature-Auswahl blieb wirkungslos, die mitgelieferten Dashboards
funktionierten auf deutschen Installationen nicht, und die Pool-Karte war
nicht auffindbar.

### 🎛️ Feature- und Sensorauswahl wirkt jetzt wirklich

Wer bei der Einrichtung Features abwählte (z. B. sämtliche DMX-/LED-Beleuchtung),
sah trotzdem alle zugehörigen Entitäten. Dahinter steckten drei unabhängige
Fehler, alle behoben:

- **Kein Reload nach Änderung der Auswahl.** Die Entitätsliste entsteht beim
  Start der Plattformen aus der Auswahl — ohne Reload lief die Integration also
  unverändert weiter, bis Home Assistant das nächste Mal neu startete. Änderungen
  an Features, Sensorauswahl und unsicheren Schaltern starten die Integration
  jetzt automatisch neu. Alle übrigen Einstellungen (Polling-Intervall, Timeout,
  Zugangsdaten) werden weiterhin im laufenden Betrieb übernommen, ohne Reload.
- **Alte Entitäten blieben stehen.** Nicht mehr erzeugte Entitäten verharrten als
  dauerhaft nicht verfügbare "wiederhergestellte" Einträge im Entitätsregister.
  Jede Plattform meldet jetzt, welche Entitäten sie tatsächlich anlegt; alles
  andere wird beim Setup entfernt. Vom Benutzer deaktivierte und standardmäßig
  deaktivierte Entitäten bleiben dabei ausdrücklich erhalten.
- **DMX-Sensoren ignorierten das Feature.** Die rohen `DMX_SCENE*`-Messwerte
  hatten keine Feature-Zuordnung und wurden deshalb auch bei abgeschalteter
  Beleuchtung als Sensoren angelegt. Gleiches galt für `LIGHT_*`, Abdeckung,
  Rückspülung und PV-Überschuss. Alle sind jetzt korrekt zugeordnet.

### 🔤 Dashboards funktionieren jetzt auch auf Deutsch

Home Assistant bildet Entity-IDs aus dem **übersetzten** Namen der Entität — für
Deutsch und einige weitere Sprachen. Auf einer deutschen Installation entstand
dadurch `sensor.violet_pool_controller_wassertemperatur`, auf einer englischen
`sensor.violet_pool_controller_pool_temperature` — für dieselbe Entität. Jedes
geteilte Dashboard, jeder Forenschnipsel und alle Beispiele im `Dashboard/`-Ordner
waren damit sprachgebunden.

Neue Entitäten bekommen jetzt **immer die englische Entity-ID**, unabhängig von
der Sprache von Home Assistant. Die angezeigten Namen bleiben übersetzt — nur die
technische ID ist überall gleich.

**Bestehende Entitäten behalten ihre ID.** Ein automatisches Umbenennen würde
vorhandene Automationen, Skripte und Dashboards zerstören. Die
Migrationsmöglichkeiten stehen in der neuen
[Dashboards-Wiki-Seite](https://xerolux.github.io/violet-hass/docs/#/dashboards).

### 📖 Dokumentation

- **Neue Wiki-Seite "Dashboards & Pool-Karten"** (DE/EN) — welche Karte aus dem
  `Dashboard/`-Ordner wofür geeignet ist, wie man sie einbindet, welche
  HACS-Karten sie benötigt und wie man die Entity-IDs anpasst. Verlinkt aus
  README, Wiki-Sidebar und Doku-Navigation; zusätzlich liegt jetzt eine
  `Dashboard/README.md` direkt im Ordner.
- **Violet Pool Card dokumentiert** — die
  [Violet Pool Card](https://github.com/Xerolux/violet-pool-card) ist ein
  eigenständiges Projekt und wird **nicht** zusammen mit der Integration
  installiert. Das stand bisher nirgends. Die Wiki-Seite erklärt jetzt die
  Installation über HACS → Eigene Repositories. `VIOLET_CARD_EXAMPLES.yaml`
  bezeichnete die Karte fälschlich als "hypothetisch" und verweist nun auf das
  echte Repository.

### 🔧 Technisch

- **Testumgebung auf Home Assistant 2026.8.2 aktualisiert.** Die Testmatrix lief
  bislang gegen **HA 2025.1.4** — `tox.ini` pinnte
  `pytest-homeassistant-custom-component<0.13.317`, weil neuere Releases Python
  3.14 voraussetzen. Validiert wurde damit gegen eine über ein Jahr alte
  Core-Version. Die Tests laufen jetzt unter Python 3.14 gegen HA 2026.8.2;
  Linting zusätzlich weiterhin auf Python 3.12 und 3.13.
- **Mindestversion auf Home Assistant 2026.1.0 gesenkt** (war 2026.5.0). Der
  bisherige Wert stammte aus der Annahme, `ZeroconfServiceInfo` sei aus
  `homeassistant.components.zeroconf` entfernt worden — der Import hat aber
  längst einen `try`/`except`-Fallback auf
  `homeassistant.helpers.service_info.zeroconf`, sodass beide Varianten
  funktionieren. Die vollständige Testsuite läuft gegen HA 2026.1.3 durch.
- **`requirements.txt` beschreibt jetzt die Entwicklungs-/Testumgebung.** Die
  Datei wird ausschließlich von `tox` genutzt; die Laufzeitanforderungen der
  Integration stehen in `manifest.json`, die Mindestversion für Nutzer in
  `hacs.json`.
- **`test_validate_ph_value` an den echten Sollwertbereich angepasst.** Der Test
  erwartete eine obere pH-Grenze von 9.0; `violet-poolController-api` 0.0.37 hat
  sie bewusst auf 8.0 gesenkt, passend zu dem vom Controller akzeptierten
  Bereich. Der Test liest die Grenzen jetzt aus `SETPOINT_RANGES` des API-Pakets,
  statt sie fest zu verdrahten.

## Version 2.3.1 (2026-07-19)

### 🔧 Technische Verbesserungen

- **Reduzierte Server-Last beim Firmware-Update-Check** - Die Integration fragt `SYSTEM_updateavailable` (löste bisher alle 10 Sekunden einen Live-Server-Check aus, Wert wurde nicht verwendet) gar nicht mehr ab und holt `SYSTEM_availableversion` nur noch stündlich statt alle 10 Sekunden. Die Update-Verfügbarkeit wird weiterhin zuverlässig über Versionsvergleich ermittelt. Entlastet das Violet-Backend bei vielen Geräten deutlich.

### 📦 Dependencies

- **API-Client auf v0.0.36 angehoben** - `violet-poolController-api>=0.0.36` (war `>=0.0.35`). Die neue API-Version entfernt die fehlerhaften Duplikate `InputSanitizer.validate_speed` / `InputSanitizer.validate_duration` (clampeden still statt zu validieren). Die Integration nutzt jetzt die kanonische Modulfunktion `validate_duration` und eine eigene kleine `_validate_speed`-Hilfe. Ungültige Service-Eingaben (z.B. Duration außerhalb des erlaubten Bereichs) erzeugen nun eine saubere Home-Assistant-Fehlermeldung statt still korrigiert zu werden.

### 🧹 Repository-Aufräum

- **Verwaiste Dateien entfernt** - `BACKLOG_PROGRESS.md` (abgeschlossene Phase-1+2-Tracker), `CODEX_CONTEXT.md` (Agent-Memory eines nicht mehr genutzten Tools), `PHPBB_COMPLETE_CHANGELOG.txt` (statisches Forum-Artifact), `Dockerfile.test` (referenzierte ein nicht mehr existierendes Verzeichnis und war damit kaputt), `scripts/start-docker-test.ps1` (verwaist, Windows-only, hing von ignorierten Dateien ab) sowie 10 ungenutzte Screenshots wurden gelöscht.
- **CODEOWNERS konsolidiert** - Die redundante Root-Datei wurde entfernt; alle Regeln liegen nun kanonisch in `.github/CODEOWNERS`.

## Version 2.3.0 (2026-07-18)

### ✨ Neue Funktionen

- **Live-Status beim Firmware-Update** - Der "Aktualisieren"-Button wird während des 2–3 minütigen Updates sofort deaktiviert und zeigt den Live-Fortschritt der Steuerung an (via `getUpdateState`). Mehrfaches Klicken wird zuverlässig verhindert; der Status überlebt einen HA-Neustart oder Reload mitten im Update.

## ⚠️ BREAKING CHANGES - Version 2.0.0-beta.10

### 🚨 **SICHERHEIT: Automatische Deaktivierung kritischer Schalter**

**WICHTIG:** Ab dieser Version werden folgende Schalter **automatisch deaktiviert** für Sicherheit:

- **Dosierungsschalter** (Chlor, pH-, pH+, Flockmittel, Elektrolyse)
- **Rückspülung/Spülung** (Backwash/Rinse)
- **Wassernachfüllung** (Refill)

**Grund:** Diese Operationen können zu schweren Schäden führen, wenn sie ohne Zeitlimit laufen:
- ⚠️ **Chemische Überdosierung** → Wasserqualität beeinträchtigt, Gesundheitsrisiko
- ⚠️ **Ausrüstungsschaden** → Pumpen, Filter, Ventile zerstört
- ⚠️ **Überflutung** → Tank überläuft, Wasserschaden im Haus

**Neue Sicherheitslogik:**
1. ✅ Alle unsicheren Schalter sind **standardmäßig deaktiviert**
2. ✅ Services erfordern **Pflicht-Zeitangabe** für sichere Kontrolle
3. ✅ Benutzer können in Sicherheitseinstellungen manuell aktivieren (mit Warnung!)
4. ✅ Ausführliche Warnmeldungen im Log, wenn Schalter deaktiviert werden

**Was ändert sich für dich?**

| Vorher | Nachher |
|--------|---------|
| ❌ Schalter kann unbegrenzt laufen | ✅ Schalter deaktiviert (sicher) |
| ❌ Risiko von Schäden | ✅ Risiko minimiert |
| ❌ Manuelle Kontrolle ohne Limits | ✅ Services mit Pflicht-Zeitlimit |

**Wie nutze ich diese Schalter weiterhin?**

Nutze die **Services** stattdessen - sie erfordern eine Zeitangabe:
- `violet_pool_controller.smart_dosing` - für Dosierungen (pH-, pH+, Chlor, Flockmittel)
- `violet_pool_controller.control_pump` - für Pumpensteuerung
- `violet_pool_controller.manage_pv_surplus` - für PV-Überschuss-Steuerung
- Zusätzliche Services: `control_dmx_scenes`, `set_light_color_pulse`, `manage_digital_rules`, `test_output`

**Oder: Schalter manuell aktivieren (Experten)**

Wenn du die Risiken kennst und akzeptierst, kannst du die unsicheren Schalter aktivieren:
1. Gehe zu **Einstellungen → Geräte & Services → Violet Pool Controller**
2. Öffne **Optionen → 🚨 Sicherheitseinstellungen**
3. Aktiviere "Manuelle Steuerung kritischer Schalter erlauben"
4. ⚠️ Akzeptiere die Warnung und nutze Schalter mit Vorsicht!

---

## Version 2.0.0-beta.10

### ✨ Neue Funktionen

- **Sicherheitseinstellungen im Reconfigure-Flow** - Sicherheit kann jetzt ohne vollständige Neukonfiguration angepasst werden
- **Auto-Disable für unsichere Schalter** - Automatische Migration für bestehende Installationen

### 🐛 Bugfixes

- Behobener AttributeError bei `RegistryEntry.enabled` (sollte `disabled` sein)
- Korrekte Speicherung von Sicherheitseinstellungen in Config-Optionen
- Re-Enable-Logik für Schalter, wenn Sicherheitsüberschreibung aktiviert wird

### 🔧 Technische Verbesserungen

- Sicherheitseinstellungen jetzt in `options` statt `data` gespeichert
- Fallback-Prüfung (options → data) für Rückwärtskompatibilität
- Separate Reconfigure-Flows für Verbindung und Sicherheit
- SSL-Verifikation im Reconfigure-Flow konfigurierbar

---

## Version 2.0.0-beta.9

### ✨ Neue Funktionen

- OneWire-ROM-Code-Sensorunterstützung (zeigt Adresse statt °C)
- DI-Rule Verbleibzeit-Anzeige in lesbarem Format (1d 2h 30m 45s)
- Verbesserte Hardware-Modul-Erkennung (aktuell statt cached)

### 🐛 Bugfixes

- OneWire-ROM-Code zeigt jetzt korrekt Adresse statt Temperatur
- DI-Rule-Stoppuhr als Text-Sensor (nicht numerisch)
- Hardware-Module werden basierend auf aktuellen Daten erkannt

### 📦 Dependencies

- Aktualisiert auf violet-poolController-api 0.0.24

---

## Sicherheitsrichtlinie

Diese Integration kontrolliert kritische Poolausrüstung mit strikter Sicherheit:

**Siehe auch:** [⚠️ BREAKING CHANGES - Version 2.0.0-beta.10](#breaking-changes---version-200-0-beta10) für vollständige Informationen zur Sicherheitsimplementierung, automatischen Deaktivierung kritischer Schalter und erforderlichen Services mit Zeitlimits.

**Sicherheitsmerkmale:**
- ✅ Automatische Deaktivierung unsicherer Schalter (standardmäßig)
- ✅ Services erfordern obligatorische Zeitangaben
- ✅ Explizite Benutzer-Opt-in für manuelle Kontrolle (mit Warnungen)
- ✅ Umfassendes Logging bei kritischen Operationen

**Kontakt & Support:**
- GitHub Issues: https://github.com/Xerolux/violet-hass/issues
- E-Mail: git@xerolux.de
