# KI-Anweisung: Steuer-Konstanten im API-Paket wiederherstellen

> Diese Datei enthält einen fertigen Prompt zum Kopieren. Füge ihn in eine
> Claude-Code-Session ein, die auf dem Repo
> **`Xerolux/violet-poolController-api`** läuft.

---

## Prompt (alles ab hier kopieren)

**Kontext:** Die Home-Assistant-Integration `violet_pool_controller` importiert
Steuer-Konstanten aus diesem Paket per
`from violet_poolcontroller_api.const_devices import *` und
`from violet_poolcontroller_api.const_api import *`. In Version **0.0.24** wurden
diese Konstanten entfernt, wodurch die Integration nicht mehr lud
(`Integration 'violet_pool_controller' not found`).

**Aufgabe:** Stelle die folgenden öffentlichen Konstanten wieder her, damit sie
als stabiler Vertrag erhalten bleiben. Lege sie im passenden Modul ab
(`const_api.py` für die `ACTION_*`-Befehlsstrings, `const_devices.py` für die
geräte-/cover-bezogenen Konstanten) und stelle sicher, dass sie über `import *`
exportiert werden (falls ein `__all__` existiert, dort ergänzen). Erhöhe danach
die Paket-Version (z. B. auf `0.0.25`) und ergänze den CHANGELOG mit dem Hinweis,
dass diese Symbole zum öffentlichen API-Vertrag gehören und nicht ohne
Major-Version-Bump entfernt werden dürfen. Erstelle einen Draft-PR.

**`const_api.py` — Action-/Befehlskonstanten:**

```python
ACTION_PUSH = "PUSH"
ACTION_ALLAUTO = "ALLAUTO"
ACTION_ALLOFF = "ALLOFF"
ACTION_ALLON = "ALLON"
ACTION_AUTO = "AUTO"
ACTION_OFF = "OFF"
ACTION_ON = "ON"
```

**`const_devices.py` — Cover-/Geräte-Konstanten:**

```python
# High-level cover actions -> protocol command keys
COVER_FUNCTIONS: dict[str, str | None] = {
    "OPEN": "COVER_OPEN",
    "CLOSE": "COVER_CLOSE",
    "STOP": "COVER_STOP",
}

# Numeric controller COVER_STATE values -> semantic states
COVER_STATE_MAP: dict[str, str] = {
    "0": "open",
    "1": "opening",
    "2": "closed",
    "3": "closing",
}

# Per-device control parameter definitions (extensible; empty by default)
DEVICE_PARAMETERS: dict[str, dict[str, str]] = {}
```

**Abschlussprüfung:**

- `import violet_poolcontroller_api.const_api` und
  `import violet_poolcontroller_api.const_devices` laufen fehlerfrei.
- `from violet_poolcontroller_api.const_api import *` liefert die `ACTION_*`.
- `from violet_poolcontroller_api.const_devices import *` liefert
  `COVER_FUNCTIONS`, `COVER_STATE_MAP`, `DEVICE_PARAMETERS`.
- Version gebumpt, CHANGELOG aktualisiert, Draft-PR erstellt.

---

## Hinweise

- **Auf der Integrationsseite ist nichts rückgängig zu machen.** Die lokalen
  Definitionen in `const.py` stehen *nach* dem `import *`, d. h. sobald das
  API-Paket die Konstanten wieder exportiert, bleiben die (identischen) lokalen
  Werte gültig. Die Integration bleibt dadurch robust gegen ein erneutes
  Entfernen.
- Den vollständigen Vertrag (Klassen wie `VioletPoolAPI`, `VioletPoolAPIError`,
  `InputSanitizer`, `VioletState`, deren Methoden und die erforderlichen Module)
  beschreibt **`docs/API_PACKAGE_CONTRACT.md`**. Diese Datei kann der KI im
  API-Repo als Referenz mitgegeben werden.
