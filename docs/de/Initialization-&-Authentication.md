> [🇬🇧 English](../Initialization-&-Authentication) | [🇩🇪 Deutsch](Initialization-&-Authentication) &nbsp;|&nbsp; [🏠](Home)

# Initialisierung & Authentifizierung

Zunächst benötigst du eine `aiohttp.ClientSession` und die Zugangsdaten deines Controllers.

```python
import asyncio
import aiohttp
from violet_poolcontroller_api.api import VioletPoolAPI, VioletPoolAPIError

async def main():
    async with aiohttp.ClientSession() as session:
        api = VioletPoolAPI(
            host="192.168.1.100",
            username="admin",        # Optional, abhaengig von den Controller-Einstellungen
            password="your_password",# Optional
            session=session,
            use_ssl=False,           # Auf True setzen, wenn HTTPS verwendet wird
            verify_ssl=True,
            timeout=10,              # Anfrage-Timeout in Sekunden
            max_retries=3,
            dosing_standalone=False  # Auf True setzen fuer Dosier-Standalone-Konfigurationen
        )

        # Jetzt koennen API-Methoden aufgerufen werden...
```
