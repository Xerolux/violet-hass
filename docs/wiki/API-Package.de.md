# Python-API-Paket (`violet-poolController-api`)

**[🇬🇧 English](API-Package)**

[![PyPI](https://img.shields.io/pypi/v/violet-poolController-api?logo=pypi)](https://pypi.org/project/violet-poolController-api/)

Der HTTP-Client der Home-Assistant-Integration wird im
[violet-hass-Monorepo](https://github.com/Xerolux/violet-hass) unter
`violet_poolcontroller_api/` entwickelt und als
[`violet-poolController-api`](https://pypi.org/project/violet-poolController-api/) auf PyPI
veröffentlicht. Er hat **keine Home-Assistant-Abhängigkeiten** und ist in jedem
Python-Projekt nutzbar.

---

## Installation

```bash
pip install violet-poolController-api
```

Benötigt Python **3.12+** und `aiohttp`.

## Schnellstart

```python
import asyncio
import aiohttp
from violet_poolcontroller_api.api import VioletPoolAPI

async def main():
    async with aiohttp.ClientSession() as session:
        api = VioletPoolAPI(
            host="192.168.1.50",
            session=session,
            username="user",
            password="geheim",
        )

        # Alle ~400 Werte lesen
        readings = await api.get_readings()
        print(readings["pH_value"], readings["orp_value"])

        # Ausgänge schalten (Pumpe, Heizung, Solar, ...)
        await api.set_switch_state("PUMP", "ON", duration=3600, last_value=2)

        # Manuelle Dosierung (Laufzeit in Sekunden, via POST /triggerManualDosing)
        await api.manual_dosing("Chlor", 60)
        await api.set_switch_state("DOS_1_CL", "OFF")   # Stopp -> zurück auf Auto

        # Dosierkanal dauerhaft aktivieren/deaktivieren (Controller-Config)
        await api.set_dosage_enabled("Flockmittel", True)

asyncio.run(main())
```

## Funktionen

| Funktion | Beschreibung |
|----------|--------------|
| **Rate Limiting** | Token-Bucket-Limiter schützt den Controller vor Überlastung |
| **Circuit Breaker** | Verhindert Dauerfeuer auf nicht erreichbare Controller; 4xx-Fehler schlagen sofort fehl |
| **Retry & Backoff** | Automatische Wiederholungen bei transienten Netzwerk-/Serverfehlern |
| **Input-Sanitization** | `InputSanitizer` schützt alle Parameter vor Injection |
| **SSL/TLS** | Zertifikatsprüfung standardmäßig aktiv, Self-Signed unterstützt |
| **Standalone-Dosing** | `dosing_standalone=True` für Dosiermodule ohne Basismodul |
| **State-Konstanten** | `VioletState`, `DEVICE_STATE_MAPPING` (States 0–6), Übersetzungen |

## Dosierung: Wichtiges Verhalten

- Dosierausgänge (`DOS_*`) lassen sich **nicht** über `/setFunctionManually` schalten —
  der Controller akzeptiert nur `POST /triggerManualDosing` (von PoolDigital bestätigt).
  Der Client routet das automatisch.
- Eine manuelle Dosierung **braucht eine Laufzeit**; Stoppen (`OFF`/`AUTO`) bringt den
  Kanal zurück in den Automatikmodus.
- Flockung (`DOS_6_FLOC`) hat keinen Auto-Modus — sie wird über das Config-Flag
  `DOSAGE_floc_use` aktiviert/deaktiviert (`set_dosage_enabled("Flockmittel", ...)`).

## Versionierung & Releases

- Single Source of Truth: `violet_poolcontroller_api/pyproject.toml` im Monorepo
- Ein Git-Tag `api-v<version>` löst den automatischen PyPI-Upload + GitHub-Release aus
- Die HA-Integration pinnt ihre Mindestversion in `manifest.json`
  (wird vom Workflow *Sync API Version* automatisch synchron gehalten)

## Links

- 📦 [PyPI](https://pypi.org/project/violet-poolController-api/)
- 📚 [Vollständige API-Referenz](https://github.com/Xerolux/violet-hass/blob/main/violet_poolcontroller_api/docs/API_REFERENCE.md)
- 📝 [Changelog](https://github.com/Xerolux/violet-hass/blob/main/violet_poolcontroller_api/CHANGELOG.md)
- 🧪 [Test-Suite](https://github.com/Xerolux/violet-hass/tree/main/violet_poolcontroller_api/tests)

Siehe auch: [API-Referenz (HTTP-Endpoints)](API-Reference.de)
