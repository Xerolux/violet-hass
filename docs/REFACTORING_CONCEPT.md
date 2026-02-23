# Refactoring Konzept - Große Dateien aufteilen

**Datum:** 2026-02-23
**Status:** Nice-to-Have (Nicht kritisch)
**Priorität:** Niedrig
**Aufwand:** 2-3 Stunden

---

## 📊 Ausgangslage

### Problem-Dateien

| Datei | Zeilen | Problem | Ziel |
|-------|--------|---------|------|
| `config_flow.py` | 1315 | Zu groß, schwer zu warten | ~400-500 Zeilen |
| `sensor.py` | 1102 | Zu viele Sensoren in einer Datei | ~300-400 Zeilen |

---

## 🎯 Zielsetzung

### Wartbarkeit verbessern
- ✅ Bessere Übersicht
- ✅ Schnellere Bugfixes
- ✅ Einfachere Erweiterungen
- ✅ Weniger Merge Conflicts

### Performance
- ✅ Kürzere Import-Zeiten
- ✅ Bessere Test-Isolation
- ✅ Modulares Laden

---

## Teil 1: config_flow.py Refactoring

### Aktueller Aufbau (1315 Zeilen)

```python
class ConfigFlow(ConfigEntry):
    # ~100 Zeilen: Imports und Konstanten
    # ~200 Zeilen: Validierungsfunktionen
    # ~150 Zeilen: Sensor-Helper-Funktionen
    # ~50 Zeilen: Menu/Help
    # ~150 Zeilen: Disclaimer Step
    # ~200 Zeilen: Connection Step
    # ~200 Zeilen: Pool/Disinfection Step
    # ~100 Zeilen: Sensor Selection Step
    # ~100 Zeilen: Options Flow
    # ~63 Zeilen: Haupt-Klasse
```

### Neuer Aufbau (~500 Zeilen)

```
custom_components/violet_pool_controller/
├── config_flow.py                    # ~450 Zeilen (Main Flow)
├── config_flow/
│   ├── __init__.py                   # Export
│   ├── validators.py                 # ~180 Zeilen
│   ├── sensor_helper.py              # ~200 Zeilen
│   ├── api_handler.py                # ~120 Zeilen
│   └── constants.py                  # ~100 Zeilen
```

---

## 📝 Detail: config_flow/ Module

### 1. constants.py (~100 Zeilen)

**Was Ausgelagert wird:**
- Alle Konstanten
- Enums
- Mappings
- Error Messages

**Vorher (config_flow.py):**
```python
# Lines 54-114
MIN_POLLING_INTERVAL = 10
MAX_POLLING_INTERVAL = 3600
MIN_TIMEOUT = 1
MAX_TIMEOUT = 60
# ... 50+ Konstanten
```

**Nachher (constants.py):**
```python
"""Config Flow Constants."""

from enum import Enum
from typing import Final

# Validation Limits
MIN_POLLING_INTERVAL: Final = 10
MAX_POLLING_INTERVAL: Final = 3600
MIN_TIMEOUT: Final = 1
MAX_TIMEOUT: Final = 60
MIN_RETRIES: Final = 1
MAX_RETRIES: Final = 10
MIN_POOL_SIZE: Final = 0.1
MAX_POOL_SIZE: Final = 1000.0

# Retry Constants
BASE_RETRY_DELAY: Final = 2
DEFAULT_API_TIMEOUT: Final = 10

# Error Messages
ERROR_ALREADY_CONFIGURED: Final = "already_configured"
ERROR_INVALID_IP: Final = "invalid_ip_address"
ERROR_CANNOT_CONNECT: Final = "cannot_connect"
ERROR_AGREEMENT_DECLINED: Final = "agreement_declined"

# Pool & Disinfection Options
POOL_TYPE_OPTIONS = {
    "outdoor": "🏖️ Freibad",
    "indoor": "🏠 Hallenbad",
    # ...
}

DISINFECTION_OPTIONS = {
    "chlorine": "🧪 Chlor (Flüssig/Tabletten)",
    # ...
}

# Enhanced Features
ENHANCED_FEATURES = {
    "heating": {"icon": "🔥", "name": "Heizungssteuerung"},
    # ...
}

# URLs
GITHUB_BASE_URL: Final = "https://github.com/xerolux/violet-hass"
HELP_DOC_DE_URL: Final = f"{GITHUB_BASE_URL}/blob/main/docs/help/configuration-guide.de.md"
HELP_DOC_EN_URL: Final = f"{GITHUB_BASE_URL}/blob/main/docs/help/configuration-guide.en.md"
SUPPORT_URL: Final = f"{GITHUB_BASE_URL}/issues"

# Menu Actions
MENU_ACTION_START: Final = "start_setup"
MENU_ACTION_HELP: Final = "open_help"
```

---

### 2. validators.py (~180 Zeilen)

**Was Ausgelagert wird:**
- IP-Validierung
- Credential-Strength-Check
- Sensor-Label-Helper
- Duplicate-Check

**Neue Datei:**
```python
"""Config Flow Validators."""

import ipaddress
import re
import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)

# Pre-compiled numeric pattern for performance
NUMERIC_PATTERN = re.compile(r"^-?\d+$")


def validate_ip_address(ip: str) -> bool:
    """
    Validate IP address or hostname.

    Args:
        ip: The IP address or hostname to validate.

    Returns:
        True if valid, False otherwise.
    """
    if not ip:
        return False

    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        # Allow hostnames (letters, numbers, dots, dashes)
        return bool(re.match(r"^[a-zA-Z0-9\-\.]+$", ip))


def validate_credentials_strength(username: str | None, password: str | None) -> None:
    """
    Check credentials against basic security policies.

    Args:
        username: The username.
        password: The password.

    Note:
        This is a basic check. For production, implement proper password validation.
    """
    if not password and username:
        # It's okay to have no auth, but if username is present, password should be checked
        pass


def get_sensor_label(key: str, all_sensors: dict) -> str:
    """
    Get the friendly name for a sensor key.

    Args:
        key: The sensor key.
        all_sensors: Dictionary of all sensors.

    Returns:
        The friendly name with key.
    """
    if key in all_sensors:
        return f"{all_sensors[key]['name']} ({key})"
    return key


def validate_pool_size(size: float) -> bool:
    """
    Validate pool size.

    Args:
        size: The pool size in cubic meters.

    Returns:
        True if valid, False otherwise.
    """
    from .constants import MIN_POOL_SIZE, MAX_POOL_SIZE
    return MIN_POOL_SIZE <= size <= MAX_POOL_SIZE


def validate_timeout(timeout: int) -> bool:
    """
    Validate timeout duration.

    Args:
        timeout: Timeout in seconds.

    Returns:
        True if valid, False otherwise.
    """
    from .constants import MIN_TIMEOUT, MAX_TIMEOUT
    return MIN_TIMEOUT <= timeout <= MAX_TIMEOUT
```

---

### 3. sensor_helper.py (~200 Zeilen)

**Was Ausgelagert wird:**
- `get_grouped_sensors()`
- `fetch_available_sensors()`
- JSON-Parsing für Sensor-Daten
- Sensor-Gruppierungs-Logik

**Neue Datei:**
```python
"""Config Flow Sensor Helper."""

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

from .api import VioletPoolAPI
from .constants import (
    CONF_API_URL,
    CONF_PASSWORD,
    CONF_TIMEOUT_DURATION,
    CONF_USE_SSL,
    CONF_USERNAME,
    DEFAULT_API_TIMEOUT,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_VERIFY_SSL,
)

_LOGGER = logging.getLogger(__name__)


async def fetch_available_sensors(
    hass: HomeAssistant,
    config_data: dict[str, Any],
) -> dict[str, list[str]]:
    """
    Fetch available sensors from the controller.

    Args:
        hass: The Home Assistant instance.
        config_data: The configuration data.

    Returns:
        A dictionary mapping groups to lists of sensor keys.

    Raises:
        VioletPoolAPIError: If API call fails.
    """
    try:
        username = config_data.get(CONF_USERNAME)
        password = config_data.get(CONF_PASSWORD)

        # Import validators
        from .validators import validate_credentials_strength
        validate_credentials_strength(username, password)

        api = VioletPoolAPI(
            host=config_data[CONF_API_URL],
            session=aiohttp_client.async_get_clientsession(hass),
            username=username,
            password=password,
            use_ssl=config_data.get(CONF_USE_SSL, False),
            verify_ssl=True,
            timeout=config_data.get(
                CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION
            ),
        )

        # Fetch data
        data = await api.async_get_readings(["ALL_SENSORS"])

        # Group sensors
        return _group_sensors_by_type(data)

    except Exception as err:
        _LOGGER.error("Failed to fetch sensors: %s", err)
        raise


def _group_sensors_by_type(data: dict[str, Any]) -> dict[str, list[str]]:
    """
    Group sensors by type.

    Args:
        data: The raw sensor data from API.

    Returns:
        A dictionary mapping types to sensor lists.
    """
    from .const_sensors import (
        ANALOG_SENSORS,
        STATUS_SENSORS,
        SYSTEM_SENSORS,
        TEMP_SENSORS,
        WATER_CHEM_SENSORS,
    )

    grouped = {
        "temperature": [],
        "water_chemistry": [],
        "analog": [],
        "system": [],
        "status": [],
    }

    # Group sensors based on presence in data
    all_sensor_defs = {
        **TEMP_SENSORS,
        **WATER_CHEM_SENSORS,
        **ANALOG_SENSORS,
        **SYSTEM_SENSORS,
        **STATUS_SENSORS,
    }

    for key, definition in all_sensor_defs.items():
        if key in data:
            sensor_type = definition.get("type", "system")
            if sensor_type in grouped:
                grouped[sensor_type].append(key)

    return grouped


def get_sensor_count_summary(grouped_sensors: dict[str, list[str]]) -> str:
    """
    Get a human-readable summary of available sensors.

    Args:
        grouped_sensors: The grouped sensor dictionary.

    Returns:
        A summary string.
    """
    total = sum(len(sensors) for sensors in grouped_sensors.values())
    return f"{total} sensors in {len(grouped_sensors)} categories"


def parse_sensor_selection(
    selected_sensors: list[str],
    all_sensors: dict[str, Any],
) -> list[str]:
    """
    Parse and validate sensor selection.

    Args:
        selected_sensors: List of selected sensor keys.
        all_sensors: Dictionary of all available sensors.

    Returns:
        Validated list of sensor keys.
    """
    # Validate all selected sensors exist
    validated = []
    for sensor in selected_sensors:
        if sensor in all_sensors:
            validated.append(sensor)
        else:
            _LOGGER.warning("Selected sensor %s not found in available sensors", sensor)

    return validated
```

---

### 4. api_handler.py (~120 Zeilen)

**Was Ausgelagert wird:**
- API-Aufrufe für Config Flow
- Verbindungs-Tests
- Retry-Logik

**Neue Datei:**
```python
"""Config Flow API Handler."""

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

from .api import VioletPoolAPI, VioletPoolAPIError
from .constants import (
    CONF_API_URL,
    CONF_PASSWORD,
    CONF_TIMEOUT_DURATION,
    CONF_USE_SSL,
    CONF_USERNAME,
    DEFAULT_TIMEOUT_DURATION,
)
from .validators import validate_credentials_strength

_LOGGER = logging.getLogger(__name__)


async def test_api_connection(
    hass: HomeAssistant,
    config_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Test API connection to the controller.

    Args:
        hass: The Home Assistant instance.
        config_data: The configuration data to test.

    Returns:
        Dictionary with test results:
        - success: bool
        - error: str | None
        - data: dict | None

    Raises:
        VioletPoolAPIError: If connection fails critically.
    """
    try:
        username = config_data.get(CONF_USERNAME)
        password = config_data.get(CONF_PASSWORD)

        # Validate credentials
        validate_credentials_strength(username, password)

        # Create API instance
        api = VioletPoolAPI(
            host=config_data[CONF_API_URL],
            session=aiohttp_client.async_get_clientsession(hass),
            username=username,
            password=password,
            use_ssl=config_data.get(CONF_USE_SSL, False),
            verify_ssl=True,
            timeout=config_data.get(
                CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION
            ),
        )

        # Test connection
        data = await api.async_get_readings(["SYSTEM"])

        return {
            "success": True,
            "error": None,
            "data": data,
        }

    except VioletPoolAPIError as err:
        _LOGGER.error("API connection test failed: %s", err)
        return {
            "success": False,
            "error": str(err),
            "data": None,
        }
    except Exception as err:
        _LOGGER.error("Unexpected error during API test: %s", err)
        return {
            "success": False,
            "error": f"Unexpected error: {err}",
            "data": None,
        }


async def fetch_controller_info(
    hass: HomeAssistant,
    config_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Fetch controller information.

    Args:
        hass: The Home Assistant instance.
        config_data: The configuration data.

    Returns:
        Dictionary with controller info.
    """
    api = VioletPoolAPI(
        host=config_data[CONF_API_URL],
        session=aiohttp_client.async_get_clientsession(hass),
        username=config_data.get(CONF_USERNAME),
        password=config_data.get(CONF_PASSWORD),
        use_ssl=config_data.get(CONF_USE_SSL, False),
        verify_ssl=True,
    )

    # Fetch basic system info
    data = await api.async_get_readings([
        "FW",
        "HW_VERSION",
        "SW_VERSION",
    ])

    return {
        "firmware": data.get("FW"),
        "hardware_version": data.get("HW_VERSION"),
        "software_version": data.get("SW_VERSION"),
    }
```

---

### 5. Neue config_flow.py (~450 Zeilen)

**Jetzt nur noch:**
- Import Statements
- Main Flow Logic
- Steps (disclaimer, connection, options)
- UI-Definitions

**Neuer Aufbau:**
```python
"""Config Flow für Violet Pool Controller - REFACTORED VERSION."""

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector

# Import aus Unter-Modulen
from .config_flow import (
    api_handler,
    constants,
    sensor_helper,
    validators,
)
from .api import VioletPoolAPI, VioletPoolAPIError
from .const import (
    AVAILABLE_FEATURES,
    CONF_ACTIVE_FEATURES,
    # ... weitere Konstanten
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für Violet Pool Controller - REFACTORED."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialisiere Config Flow."""
        self._config_data: dict[str, Any] = {}
        self._sensor_data: dict[str, list[str]] = {}
        self._reauth_entry: config_entries.ConfigEntry | None = None
        _LOGGER.info("Violet Pool Controller Setup gestartet")

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Options Flow zurückgeben."""
        return OptionsFlowHandler()

    # ========================================================================
    # MAIN MENU
    # ========================================================================

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the user-initiated setup start step."""
        if user_input:
            action = user_input.get("action", constants.MENU_ACTION_START)
            if action == constants.MENU_ACTION_HELP:
                return await self.async_step_help()
            return await self.async_step_disclaimer()

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_main_menu_schema(),
        )

    # ========================================================================
    # DISCLAIMER STEP
    # ========================================================================

    async def async_step_disclaimer(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the disclaimer step."""
        if user_input:
            if user_input.get("agreement"):
                return await self.async_step_connection()
            else:
                return self.async_abort(reason=constants.ERROR_AGREEMENT_DECLINED)

        return self.async_show_form(
            step_id="disclaimer",
            data_schema=vol.Schema({
                vol.Required("agreement", default=False): bool
            }),
            description_placeholders={
                "disclaimer_text": self._get_disclaimer_text(),
                **self._get_help_links(),
            },
        )

    # ========================================================================
    # CONNECTION STEP
    # ========================================================================

    async def async_step_connection(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the controller connection step."""
        errors = {}

        if user_input:
            # Validierung
            if self._is_duplicate_entry(
                user_input[CONF_API_URL],
                int(user_input.get(CONF_DEVICE_ID, 1))
            ):
                errors["base"] = constants.ERROR_ALREADY_CONFIGURED
            elif not validators.validate_ip_address(user_input[CONF_API_URL]):
                errors[CONF_API_URL] = constants.ERROR_INVALID_IP
            else:
                # API Connection Test
                self._config_data = self._build_config_data(user_input)

                test_result = await api_handler.test_api_connection(
                    self.hass, self._config_data
                )

                if test_result["success"]:
                    # Sensoren abrufen
                    self._sensor_data = await sensor_helper.fetch_available_sensors(
                        self.hass, self._config_data
                    )

                    # Zum nächsten Schritt
                    return await self.async_step_pool_disinfection()
                else:
                    errors["base"] = constants.ERROR_CANNOT_CONNECT
                    _LOGGER.error("Connection test failed: %s", test_result["error"])

        # Formular anzeigen
        return self.async_show_form(
            step_id="connection",
            data_schema=self._get_connection_schema(),
            errors=errors,
        )

    # ... weitere Steps ...

    # ========================================================================
    # HELPER METHODS (nur UI-relevant)
    # ========================================================================

    def _get_main_menu_schema(self) -> vol.Schema:
        """Get the main menu schema."""
        return vol.Schema({
            vol.Required(
                "action",
                default=constants.MENU_ACTION_START
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(
                            value=constants.MENU_ACTION_START,
                            label="⚙️ Setup starten / Start setup",
                        ),
                        selector.SelectOptionDict(
                            value=constants.MENU_ACTION_HELP,
                            label="📘 Hilfe & Dokumentation / Help & docs",
                        ),
                    ]
                )
            )
        })

    def _get_connection_schema(self) -> vol.Schema:
        """Get the connection schema."""
        from .constants import (
            DEFAULT_USE_SSL,
            MIN_DEVICE_ID,
            MAX_DEVICE_ID,
        )

        return vol.Schema({
            vol.Required(CONF_API_URL, default="192.168.178.55"): str,
            vol.Optional(CONF_USERNAME): str,
            vol.Optional(CONF_PASSWORD): str,
            vol.Required(CONF_USE_SSL, default=DEFAULT_USE_SSL): bool,
            vol.Required(
                CONF_DEVICE_ID,
                default=1
            ): selector.NumberSelector(
                selector.SelectNumberSelectorConfig(
                    min=MIN_DEVICE_ID,
                    max=MAX_DEVICE_ID,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            # ... weitere Felder
        })

    def _build_config_data(self, user_input: dict[str, Any]) -> dict[str, Any]:
        """Build configuration data from user input."""
        return {
            CONF_API_URL: user_input[CONF_API_URL],
            CONF_USERNAME: user_input.get(CONF_USERNAME),
            CONF_PASSWORD: user_input.get(CONF_PASSWORD),
            CONF_USE_SSL: user_input.get(CONF_USE_SSL, False),
            CONF_DEVICE_ID: user_input.get(CONF_DEVICE_ID, 1),
            CONF_TIMEOUT_DURATION: user_input.get(
                CONF_TIMEOUT_DURATION,
                constants.DEFAULT_TIMEOUT_DURATION,
            ),
            CONF_RETRY_ATTEMPTS: user_input.get(
                CONF_RETRY_ATTEMPTS,
                constants.DEFAULT_RETRY_ATTEMPTS,
            ),
        }
```

---

## Teil 2: sensor.py Refactoring

### Aktueller Aufbau (1102 Zeilen)

```
sensor.py
├── ~100 Zeilen: Imports
├── ~50 Zeilen: Konstanten
├── ~900 Zeilen: Sensor-Klassen (verschiedene Typen)
└── ~52 Zeilen: Setup-Funktion
```

### Neuer Aufbau (~400 Zeilen)

```
custom_components/violet_pool_controller/
├── sensor.py                         # ~250 Zeilen (Main + Setup)
├── sensor/
│   ├── __init__.py                   # Export
│   ├── base.py                       # ~150 Zeilen (Base Class)
│   ├── temperature_sensors.py        # ~120 Zeilen
│   ├── chemistry_sensors.py          # ~130 Zeilen
│   ├── system_sensors.py             # ~110 Zeilen
│   ├── dosing_sensors.py             # ~140 Zeilen
│   └── runtime_sensors.py            # ~100 Zeilen
```

---

### Beispiel: base.py (~150 Zeilen)

```python
"""Base Sensor Class."""

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry

from ..entity import VioletPoolControllerEntity

_LOGGER = logging.getLogger(__name__)


class VioletPoolSensor(VioletPoolControllerEntity, SensorEntity):
    """Base class for all Violet Pool sensors."""

    def __init__(
        self,
        coordinator,
        config_entry: ConfigEntry,
        description,
        sensor_key: str,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry, description)
        self._sensor_key = sensor_key

        _LOGGER.debug(
            "Sensor initialisiert: %s (Key: %s)",
            self.entity_id,
            sensor_key,
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.get_value(self._sensor_key, None)

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        return {
            "sensor_key": self._sensor_key,
            "last_update": self.coordinator.last_update_success,
        }
```

---

### Beispiel: temperature_sensors.py (~120 Zeilen)

```python
"""Temperature Sensors."""

from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.const import UnitOfTemperature

from .base import VioletPoolSensor

TEMP_SENSORS = [
    SensorEntityDescription(
        key="aussentemperatur",
        name="Außentemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class="temperature",
    ),
    SensorEntityDescription(
        key="beckenwasser",
        name="Beckenwasser",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class="temperature",
    ),
    # ... weitere Temperatur-Sensoren
]


def setup_temperature_sensors(hass, config_entry, coordinator):
    """Setup all temperature sensors."""
    entities = []
    for description in TEMP_SENSORS:
        entities.append(
            VioletPoolSensor(
                coordinator,
                config_entry,
                description,
                description.key,
            )
        )
    return entities
```

---

## 🚀 Umsetzungs-Plan

### Schritt 1: Vorbereitung (10 Min)

```bash
# 1. Backup erstellen
git checkout -b refactor-large-files
git commit -am "Backup before refactoring"

# 2. Ordnerstruktur erstellen
mkdir -p custom_components/violet_pool_controller/config_flow
mkdir -p custom_components/violet_pool_controller/sensor

# 3. __init__.py Dateien erstellen
touch custom_components/violet_pool_controller/config_flow/__init__.py
touch custom_components/violet_pool_controller/sensor/__init__.py
```

### Schritt 2: config_flow Refactoring (90 Min)

```bash
# 2.1 Konstanten auslagern
# Ausschneiden aus config_flow.py:
# - Lines 54-114 (Konstanten)
# Einfügen in: config_flow/constants.py

# 2.2 Validators auslagern
# Ausschneiden aus config_flow.py:
# - Lines 119-136 (validate_ip, validate_credentials, get_sensor_label)
# Einfügen in: config_flow/validators.py

# 2.3 Sensor Helper auslagern
# Ausschneiden aus config_flow.py:
# - Lines 170-219 (get_grouped_sensors, etc.)
# Einfügen in: config_flow/sensor_helper.py

# 2.4 API Handler erstellen
# Verschieben aus config_flow.py:
# - API-Call Logic aus async_step_connection
# Einfügen in: config_flow/api_handler.py

# 2.5 config_flow.py aufräumen
# Imports anpassen
# Tests laufen lassen
```

### Schritt 3: sensor.py Refactoring (60 Min)

```bash
# 3.1 Base Class extrahieren
# Ausschneiden aus sensor.py:
# - Gemeinsame Sensor-Logik
# Einfügen in: sensor/base.py

# 3.2 Sensor-Typen gruppieren
# Verschieben aus sensor.py:
# - Temperatur-Sensoren → sensor/temperature_sensors.py
# - Chemie-Sensoren → sensor/chemistry_sensors.py
# - System-Sensoren → sensor/system_sensors.py
# - Dosier-Sensoren → sensor/dosing_sensors.py
# - Runtime-Sensoren → sensor/runtime_sensors.py

# 3.3 sensor.py aufräumen
# Nur noch Setup-Funktion + Imports
```

### Schritt 4: Testing (30 Min)

```bash
# 4.1 Syntax-Check
python -m py_compile custom_components/violet_pool_controller/config_flow/*.py
python -m py_compile custom_components/violet_pool_controller/sensor/*.py

# 4.2 Import-Test
python -c "from custom_components.violet_pool_controller import config_flow"

# 4.3 Docker Test
docker compose restart
# Logs prüfen auf Import-Errors

# 4.4 Integration Test
# Config Flow durchlaufen
# Sensoren prüfen
```

### Schritt 5: Finalisierung (20 Min)

```bash
# 5.1 Code Review
# Neue Dateien reviewen
# Imports optimieren

# 5.2 Dokumentation
# README.md aktualisieren
# Developer-Doku ergänzen

# 5.3 Commit
git add .
git commit -m "refactor: Split large files into modules

- Split config_flow.py (1315 → 450 lines)
- Split sensor.py (1102 → 250 lines)
- Improved maintainability and testability
- No functional changes"

# 5.4 Push
git push origin refactor-large-files
```

---

## 📊 Erwartete Ergebnisse

### Code Quality Verbesserung

| Metrik | Vorher | Nachher | Verbesserung |
|--------|--------|---------|--------------|
| config_flow.py | 1315 Zeilen | 450 Zeilen | **-66%** |
| sensor.py | 1102 Zeilen | 250 Zeilen | **-77%** |
| Dateien | 2 große | 12 kleine | **+6x modularer** |
| Wartbarkeit | 😓 Schwer | 😊 Leicht | **+++** |
| Testbarkeit | 😓 Schwer | 😊 Leicht | **+++** |

### Vorteile

✅ **Bessere Übersicht:** Jede Datei hat einen klaren Zweck
✅ **Schnellere Bugfixes:** Man findet den Code schneller
✅ **Einfachere Tests:** Module können einzeln getestet werden
✅ **Weniger Conflicts:** Mehrere Developer können an verschiedenen Modulen arbeiten
✅ **Bessere Performance:** Kürzere Import-Zeiten

### Nachteile

⚠️ **Initialer Aufwand:** 2-3 Stunden Refactoring
⚠️ **Lernkurve:** Neues Projekt-Layout kennenlernen
⚠️ **Risiko:** Bei Fehlern können Import-Statements brechen

---

## 💡 Best Practices

### Wann aufteilen?

**Ja, wenn:**
- Datei > 800 Zeilen
- Mehrere Verantwortlichkeiten
- Schwer zu verstehen
- Häufige Merge Conflicts

**Nein, wenn:**
- Datei < 500 Zeilen
- Kohärente Funktionalität
- Gut verständlich
- Funktioniert problemlos

### Aufteilungs-Strategie

1. **Nach Verantwortlichkeit:** Validierung, API, UI, etc.
2. **Nach Typ:** Temperaturen, Chemie, System, etc.
3. **Nach Abhängigkeit:** Base Classes, Helper, Implementierungen

---

## 🔧 Zusammenfassung

Dieses Konzept zeigt, wie du die großen Dateien aufteilen kannst, **ohne die Funktionalität zu ändern**. Es ist ein rein strukturelles Refactoring zur Verbesserung der Wartbarkeit.

**Empfehlung:** Führe das Refactoring in einem separaten Branch durch und teste gründlich, bevor du mergest.

---

*Erstellt: 2026-02-23*
*Status: Konzept Ready for Implementation*
