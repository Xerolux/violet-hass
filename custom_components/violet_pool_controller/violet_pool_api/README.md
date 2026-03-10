# Violet Pool API

An asynchronous Python client for interacting with the **Violet Pool Controller**.

This library is primarily designed to power the official [Violet Pool Controller Home Assistant Integration](https://github.com/Xerolux/violet-hass), but it can be used independently for any Python project that needs to fetch readings or control a Violet Pool system.

## Features
* **Asynchronous:** Fully async operations using `aiohttp`.
* **Resilient:** Built-in Circuit Breaker and Rate Limiter to protect both the client and the controller from overload.
* **Sanitization:** Strict payload input sanitization to prevent injection and invalid settings.

## Installation

```bash
pip install violet-pool-api
```

## Basic Usage

```python
import asyncio
from violet_pool_api.api import VioletPoolAPI

async def main():
    # Initialize the API
    api = VioletPoolAPI(
        host="192.168.1.100",
        username="admin",
        password="your_password"
    )

    try:
        # Fetch current sensor readings
        readings = await api.get_readings()
        print(readings)
    finally:
        await api.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## License
MIT License
