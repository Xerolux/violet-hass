"""Config flow for Violet Pool Controller."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, CONF_TIMEOUT
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import ConfigEntryNotReady

from .api import VioletPoolAPI, VioletPoolAPIError
from .const import (
    DOMAIN,
    CONF_API_URL,
    CONF_USE_SSL,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_CONTROLLER_NAME,
    CONF_POOL_VOLUME,
    CONF_POLLING_INTERVAL,
    CONF_RETRY_ATTEMPTS,
    CONF_TIMEOUT_DURATION,
    CONF_ACTIVE_FEATURES,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_POOL_VOLUME,
    DEFAULT_POLLING_INTERVAL,
    AVAILABLE_FEATURES,
    AVAILABLE_SENSORS,
    DEVICE_MODEL_NAME,
    DEVICE_MANUFACTURER,
    ERROR_INVALID_AUTH,
    ERROR_CANNOT_CONNECT,
    ERROR_UNKNOWN,
)
from .device import async_setup_device
from .error_codes import async_get_error_message

_LOGGER = logging.getLogger(__name__)


# =============================================================================
# SCHEMA DEFINITIONS
# =============================================================================

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_USERNAME, default=""): str,
        vol.Optional(CONF_PASSWORD, default=""): str,
        vol.Optional(CONF_USE_SSL, default=False): bool,
        vol.Optional(CONF_TIMEOUT_DURATION, default=DEFAULT_TIMEOUT_DURATION): vol.All(
            vol.Coerce(int), vol.Range(min=5, max=60)
        ),
        vol.Optional(CONF_RETRY_ATTEMPTS, default=DEFAULT_RETRY_ATTEMPTS): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=10)
        ),
        vol.Optional(CONF_POOL_VOLUME, default=DEFAULT_POOL_VOLUME): vol.All(
            vol.Coerce(float), vol.Range(min=0.1, max=1000.0)
        ),
        vol.Optional(
            CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL
        ): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
    }
)


# =============================================================================
# CONFIG FLOW
# =============================================================================


class VioletPoolControllerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Violet Pool Controller."""

    VERSION = 1

    def __init__(self):
        """Initialisiere den Flow."""
        self.config_data: dict[str, Any] = {}
        self._sensor_data: dict[str, Any] = {}  # Wird im Sensor-Schritt gesetzt

    # --------------------------------------------------------------------------
    # Step 1: User Input (Connection Details)
    # --------------------------------------------------------------------------

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            username = user_input.get(CONF_USERNAME, "")
            password = user_input.get(CONF_PASSWORD, "")
            use_ssl = user_input.get(CONF_USE_SSL, False)
            timeout = user_input.get(CONF_TIMEOUT_DURATION)
            retries = user_input.get(CONF_RETRY_ATTEMPTS)

            self.config_data = {**user_input}
            self.config_data[CONF_API_URL] = f"{'https' if use_ssl else 'http'}://{host}"

            # Prüfe Verbindung zur API
            try:
                await self._async_test_connection(
                    host=host,
                    username=username,
                    password=password,
                    use_ssl=use_ssl,
                    timeout=timeout,
                    retries=retries,
                )
            except VioletPoolAPIError as e:
                _LOGGER.warning("Connection failed: %s", e)
                if e.error_code == "invalid_auth":
                    errors["base"] = ERROR_INVALID_AUTH
                elif e.error_code == "cannot_connect":
                    errors["base"] = ERROR_CANNOT_CONNECT
                else:
                    errors["base"] = ERROR_UNKNOWN
            except Exception as e:  # Fange unerwartete Fehler ab
                _LOGGER.exception("Unexpected error during connection test: %s", e)
                errors["base"] = ERROR_UNKNOWN

            if not errors:
                # Verbindung erfolgreich, gehe zum nächsten Schritt (Features)
                return await self.async_step_features()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    # --------------------------------------------------------------------------
    # Step 2: Feature Selection
    # --------------------------------------------------------------------------

    async def async_step_features(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Schritt zur Auswahl der aktiven Features (Switches, Climate, Cover)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Filtere die "enable_"-Felder, um CONF_ACTIVE_FEATURES zu erstellen
            active_features = [
                feature_id
                for key, enabled in user_input.items()
                if key.startswith("enable_") and enabled
                for feature_id in [key[7:]]  # Entferne "enable_" Präfix
            ]

            self.config_data[CONF_ACTIVE_FEATURES] = active_features

            # Gehe zum nächsten Schritt (Sensoren)
            return await self.async_step_sensors()

        # Zeige das Formular für die Feature-Auswahl
        return self.async_show_form(
            step_id="features", data_schema=self._get_feature_selection_schema()
        )

    # --------------------------------------------------------------------------
    # Step 3: Sensor Selection
    # --------------------------------------------------------------------------

    async def async_step_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Schritt zur Auswahl der anzuzeigenden Sensoren."""
        errors: dict[str, str] = {}

        if not self._sensor_data:
            # Rufe verfügbare Sensoren und deren aktuelle Werte ab
            try:
                self._sensor_data = await self._async_get_sensor_data()
            except VioletPoolAPIError as e:
                errors["base"] = async_get_error_message(e.error_code)
                # Bei API-Fehler zurück zu Schritt 1 (vermutlich Auth-Problem)
                return self.async_show_form(
                    step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
                )
            except Exception:
                errors["base"] = ERROR_UNKNOWN
                return self.async_show_form(
                    step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
                )

        if user_input is not None:
            # user_input enthält die ausgewählten Sensor-Keys in Gruppen
            selected_sensors = []
            for group, keys in user_input.items():
                selected_sensors.extend(keys)

            # Die finale Liste aller Sensor-Keys in die Konfiguration speichern
            self.config_data["selected_sensors"] = selected_sensors

            # Gehe zum Abschluss-Schritt
            return self.async_step_finish()

        # Zeige das Formular für die Sensor-Auswahl
        return self.async_show_form(
            step_id="sensors", data_schema=self._get_sensor_selection_schema()
        )

    # --------------------------------------------------------------------------
    # Step 4: Finish (Final Details & Create Entry)
    # --------------------------------------------------------------------------

    async def async_step_finish(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Schritt zur Eingabe des finalen Gerätenamens und Fertigstellung."""
        
        # Generiere einen standardisierten Gerätenamen
        default_name = (
            f"{DEVICE_MODEL_NAME} {self.config_data.get(CONF_DEVICE_ID, '1')}"
        )
        
        finish_schema = vol.Schema(
            {
                # Der CONF_CONTROLLER_NAME wird für die UI-Anzeige verwendet
                vol.Required(
                    CONF_CONTROLLER_NAME, default=default_name
                ): str,
                # Setze den tatsächlichen, unveränderlichen Gerätenamen (z.B. für Logs)
                vol.Optional(
                    CONF_DEVICE_NAME, default=default_name
                ): str,
            }
        )

        if user_input is not None:
            # Füge die finalen Namen zur Konfiguration hinzu
            self.config_data.update(user_input)

            # Markiere den Controller als eindeutig
            await self.async_set_unique_id(
                f"{self.config_data[CONF_HOST]}_{self.config_data.get(CONF_DEVICE_ID, 1)}"
            )
            self._abort_if_unique_id_configured()

            # Erstelle den Config Entry
            return self.async_create_entry(
                title=self.config_data[CONF_CONTROLLER_NAME], data=self.config_data
            )

        return self.async_show_form(step_id="finish", data_schema=finish_schema)

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    def _get_feature_selection_schema(self) -> vol.Schema:
        """Erstellt das Schema für die Feature-Auswahl. (FEHLERBEHOBENE VERSION)"""
        feature_schema = {}
        
        # FIX: Ersetzt fehlerhafte Dictionary Comprehension durch eine explizite Zuweisungsschleife.
        # Dies stellt sicher, dass Voluptuous die dynamischen Keys korrekt registriert,
        # was den Fehler "extra keys not allowed" behebt.
        for f in AVAILABLE_FEATURES:
            key_name = f"enable_{f['id']}"
            default_value = f.get("default", False)
            
            # Die korrekte Voluptuous-Syntax: vol.Optional wird als Key verwendet.
            feature_schema[vol.Optional(key_name, default=default_value)] = bool

        return vol.Schema(feature_schema)

    def _get_sensor_selection_schema(self) -> vol.Schema:
        """Erstellt das Schema für die Sensor-Auswahl. (FEHLERBEHOBENE VERSION)"""
        schema = {}
        for group, sensors in self._sensor_data.items():
            # Verwende den Gruppennamen als Key und Label
            
            # FIX: Entfernt vol.All(...) und vereinfacht zu [vol.In(...)].
            # Dies behebt den Fehler "ValueError: Unable to convert schema: <class 'list'>",
            # da es die einfachste Form zur Definition eines Multi-Select-List-Schemas ist, 
            # die Voluptuous-Serialize in Home Assistant korrekt verarbeiten kann.
            schema[vol.Optional(group, default=sensors)] = [vol.In(sensors)]
        
        return vol.Schema(schema)

    async def _async_get_sensor_data(self) -> dict[str, list[str]]:
        """Ruft die verfügbaren Sensor-Keys vom Controller ab (simuliert)."""
        _LOGGER.debug("Simuliere Abruf der verfügbaren Sensor-Keys...")
        
        # Simuliere API-Aufruf
        # In der echten Implementierung müsste hier api.get_available_sensors() stehen.
        # Für den Konfigurations-Flow werden alle bekannten Sensoren als verfügbar angenommen.
        
        # Grouping basierend auf const_sensors.py (angenommene Struktur)
        sensor_data: dict[str, list[str]] = {}
        
        for group, sensors in AVAILABLE_SENSORS.items():
            sensor_data[group] = [s["key"] for s in sensors]
            
        return sensor_data


    async def _async_test_connection(
        self, host: str, username: str, password: str, use_ssl: bool, timeout: int, retries: int
    ) -> None:
        """Teste die Verbindung zur API und rufe Gerätedetails ab."""
        
        # Wir benötigen hier nur eine minimale API-Instanz zum Testen
        test_api = VioletPoolAPI(
            host=host,
            session=self.hass.helpers.aiohttp_client.async_get_clientsession(self.hass),
            username=username,
            password=password,
            use_ssl=use_ssl,
            timeout=timeout,
            max_retries=retries
        )

        try:
            # Rufe eine einfache, authentifizierte Endpunkt-Antwort ab, um Auth/Verbindung zu prüfen
            device_info = await test_api.get_device_info()
            
            # Speichere die im Test ermittelten Daten für den Konfigurations-Entry
            self.config_data[CONF_DEVICE_ID] = device_info.get("device_id", 1)
            self.config_data[CONF_DEVICE_NAME] = device_info.get("device_name", "Violet Pool Controller")

            # Überprüfe die Eindeutigkeit der ID (HOST + DEVICE_ID)
            unique_id = f"{host}_{self.config_data[CONF_DEVICE_ID]}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            
            _LOGGER.info(
                "Verbindung erfolgreich. Gefundene Geräte-ID: %s, Name: %s",
                self.config_data[CONF_DEVICE_ID],
                self.config_data[CONF_DEVICE_NAME]
            )

        except VioletPoolAPIError as e:
            _LOGGER.error("API-Test fehlgeschlagen: %s", e)
            raise
        except Exception as e:
            _LOGGER.exception("Unerwarteter Fehler während des Verbindungstests")
            raise VioletPoolAPIError(
                f"Unerwarteter Fehler: {e}", "unexpected_error"
            )

    # =============================================================================
    # OPTIONS FLOW
    # =============================================================================

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Erstelle den Options-Flow."""
        return VioletPoolControllerOptionsFlow(config_entry)


class VioletPoolControllerOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Violet Pool Controller."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialisiere den Options-Flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)
        self.config = dict(config_entry.data)
        self._sensor_data: dict[str, Any] = {}

    # --------------------------------------------------------------------------
    # Step 1: Options (Polling, Timeout, Retries)
    # --------------------------------------------------------------------------

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial options step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.options.update(user_input)
            
            # Gehe zum nächsten Schritt (Feature-Auswahl)
            return await self.async_step_options_features()

        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_POLLING_INTERVAL,
                    default=self.options.get(
                        CONF_POLLING_INTERVAL,
                        self.config.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL),
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
                vol.Optional(
                    CONF_TIMEOUT_DURATION,
                    default=self.options.get(
                        CONF_TIMEOUT_DURATION,
                        self.config.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION),
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=60)),
                vol.Optional(
                    CONF_RETRY_ATTEMPTS,
                    default=self.options.get(
                        CONF_RETRY_ATTEMPTS,
                        self.config.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS),
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
            }
        )
        
        # Zeige das Options-Formular
        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )

    # --------------------------------------------------------------------------
    # Step 2: Options Feature Selection
    # --------------------------------------------------------------------------

    async def async_step_options_features(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Options-Schritt zur Auswahl der Features."""
        
        if user_input is not None:
            active_features = [
                feature_id
                for key, enabled in user_input.items()
                if key.startswith("enable_") and enabled
                for feature_id in [key[7:]]
            ]

            self.options[CONF_ACTIVE_FEATURES] = active_features
            
            # Gehe zum nächsten Schritt (Sensor-Auswahl)
            return await self.async_step_options_sensors()

        # Erstelle das Feature-Schema basierend auf aktuellen Optionen/Daten
        current_active_features = self.options.get(
            CONF_ACTIVE_FEATURES, self.config.get(CONF_ACTIVE_FEATURES, [])
        )
        
        options_schema = self._get_options_feature_selection_schema(current_active_features)

        return self.async_show_form(
            step_id="options_features", data_schema=options_schema
        )

    # --------------------------------------------------------------------------
    # Step 3: Options Sensor Selection
    # --------------------------------------------------------------------------

    async def async_step_options_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Options-Schritt zur Auswahl der Sensoren."""

        if not self._sensor_data:
            # Wiederverwendung der Funktion zur Ermittlung der Sensordaten
            flow = VioletPoolControllerConfigFlow()
            self._sensor_data = await flow._async_get_sensor_data()

        if user_input is not None:
            selected_sensors = []
            for group, keys in user_input.items():
                selected_sensors.extend(keys)

            self.options["selected_sensors"] = selected_sensors
            
            # Options-Entry erstellen und beenden
            return self.async_create_entry(title="", data=self.options)

        # Hole aktuelle Sensor-Auswahl für die Defaults
        current_selected_sensors = self.options.get(
            "selected_sensors", self.config.get("selected_sensors", [])
        )
        
        options_schema = self._get_options_sensor_selection_schema(current_selected_sensors)

        return self.async_show_form(
            step_id="options_sensors", data_schema=options_schema
        )

    # --------------------------------------------------------------------------
    # Options Helpers
    # --------------------------------------------------------------------------
    
    def _get_options_feature_selection_schema(self, current_active_features: list[str]) -> vol.Schema:
        """Erstellt das Schema für die Feature-Auswahl (Options-Flow)."""
        feature_schema = {}
        for f in AVAILABLE_FEATURES:
            key_name = f"enable_{f['id']}"
            is_active = f['id'] in current_active_features
            # Verwende die im Config-Entry oder Options-Flow gespeicherten Werte als Default
            feature_schema[vol.Optional(key_name, default=is_active)] = bool

        return vol.Schema(feature_schema)

    def _get_options_sensor_selection_schema(self, current_selected_sensors: list[str]) -> vol.Schema:
        """Erstellt das Schema für die Sensor-Auswahl (Options-Flow)."""
        schema = {}
        
        # Gehe die Gruppen durch, um Defaults zu setzen
        for group, available_sensors in self._sensor_data.items():
            # Filtert die Liste der verfügbaren Sensoren, um nur die aktuell
            # ausgewählten als Standard zu markieren (zur Vereinfachung).
            default_selection = [
                key for key in available_sensors if key in current_selected_sensors
            ]
            
            # Wenn keine Sensoren vorausgewählt sind, wähle alle verfügbaren
            if not default_selection:
                 default_selection = available_sensors

            # Verwende die korrigierte Schema-Definition
            schema[vol.Optional(group, default=default_selection)] = [vol.In(available_sensors)]
        
        return vol.Schema(schema)

# EOF