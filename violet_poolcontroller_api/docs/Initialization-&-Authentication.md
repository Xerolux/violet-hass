> [🇬🇧 English](Initialization-&-Authentication) | [🇩🇪 Deutsch](de/Initialization-&-Authentication) &nbsp;|&nbsp; [🏠](Home)

# Initialization & Authentication

To start, you need an `aiohttp.ClientSession` and your controller's credentials.

```python
import asyncio
import aiohttp
from violet_poolcontroller_api.api import VioletPoolAPI, VioletPoolAPIError

async def main():
    async with aiohttp.ClientSession() as session:
        api = VioletPoolAPI(
            host="192.168.1.100",
            username="admin",        # Optional, depending on controller settings
            password="your_password",# Optional
            session=session,
            use_ssl=False,           # Set to True if you use HTTPS
            verify_ssl=True,
            timeout=10,              # Request timeout in seconds
            max_retries=3,
            dosing_standalone=False  # Set to True for dosing-only standalone setups
        )

        # Now you can call api methods...
```
