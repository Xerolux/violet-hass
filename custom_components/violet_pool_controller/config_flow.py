"""Config Flow for Violet Pool Controller integration."""
import logging
import re
import asyncio
import ipaddress
from typing import Dict, Optional, Union, Any, List

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.typing import ConfigType
from homeassistant.core import HomeAssistant

# WICHTIG: Passe diese Importe an dein eigenes Projekt an:
from .const import (
    DOMAIN,
    API_READINGS,
    CONF_API_URL,
    CONF_USE_SSL,
    CONF_DEVICE_NAME,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_DEVICE_ID,
    CONF_POLLING_INTERVAL,
    CONF_TIMEOUT_DURATION,
    CONF_RETRY_ATTEMPTS,
    CONF_ACTIVE_FEATURES,
    DEFAULT_USE_SSL,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_RETRY_ATTEMPTS,
)

_LOGGER = logging.getLogger(__name__)

# Neue Keys für Pool-Features und -Einstellungen
CONF_POOL_SIZE = "pool_size"  # in m³
CONF_POOL_TYPE = "pool_type"
CONF_DISINFECTION_METHOD = "disinfection_method"

# Standardwerte für neue Konfigurationen
DEFAULT_POOL_SIZE = 50  # m³
DEFAULT_POOL_TYPE = "outdoor"
DEFAULT_DISINFECTION_METHOD = "chlorine"

# Verfügbare Pool-Typen
POOL_TYPES = [
    "outdoor",       # Freibad
    "indoor",        # Hallenbad
    "whirlpool",     # Whirlpool/Jacuzzi
    "natural",       # Naturpool/Schwimmteich
    "combination",   # Kombination
]

# Verfügbare Desinfektionsmethoden
DISINFECTION_METHODS = [
    "chlorine",      # Klassisches Chlor
    "salt",          # Salzelektrolyse
    "bromine",       # Brom
    "active_oxygen", # Aktivsauerstoff
    "uv",            # UV-Desinfektion
    "ozone",         # Ozon-Desinfektion
]

# Verfügbare Features zur Aktivierung
AVAILABLE_FEATURES = [
    {
        "id": "heating",
        "name": "Heizung",
        "description": "Kontrolle der Pool-Heizung",
        "default": True,
        "platforms": ["climate"],
    },
    {
        "id": "solar",
        "name": "Solarabsorber",
        "description": "Kontrolle des Solarabsorbers",
        "default": True,
        "platforms": ["climate"],
    },
    {
        "id": "ph_control",
        "name": "pH-Kontrolle",
        "description": "Überwachung und Steuerung des pH-Werts",
        "default": True,
        "platforms": ["number", "sensor"],
    },
    {
        "id": "chlorine_control",
        "name": "Chlor-Kontrolle",
        "description": "Überwachung und Steuerung des Chlorgehalts",
        "default": True,
        "platforms": ["number", "sensor"],
    },
    {
        "id": "cover_control",
        "name": "Abdeckungssteuerung",
        "description": "Steuerung der Pool-Abdeckung",
        "default": True,
        "platforms": ["cover"],
    },
    {
        "id": "backwash",
        "name": "Rückspülung",
        "description": "Steuerung der Rückspülung",
        "default": True,
        "platforms": ["switch"],
    },
    {
        "id": "pv_surplus",
        "name": "PV-Überschuss",
        "description": "Nutzung von PV-Überschuss für Poolgeräte",
        "default": True,
        "platforms": ["switch"],
    },
    {
        "id": "water_level",
        "name": "Wasserstand",
        "description": "Überwachung und Steuerung des Wasserstands",
        "default": False,
        "platforms": ["sensor", "switch"],
    },
    {
        "id": "water_refill",
        "name": "Wassernachfüllung",
        "description": "Automatische Wassernachfüllung",
        "default": False,
        "platforms": ["switch"],
    },
    {
        "id": "led_lighting",
        "name": "LED-Beleuchtung",
        "description": "Steuerung der Pool-Beleuchtung",
        "default": True,
        "platforms": ["switch"],
    },
]

# SemVer-ähnliches Regex, das auch Unterstriche zulässt
FIRMWARE_REGEX = (
    r"^(0|[1-9]\d*)\."                  # MAJOR
    r"(0|[1-9]\d*)\."                   # MINOR
    r"(0|[1-9]\d*)"                     # PATCH
    r"(?:-((?:[0-9A-Za-z-_]+)(?:\.[0-9A-Za-z-_]+)*))?"  # optionaler PRERELEASE
    r"(?:\+((?:[0-9A-Za-z-_]+)(?:\.[0-9A-Za-z-_]+)*))?"  # optionales BUILD
)

def validate_ip_address(ip: str) -> bool:
    """Validiere IP-Adresse."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def parse_firmware_version(firmware_version: str) -> Optional[Dict[str, Any]]:
    """Zerlege Firmware-Version in ihre Komponenten."""
    match = re.match(FIRMWARE_REGEX, firmware_version)
    if not match:
        return None
    
    return {
        "major": int(match.group(1)),
        "minor": int(match.group(2)),
        "patch": int(match.group(3)),
        "prerelease": match.group(4) if match.group(4) else None,
        "build": match.group(5) if match.group(5) else None
    }

def _format_error_message(err: Exception) -> str:
    """Formatiere Fehlermeldungen benutzerfreundlich."""
    error_map = {
        asyncio.TimeoutError: "Zeitüberschreitung bei der Verbindung",
        aiohttp.ClientConnectionError: "Verbindungsfehler",
        aiohttp.ClientResponseError: "Fehler in der API-Antwort",
        ValueError: "Ungültige Konfiguration"
    }
    return error_map.get(type(err), str(err))

async def fetch_api_data(
    session: aiohttp.ClientSession,
    api_url: str,
    auth: Optional[aiohttp.BasicAuth],
    use_ssl: bool,
    timeout_duration: int,
    retry_attempts: int,
) -> Dict[str, Any]:
    """
    Hole Daten von der API mit Retry-Logik und exponentiellem Backoff.
    """
    for attempt in range(retry_attempts):
        try:
            async with async_timeout.timeout(timeout_duration):
                _LOGGER.debug(
                    "Versuche Verbindung zur API unter %s (SSL=%s), Versuch %d/%d",
                    api_url,
                    use_ssl,
                    attempt + 1,
                    retry_attempts,
                )
                async with session.get(api_url, auth=auth, ssl=use_ssl) as response:
                    if response.status >= 400:
                        error_msg = f"HTTP-Fehler {response.status}: {response.reason}"
                        _LOGGER.error(error_msg)
                        if response.status == 401:
                            raise ValueError("Authentifizierungsfehler. Bitte Benutzername und Passwort prüfen.")
                        elif response.status == 404:
                            raise ValueError("API-Endpunkt nicht gefunden. Bitte URL prüfen.")
                        else:
                            raise aiohttp.ClientResponseError(
                                request_info=response.request_info, 
                                history=response.history, 
                                status=response.status,
                                message=error_msg,
                                headers=response.headers
                            )
                    
                    data = await response.json()
                    _LOGGER.debug("API-Antwort erhalten: %s", data)
                    return data

        except (
            aiohttp.ClientConnectionError,
            aiohttp.ClientResponseError,
            asyncio.TimeoutError,
        ) as err:
            _LOGGER.error("API-Fehler: %s (Versuch %d/%d)", err, attempt + 1, retry_attempts)
            if attempt + 1 == retry_attempts:
                raise ValueError(
                    f"API-Anfrage nach {retry_attempts} Versuchen fehlgeschlagen: {_format_error_message(err)}"
                ) from err

        # Exponentielles Backoff: Warte 2^attempt Sekunden
        await asyncio.sleep(2**attempt)

    raise ValueError("Fehler beim Abrufen der API-Daten nach allen Versuchen.")


class VioletDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für den Violet Pool Controller."""
    VERSION = 1
    
    def __init__(self):
        """Initialisiere den Config Flow."""
        self._config_data = {}
        self._api_data = None

    async def async_step_user(
        self, 
        user_input: Optional[Dict[str, Union[str, bool, int]]] = None
    ) -> config_entries.FlowResult:
        """Erster Schritt (benutzerinitiierte Eingabe) für das Setup."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                # Validiere IP-Adresse
                if not validate_ip_address(user_input[CONF_API_URL]):
                    errors[CONF_API_URL] = "Ungültige IP-Adresse"

                # Validiere numerische Eingaben
                polling_interval = int(user_input.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL))
                timeout_duration = int(user_input.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION))
                retry_attempts = int(user_input.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS))

                # Konfigurationsdaten aus dem Formular übernehmen
                self._config_data = {
                    "base_ip": user_input[CONF_API_URL],
                    "use_ssl": user_input.get(CONF_USE_SSL, DEFAULT_USE_SSL),
                    "device_name": user_input.get(CONF_DEVICE_NAME, "Violet Pool Controller"),
                    "username": user_input.get(CONF_USERNAME),
                    "password": user_input.get(CONF_PASSWORD),
                    "device_id": user_input.get(CONF_DEVICE_ID, 1),
                    "polling_interval": polling_interval,
                    "timeout_duration": timeout_duration,
                    "retry_attempts": retry_attempts,
                }

                # Protokoll-URL zusammenbauen
                protocol = "https" if self._config_data["use_ssl"] else "http"
                # Füge den "?ALL" Query-Parameter hinzu
                api_url = f"{protocol}://{self._config_data['base_ip']}{API_READINGS}?ALL"

                # Eindeutige ID: Kombination aus IP und device_id
                await self.async_set_unique_id(f"{self._config_data['base_ip']}-{self._config_data['device_id']}")
                self._abort_if_unique_id_configured()

                # Versuche Daten von der API zu holen
                session = aiohttp_client.async_get_clientsession(self.hass)
                auth = None
                if self._config_data["username"]:
                    auth = aiohttp.BasicAuth(
                        login=self._config_data["username"], 
                        password=self._config_data.get("password", "")
                    )

                self._api_data = await fetch_api_data(
                    session=session,
                    api_url=api_url,
                    auth=auth,
                    use_ssl=self._config_data["use_ssl"],
                    timeout_duration=self._config_data["timeout_duration"],
                    retry_attempts=self._config_data["retry_attempts"],
                )

                await self._process_firmware_data(self._api_data, errors)

            except Exception as err:
                _LOGGER.error("Fehler beim Abrufen/Verarbeiten der Daten: %s", err)
                errors["base"] = _format_error_message(err)

            # Wenn keine Fehler aufgetreten sind, gehe zum nächsten Schritt
            if not errors:
                return await self.async_step_pool_setup()

        # Formular-Schema mit verbesserten Validierungen
        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_URL, default="192.168.1.100"): str,
                vol.Optional(CONF_USERNAME): str,
                vol.Optional(CONF_PASSWORD): str,
                vol.Required(CONF_USE_SSL, default=DEFAULT_USE_SSL): bool,
                vol.Required(CONF_DEVICE_ID, default=1): vol.All(vol.Coerce(int), vol.Range(min=1)),

                # Polling, Timeout und Retry separat mit verbesserten Validierungen
                vol.Required(
                    CONF_POLLING_INTERVAL, 
                    default=str(DEFAULT_POLLING_INTERVAL)
                ): vol.All(str, vol.Coerce(int), vol.Range(min=10, max=3600)),
                
                vol.Required(
                    CONF_TIMEOUT_DURATION, 
                    default=str(DEFAULT_TIMEOUT_DURATION)
                ): vol.All(str, vol.Coerce(int), vol.Range(min=1, max=60)),
                
                vol.Required(
                    CONF_RETRY_ATTEMPTS, 
                    default=str(DEFAULT_RETRY_ATTEMPTS)
                ): vol.All(str, vol.Coerce(int), vol.Range(min=1, max=10)),

                vol.Optional(CONF_DEVICE_NAME, default="Violet Pool Controller"): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def async_step_pool_setup(
        self, 
        user_input: Optional[Dict[str, Any]] = None
    ) -> config_entries.FlowResult:
        """Zweiter Schritt: Pool-Grundeinstellungen."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            # Validiere Eingaben
            try:
                pool_size = float(user_input.get(CONF_POOL_SIZE, DEFAULT_POOL_SIZE))
                if pool_size <= 0:
                    errors[CONF_POOL_SIZE] = "Ungültige Poolgröße"
            except ValueError:
                errors[CONF_POOL_SIZE] = "Ungültige Poolgröße"

            if not errors:
                # Speichere Pool-Einstellungen
                self._config_data.update({
                    CONF_POOL_SIZE: pool_size,
                    CONF_POOL_TYPE: user_input.get(CONF_POOL_TYPE, DEFAULT_POOL_TYPE),
                    CONF_DISINFECTION_METHOD: user_input.get(CONF_DISINFECTION_METHOD, DEFAULT_DISINFECTION_METHOD),
                })
                
                # Weiter zum Feature-Auswahlschritt
                return await self.async_step_feature_selection()
                    
        # Formular für Pool-Einstellungen
        pool_type_options = {t: t.capitalize() for t in POOL_TYPES}
        disinfection_options = {m: m.capitalize().replace("_", " ") for m in DISINFECTION_METHODS}
        
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_POOL_SIZE, 
                    default=DEFAULT_POOL_SIZE
                ): vol.All(vol.Coerce(float), vol.Range(min=0.1)),
                
                vol.Required(
                    CONF_POOL_TYPE, 
                    default=DEFAULT_POOL_TYPE
                ): vol.In(pool_type_options),
                
                vol.Required(
                    CONF_DISINFECTION_METHOD, 
                    default=DEFAULT_DISINFECTION_METHOD
                ): vol.In(disinfection_options),
            }
        )

        return self.async_show_form(
            step_id="pool_setup", 
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "device_name": self._config_data.get("device_name", "Violet Pool Controller")
            },
        )

    async def async_step_feature_selection(
        self, 
        user_input: Optional[Dict[str, bool]] = None
    ) -> config_entries.FlowResult:
        """Dritter Schritt: Feature-Auswahl."""
        errors: Dict[str, str] = {}

        # Bestimme verfügbare Features basierend auf API-Daten
        available_features = self._determine_available_features()

        if user_input is not None:
            # Speichere aktivierte Features
            active_features = []
            for feature in available_features:
                if user_input.get(feature["id"], feature["default"]):
                    active_features.append(feature["id"])
            
            self._config_data[CONF_ACTIVE_FEATURES] = active_features
            
            # Integration anlegen
            return self.async_create_entry(
                title=f"{self._config_data['device_name']} (ID {self._config_data['device_id']})",
                data=self._config_data,
            )

        # Erstelle Schema für Feature-Auswahl
        schema_dict = {}
        for feature in available_features:
            schema_dict[vol.Required(feature["id"], default=feature["default"])] = bool
        
        data_schema = vol.Schema(schema_dict)

        return self.async_show_form(
            step_id="feature_selection", 
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "device_name": self._config_data.get("device_name", "Violet Pool Controller")
            },
        )

    def _determine_available_features(self) -> List[Dict[str, Any]]:
        """Bestimmt verfügbare Features basierend auf API-Daten."""
        # Wenn keine API-Daten verfügbar sind, alle Features zeigen
        if not self._api_data:
            return AVAILABLE_FEATURES
        
        # Sonst API-Daten prüfen und nur unterstützte Features zeigen
        api_data_keys = set(self._api_data.keys())
        available_features = []
        
        # Feature-Erkennungsliste
        feature_detection = {
            "heating": ["HEATER", "onewire5_value"],
            "solar": ["SOLAR", "onewire3_value"],
            "ph_control": ["pH_value", "DOS_4_PHM", "DOS_5_PHP"],
            "chlorine_control": ["orp_value", "pot_value", "DOS_1_CL"],
            "cover_control": ["COVER_STATE", "COVER_OPEN", "COVER_CLOSE"],
            "backwash": ["BACKWASH", "BACKWASHRINSE"],
            "pv_surplus": ["PVSURPLUS"],
            "water_level": ["ADC2_value", "REFILL"],
            "water_refill": ["REFILL"],
            "led_lighting": ["LIGHT", "DMX_SCENE1"]
        }
        
        # Alle Standard-Features vorbereiten
        feature_map = {feature["id"]: feature for feature in AVAILABLE_FEATURES}
        detected_features = set()
        
        # Erkenne Features basierend auf API-Daten
        for feature_id, detection_keys in feature_detection.items():
            if any(key in api_data_keys for key in detection_keys):
                detected_features.add(feature_id)
        
        # Füge erkannte Features hinzu
        for feature_id in list(feature_map.keys()):
            if feature_id in detected_features:
                available_features.append(feature_map[feature_id])
            else:
                # Füge nicht-erkannte Features als optional hinzu (standard auf False)
                feature = feature_map[feature_id].copy()
                feature["default"] = False
                available_features.append(feature)
                
        return available_features

    async def _process_firmware_data(self, data: Dict[str, Any], errors: Dict[str, str]) -> None:
        """Prüft die Firmware-Version in den API-Daten und fügt ggf. Fehler hinzu."""
        firmware_version = data.get("fw")

        if not firmware_version:
            errors["base"] = "Firmware-Daten fehlen in der API-Antwort."
            return

        parsed_firmware = parse_firmware_version(firmware_version)
        if not parsed_firmware:
            errors["base"] = f"Ungültige Firmware-Version: {firmware_version}"
            return
            
        # Hier könnten weitere Firmware-Prüfungen stattfinden, z.B. Mindestversion

    @staticmethod
    def async_get_options_flow(config_entry):
        """Gibt den Options Flow zurück."""
        return VioletOptionsFlowHandler(config_entry)


class VioletOptionsFlowHandler(config_entries.OptionsFlow):
    """OptionsFlow, um nachträglich Polling, Timeout, Retry und Features zu ändern."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Speichere das ConfigEntry."""
        # Store a reference to the entry_id instead of the config_entry itself
        self.entry_id = config_entry.entry_id
        # Keep a reference to the entry data and existing options for use in the flow
        self.entry_data = dict(config_entry.data)
        self.entry_options = dict(config_entry.options)
        self._api_data = None

    async def async_step_init(self, user_input=None):
        """Erster Options-Schritt."""
        if user_input is not None:
            # Speichere die neuen Options
            if user_input.get("go_to_features", False):
                # Wenn "Weiter zu Features" gewählt wurde, zum Feature-Schritt gehen
                return await self.async_step_features()
                
            # Nur die relevanten Optionen speichern (ohne "go_to_features")
            options = {k: v for k, v in user_input.items() if k != "go_to_features"}
            return self.async_create_entry(title="", data=options)

        # Bestehende Options oder Defaults lesen
        polling = self.entry_options.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
        timeout = self.entry_options.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION)
        retries = self.entry_options.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS)

        options_schema = vol.Schema(
            {
                vol.Required(
                    CONF_POLLING_INTERVAL, 
                    default=polling
                ): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
                
                vol.Required(
                    CONF_TIMEOUT_DURATION, 
                    default=timeout
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
                
                vol.Required(
                    CONF_RETRY_ATTEMPTS, 
                    default=retries
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
                
                vol.Required(
                    "go_to_features",
                    default=False
                ): bool,
            }
        )
        return self.async_show_form(step_id="init", data_schema=options_schema)

    async def async_step_features(self, user_input=None):
        """Erlaubt die Auswahl von Features für die Integration."""
        errors = {}
        
        if user_input is not None:
            try:
                # Speichere die ausgewählten Features
                active_features = []
                
                # Hole die aktiven Features aus den API-Daten
                available_features = self._determine_available_features()
                
                # Verarbeite die Auswahl des Benutzers
                for feature in available_features:
                    if user_input.get(feature["id"], feature["default"]):
                        active_features.append(feature["id"])
                
                # Aktualisiere die Options
                options = dict(self.entry_options)
                options[CONF_ACTIVE_FEATURES] = active_features
                
                # Erstelle einen aktualisierten Config-Entry
                return self.async_create_entry(title="", data=options)
            except Exception as err:
                _LOGGER.error("Fehler beim Speichern der Features: %s", err)
                errors["base"] = f"Fehler: {err}"
        
        # Bestimme die verfügbaren Features
        available_features = self._determine_available_features()
        
        # Aktuelle Auswahl berücksichtigen
        current_features = self.entry_options.get(CONF_ACTIVE_FEATURES, [])
        
        # Erstelle das Formular für die Feature-Auswahl
        schema_dict = {}
        for feature in available_features:
            default = feature["id"] in current_features if current_features else feature["default"]
            schema_dict[vol.Optional(feature["id"], default=default)] = bool
        
        options_schema = vol.Schema(schema_dict)
        
        # Find device_name from the integration's data since we don't have direct config_entry access
        device_name = self.entry_data.get(CONF_DEVICE_NAME, "Violet Pool Controller")
        
        # Zeige das Formular
        return self.async_show_form(
            step_id="features", 
            data_schema=options_schema, 
            errors=errors,
            description_placeholders={
                "device_name": device_name
            }
        )
        
    def _determine_available_features(self) -> List[Dict[str, Any]]:
        """Bestimmt verfügbare Features basierend auf API-Daten oder vorhandenen Einstellungen."""
        # Wenn API-Daten verfügbar sind, diese verwenden
        if self._api_data:
            # Hier könnte die gleiche Logik wie in VioletDeviceConfigFlow._determine_available_features verwendet werden
            api_data_keys = set(self._api_data.keys())
            available_features = []
            
            # Feature-Erkennungsliste
            feature_detection = {
                "heating": ["HEATER", "onewire5_value"],
                "solar": ["SOLAR", "onewire3_value"],
                "ph_control": ["pH_value", "DOS_4_PHM", "DOS_5_PHP"],
                "chlorine_control": ["orp_value", "pot_value", "DOS_1_CL"],
                "cover_control": ["COVER_STATE", "COVER_OPEN", "COVER_CLOSE"],
                "backwash": ["BACKWASH", "BACKWASHRINSE"],
                "pv_surplus": ["PVSURPLUS"],
                "water_level": ["ADC2_value", "REFILL"],
                "water_refill": ["REFILL"],
                "led_lighting": ["LIGHT", "DMX_SCENE1"]
            }
            
            # Alle Standard-Features vorbereiten
            feature_map = {feature["id"]: feature for feature in AVAILABLE_FEATURES}
            detected_features = set()
            
            # Erkenne Features basierend auf API-Daten
            for feature_id, detection_keys in feature_detection.items():
                if any(key in api_data_keys for key in detection_keys):
                    detected_features.add(feature_id)
            
            # Füge erkannte Features hinzu
            for feature_id in list(feature_map.keys()):
                if feature_id in detected_features:
                    available_features.append(feature_map[feature_id])
                else:
                    # Füge nicht-erkannte Features als optional hinzu (standard auf False)
                    feature = feature_map[feature_id].copy()
                    feature["default"] = False
                    available_features.append(feature)
                    
            return available_features
            
        # Wenn keine API-Daten, verwende aktuelle Config oder Standardwerte
        current_features = self.entry_options.get(CONF_ACTIVE_FEATURES, [])
        if current_features:
            # Setze Features basierend auf aktueller Konfiguration
            features = []
            for feature in AVAILABLE_FEATURES:
                new_feature = feature.copy()
                new_feature["default"] = feature["id"] in current_features
                features.append(new_feature)
            return features
        
        # Fallback: Standardfeatures
        return AVAILABLE_FEATURES

    async def _fetch_api_data(self) -> None:
        """Holt aktuelle API-Daten für Feature-Erkennung."""
        try:
            # Here we need to get these values from the stored data rather than from config_entry
            base_ip = self.entry_data.get('base_ip')
            use_ssl = self.entry_data.get('use_ssl', True)
            username = self.entry_data.get('username')
            password = self.entry_data.get('password', '')
            timeout_duration = self.entry_data.get('timeout_duration', DEFAULT_TIMEOUT_DURATION)
            retry_attempts = self.entry_data.get('retry_attempts', DEFAULT_RETRY_ATTEMPTS)
            
            protocol = "https" if use_ssl else "http"
            api_url = f"{protocol}://{base_ip}{API_READINGS}?ALL"
            
            session = aiohttp_client.async_get_clientsession(self.hass)
            auth = None
            
            if username:
                auth = aiohttp.BasicAuth(
                    login=username, 
                    password=password
                )
                
            self._api_data = await fetch_api_data(
                session=session,
                api_url=api_url,
                auth=auth,
                use_ssl=use_ssl,
                timeout_duration=timeout_duration,
                retry_attempts=retry_attempts,
            )
        except Exception as err:
            _LOGGER.error("Fehler beim Abrufen der API-Daten für Options: %s", err)
            self._api_data = None