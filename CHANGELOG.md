# Changelog - Violet Pool Controller

> **Diese Integration entsteht in meiner Freizeit — und ist komplett kostenlos.**
> Wenn sie dir das Leben mit deinem Pool leichter macht und du die Entwicklung
> unterstützen möchtest, freue ich mich riesig. Kein Muss, aber mega
> motivierend! 😊☕

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Spendier%20mir%20einen%20Kaffee!-yellow?logo=buy-me-a-coffee&style=for-the-badge)](https://buymeacoffee.com/xerolux)
[![PayPal](https://img.shields.io/badge/PayPal-Danke%20f%C3%BCr%20deine%20Unterst%C3%BCtzung!-blue?logo=paypal&style=for-the-badge)](https://paypal.me/xerolux)

---

Dieser Changelog ist auf Deutsch. Der Abschnitt zur jeweiligen Version wird
beim Release automatisch zum Text der GitHub-Release-Seite — was hier nicht
steht, erfährt also auch niemand dort.

> **Language Note:** This changelog is written in German.

## Version 2.5.2 (2026-08-18)

Patch-Release: neun Entity-IDs, die noch die in 2.5.0/2.5.1 korrigierte falsche
Bezeichnung im Namen tragen, werden einmalig umbenannt. **Achtung: Entity-IDs
ändern sich** — Dashboards und Automationen, die genau diese neun IDs
referenzieren, müssen angepasst werden. Alle anderen Entitäten bleiben
unangetastet.

### 🐛 Behoben

- **Die Entity-ID blieb auf der falschen Bezeichnung stehen.** Home Assistant
  bildet eine Entity-ID einmalig bei der Registrierung und schreibt sie danach
  nie wieder um. Ein korrigierter Anzeigename half also nichts: die
  Elektrolyse-Restlaufzeit hing weiter unter
  `sensor.violet_pool_controller_elektrolyse_kanisterinhalt_ml` — eine Laufzeit
  in Stunden, deren ID einen Kanisterfüllstand in Millilitern behauptet.
  Betroffen sind genau die neun Entitäten, deren Bezeichnung in 2.5.0/2.5.1
  falsch war: die drei Elektrolyse-Sensoren, die fünf `DOS_*_USE`-Flags und
  `CPU_TEMP_CARRIER`. Sie wandern jetzt beim nächsten Start auf die ID, die
  eine Neuinstallation ohnehin vergeben würde, und jede Umbenennung steht als
  Warnung im Log.
- **Umbenannt wird nur, was die falsche Bezeichnung wirklich enthält.** Wer
  eine dieser Entitäten selbst umbenannt hat, behält seine ID. Ist die
  Ziel-ID schon belegt, passiert ebenfalls nichts — zwei kaputte Entitäten
  wären schlimmer als eine unschöne ID. Beim ersten Start einer neuen
  Installation gibt es nichts umzubenennen.

### 🔧 Technisch

- **Die beiden pH-Kanäle bekommen unterscheidbare IDs.** „pH-" und „pH+"
  werden beide zu `ph` verschliffen, die zwei `_USE`-Sensoren hätten sich also
  dieselbe ID geteilt. Die englischen Namen heißen deshalb „pH Minus Dosing
  Configured" und „pH Plus Dosing Configured"; die deutschen Anzeigenamen
  bleiben wie sie sind.

### 🧪 Tests

- 10 neue Tests (713 → 723): die gemeldete Umbenennung selbst, Idempotenz über
  mehrere Starts, eine vom Nutzer gewählte ID bleibt stehen, eine belegte
  Ziel-ID wird nicht überschrieben, Entitäten außerhalb der Tabelle werden nie
  angefasst, und eine korrigierte Bezeichnung darf nie wieder auf ihre eigene
  Wortliste passen — sonst würde die ID bei jedem Start weiterwandern.

## Version 2.5.1 (2026-08-18)

Patch-Release direkt hinter 2.5.0: die Elektrolyse-Tagesproduktion bekommt die
Einheit, die 2.5.0 offengelassen hat. **Keine Migration nötig**, Entity-IDs,
Unique IDs und die API-Paarung bleiben unverändert.

### 🐛 Behoben

- **Elektrolyse-Tagesproduktion zählt Chlor, jetzt auch mit Einheit.** In 2.5.0
  hatte der Sensor keine Einheit mehr, weil Milliliter für eine Zelle sicher
  falsch sind — was er stattdessen zählt, war offen. Geklärt: eine
  Salzwasser-Elektrolyse wird in **Gramm Chlor pro Stunde** ausgelegt (Faustregel
  Pool-Volumen in m³ ÷ 4, ein 50-m³-Pool also rund 12 g/h), der Controller
  zählt in **Milligramm**. Der Sensor trägt jetzt `mg` und ist als Gewicht
  gekennzeichnet — damit bietet Home Assistant die Umrechnung auf Gramm direkt
  in den Entitätseinstellungen an, ohne Template-Sensor.
  *Hinweis:* Wer 2.5.0 schon installiert hat, bekommt für diesen Sensor noch
  einmal den Hinweis auf einen Einheitenwechsel.

### 🧪 Tests

- Der Test zur Tagesproduktion prüft jetzt Milligramm und die Gewichts-Device-Class
  statt „keine Einheit"; die Zuordnung Masse-Einheit → Device Class deckt
  `mg`, `g` und `kg` ab.

## Version 2.5.0 (2026-08-18)

Minor-Release mit zwei Schwerpunkten: die Datenpunkt-Auswahl gilt jetzt für
**alle** Plattformen statt nur für Sensoren, und eine Reihe von Entitäten trägt
endlich den Namen, der zu ihrem Messwert passt — angefangen bei der
Elektrolyse, die nie einen Kanister hatte. **Kein Entitätsverlust durch das
Update** — eine Migration auf Config-Entry-Version 3 friert den heutigen Stand
ein; das Ausmisten bleibt danach deine Entscheidung. Entity-IDs, Unique IDs und
die API-Paarung bleiben unverändert.

### 🐛 Behoben

- **Elektrolyse: „Kanisterinhalt (ml)" war die falsche Bezeichnung.** Aus dem
  Forum gemeldet: der Wert hinter diesem Sensor ist die **Restlaufzeit der
  Elektrolysezelle in Stunden**, nicht der Füllstand eines Kanisters — die
  Elektrolyse hat gar keinen. Der Controller belegt bei `DOS_2_ELO` dieselben
  zwei Felder des Dosiercontrollers mit Zellenwerten; die Firmware überwacht
  genau diese Zahl mit den Fehlercodes 133 („Elektrolyse Restlaufzeit") und 134
  („max. Betriebszeit Elektrolyse-Zelle"). Der Sensor heißt jetzt
  **Elektrolysezelle Restlaufzeit**, zählt in Stunden und ist als Dauer
  gekennzeichnet. Aus demselben Grund heißt der Tageswert jetzt
  **Elektrolyse-Tagesproduktion** und trägt keine Milliliter-Einheit mehr, und
  der Kanister-Reset wurde zum **Zellen-Reset**. Die Milliliter bleiben dort,
  wo tatsächlich aus einem Kanister dosiert wird: Chlor, pH-, pH+ und Flockung.
  *Hinweis:* Home Assistant meldet für die beiden Elektrolyse-Sensoren einen
  Einheitenwechsel und bietet an, die Langzeitstatistik anzupassen oder zu
  verwerfen — die alten Werte waren in der falschen Einheit erfasst.
- **`DOS_*_USE` hieß „Verbrauch", ist aber ein Konfigurations-Flag.** Der Wert
  ist 0/1 und sagt nur, ob der Dosierkanal in der Anlagenkonfiguration
  aktiviert ist — mit Verbrauch hat er nichts zu tun. Heißt jetzt
  „… konfiguriert" (alle fünf Kanäle, alle zehn Sprachen).
- **`CPU_TEMP_CARRIER` hieß „Träger-Platine".** Der Sensor liefert deren
  CPU-Temperatur und heißt jetzt auch so.
- **27 Entitäten zeigten allen Nutzern den deutschen Namen.** Die zwölf
  DMX-Szenen, die sechs OMNI-DC-Ausgänge samt Modus-Auswahl, der
  Elektrolyse-Schalter, ECO und die Wassernachfüllung hatten in keiner Sprache
  eine Übersetzung — Home Assistant fällt in dem Fall auf den fest im Code
  hinterlegten deutschen Namen zurück. Dazu kamen 30 Sensoren im selben
  Zustand (Analog- und Temperaturregeln, OMNI-Laufzeiten, Elektrolyse-Polarität
  und -Umkehrlaufzeit, letzte Fehler-ID). Alle sind jetzt in allen zehn
  Sprachen benannt; die neuen Auswahl-Entitäten haben zusätzlich übersetzte
  Optionen statt roher `off`/`on`/`auto`-Werte.
- **Die fünf „verbleibende Reichweite"-Sensoren fanden ihre Übersetzung nie.**
  Der Schlüssel wurde als `1_cl_remaining_range` erzeugt, hinterlegt war
  `dos_1_cl_remaining_range` — ein fehlendes Präfix, das die vorhandene
  Übersetzung für alle Kanäle unerreichbar machte.

### ✨ Neu

- **Die Auswahl gilt für Schalter, Binärsensoren, Auswahl-Entitäten und
  Lichter.** Bis 2.4.1 wurde `selected_sensors` ausschließlich von der
  Sensor-Plattform gelesen, obwohl der Auswahlschritt die rohen Controller-Keys
  auflistet (`ECO`, `PUMP`, `DMX_SCENE1`, …). Wer `ECO` abwählte, verlor den
  ECO-Sensor und behielt Schalter, Binärsensor und Auswahl — der in 2.4.1
  gemeldete Fehler. Jede Entität, die aus einem Controller-Key entsteht, folgt
  jetzt derselben Auswahl. Entitäten **ohne** Controller-Key bleiben bewusst
  außen vor: Systemzustand, Verbindungslatenz, Firmware-Update und die
  Sättigungsindex-Rechner tauchen in `getReadings` gar nicht auf, können also
  auch nicht in der Liste stehen.
- **Ohne gespeicherte Auswahl bleibt alles.** Eine Config Entry, die den
  Auswahlschritt nie durchlaufen hat, verliert nichts — „nichts gespeichert“
  heißt weiterhin „alles anzeigen“. Eine *leere* Auswahl ist dagegen eine
  bewusste Entscheidung und wird als solche behandelt.

### 🔧 Technisch

- **Migration auf Config-Entry-Version 3.** Bestehende Auswahlen wurden
  getroffen, als sie nur über Sensoren entschieden: wer `PUMP` abwählte, um den
  rohen Messwert loszuwerden, wollte damit nicht seinen Pumpen-Schalter
  verlieren. Die Migration ergänzt deshalb einmalig die Keys aller
  Nicht-Sensor-Entitäten. Hinzufügen kann eine Entität nur erhalten, nie
  entfernen — Feature-Gates und die Prüfung „Key ist in der Controller-Antwort
  vorhanden“ greifen unverändert darüber.
- **Migrationskette repariert.** Die 2.4.1-Migration setzte die Version direkt
  auf den Endstand statt auf ihr eigenes Ziel. Bei einem Sprung von Version 1
  auf 3 wäre der zweite Schritt dadurch übersprungen worden. Jeder Schritt
  zählt jetzt einzeln hoch; ein Test deckt genau diesen Sprung ab.
- **Auswahlschritt-Text wieder angeglichen** (alle zehn Sprachen): der in 2.4.1
  ergänzte Hinweis „betrifft nur Sensor-Entitäten“ stimmt nicht mehr und ist
  entfernt. Dort steht jetzt, dass jede aus einem Datenpunkt entstehende
  Entität der Auswahl folgt.

### 🧪 Tests

- 48 neue Tests (665 → 713). 16 zur Auswahl-Semantik (nichts gespeichert, leere
  Auswahl, Optionen schlagen Daten, synthetische Entitäten), Abdeckung aller
  vier Steuer-Plattformen und sechs Migrationsfälle — darunter der Sprung von
  Version 1 direkt auf 3.
- 32 zu den Bezeichnungen: jeder Übersetzungsschlüssel jeder Entitätsdefinition
  muss in `de.json` und `en.json` auflösbar sein — genau das war die Ursache
  der deutschen Namen und der ins Leere laufenden Reichweiten-Schlüssel. Dazu
  Prüfungen, dass auf dem Elektrolyse-Kanal nirgends mehr „Kanister" steht, die
  Milliliter auf den Flüssigkeits-Kanälen bleiben und kein `_USE`-Sensor als
  Verbrauch auftritt.

## Version 2.4.1 (2026-08-17)

Patch-Release: ein aus dem Forum gemeldeter Fehler, bei dem abgewählte
Entitäten sichtbar blieben, dazu ein neuer Blueprint für kühlfähige
Wärmepumpen. **Vollständig abwärtskompatibel** — eine Migration der Config
Entry auf Version 2 sorgt dafür, dass keine bestehende Installation durch das
Update eine Entität verliert. Entity-IDs, Unique IDs und die API-Paarung
(`violet-poolController-api>=0.0.36`) bleiben unverändert.

### 🐛 Behoben

- **Abgewählte ECO- und DMX-Entitäten blieben sichtbar.** Gemeldet im
  [poolsteuerung.de-Forum](https://www.poolsteuerung.de/viewtopic.php?t=2227):
  bei der Einrichtung alles rund um ECO und DMX abgewählt, nach dem
  HA-Neustart trotzdem alles da. Ursache ist, dass die **Sensorauswahl
  ausschließlich von der Sensor-Plattform gelesen wird** — die übrigen neun
  Plattformen (Schalter, Binärsensoren, Auswahl, Licht, Zahl, Klima,
  Abdeckung, Knopf, Update) richten sich allein nach der Feature-Liste. Der
  Auswahlschritt zeigt aber die rohen Controller-Keys (`ECO`, `DMX_SCENE1`,
  …), liest sich also wie „welche Datenpunkte will ich haben“, und deckte
  davon nur die Sensoren ab. Was in 2.3.4 behoben wurde, war etwas
  Benachbartes: dass die Auswahl überhaupt *wirksam* wird (Reload und
  Entfernen verwaister Registry-Einträge). Die Reichweite der Auswahl blieb
  unverändert.
- **ECO ließ sich überhaupt nicht entfernen.** Schalter, Binärsensor und
  Auswahl hatten kein Feature hinterlegt, und in der Feature-Liste gab es
  keinen ECO-Eintrag — es existierte also keine Einstellung, die diese drei
  Entitäten hätte abschalten können. Abwählen im Sensorschritt entfernte nur
  `ECO` und `ECO_RUNTIME`, die zwei Sensoren. Es gibt jetzt das Feature **„ECO
  Mode“**, das alle vier Entitäten gemeinsam schaltet. Eine Auswertung
  sämtlicher Entitätsdefinitionen bestätigt: ECO war die einzige
  standardmäßig aktive Entität ohne Feature. Die übrigen 16 ungegateten
  Definitionen sind durchweg Diagnose-Entitäten, die deaktiviert ausgeliefert
  werden und deshalb niemandem ungefragt erscheinen.
- **Die zwölf DMX-Szenen hingen am Poollicht.** Sie waren dem Feature „LED
  Lighting“ zugeordnet, weshalb das Abwählen der DMX-*Sensoren* sie nicht
  berührte. Die Szenen sind jetzt das eigene Feature **„DMX Scenes“** —
  Poollicht behalten und trotzdem zwölf Szenen-Entitäten loswerden ist damit
  möglich. Die DMX-Sensoren folgen dem neuen Feature, das einfache `LIGHT`
  bleibt bei „LED Lighting“.
- **Sicherheits-Cooldown griff bei Schaltern nicht** *(bereits in 2.4.0
  enthalten, hier nachgetragen)* — `_get_safety_guard()` suchte den
  Service-Manager mit `getattr()` in einem Dictionary, was einen Schlüssel
  niemals findet.

### ✨ Neu

- **Blueprint „Heat Pump Heating & Cooling“.** Der Violet-Controller kann nicht
  kühlen: seine API kennt genau zwei Wärme-Ausgänge, `HEATER` und `SOLAR`,
  beide heizend, und `setFunctionManually` hat keinen Kühlbefehl. Ein
  `cool`-Modus an den Climate-Entitäten wäre eine Fähigkeit, die die Hardware
  nicht ausführen kann. Wer kühlt, tut das mit einer Wärmepumpe über deren
  eigene Integration — der neue Blueprint
  (`blueprints/automation/pool_heatpump_cooling.yaml`) verbindet beides an der
  Stelle, an die diese Kopplung gehört, in einer Automation: ein
  `input_number`-Helper hält die Solltemperatur und wird auf die Wärmepumpe
  durchgeschrieben, sodass der in Home Assistant angezeigte Wert auch der
  geregelte ist. Pool über Soll + Hysterese → `cool`, unter Soll − Hysterese →
  `heat`, dazwischen ein konfigurierbarer Ruhemodus. Optional wird der
  Violet-Heizsollwert auf einer Freigabetemperatur gehalten, damit der
  Controller das Ventil offen lässt — der verbreitete Workaround, aber
  explizit und dokumentiert statt als stille Falle in der Oberfläche. Ein
  Modus wird nur gesendet, wenn die Wärmepumpe ihn in `hvac_modes` meldet, und
  solange ein Messwert `unavailable` ist, wird gar nichts geschrieben.

### 🔧 Technisch

- **Migration auf Config-Entry-Version 2.** Bestehende Konfigurationen kennen
  die neuen Feature-IDs nicht, und eine unbekannte ID zählt als „aus“ — ohne
  Migration wären ECO und die DMX-Szenen beim Update bei *allen* Nutzern still
  verschwunden. `eco_mode` wird deshalb aktiviert (war immer an), `dmx_scenes`
  übernimmt die bisherige Einstellung von `led_lighting`. Wer die Beleuchtung
  abgeschaltet hatte, bekommt also nicht plötzlich zwölf Szenen dazu.
- **Klarerer Text im Sensorschritt** (alle zehn Sprachen): dort steht jetzt,
  dass die Auswahl nur Sensor-Entitäten betrifft und Schalter, Lichter sowie
  übrige Bedienelemente zu den Features gehören. Die vollständige Ausweitung
  der Auswahl auf alle Plattformen ist für 2.5.0 vorgesehen; sie braucht eine
  eigene Migration, weil bestehende Auswahlen im Sensor-Kontext getroffen
  wurden.
- **Der Changelog ist jetzt der Release-Text.** Bis 2.4.0 enthielt die
  GitHub-Release-Seite nur die automatisch erzeugte PR-Liste. Der Release-Job
  liest jetzt den Abschnitt zur jeweiligen Version aus dieser Datei und bricht
  ab, wenn es keinen gibt.

### 🧪 Tests

- **Regel gegen die Wiederkehr der Lücke:** jede standardmäßig aktive Entität
  muss ein Feature nennen, und jedes genannte Feature muss im Config-Flow
  existieren — für Schalter, Binärsensoren, Auswahl, Licht und die
  Sensor-Zuordnung. Dazu sieben Migrationstests, die unter anderem absichern,
  dass DMX bei abgeschalteter Beleuchtung *nicht* hinzukommt.
- **Blueprints werden erstmals überhaupt geprüft.** Sie waren reines YAML, das
  im Build nie jemand geladen hat — ein Tippfehler wäre erst beim Import durch
  einen Nutzer aufgefallen. Alle fünf werden jetzt mit Home Assistants eigenem
  `AUTOMATION_BLUEPRINT_SCHEMA` geparst; beim neuen werden zusätzlich die
  eingesetzten Trigger, Bedingungen und Aktionen validiert, einmal mit
  vollständigen und einmal ohne die optionalen Eingaben.

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
