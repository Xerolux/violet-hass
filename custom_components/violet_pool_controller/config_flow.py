"""Config Flow für Violet Pool Controller Integration - OPTIMIZED VERSION."""
import logging
import ipaddress
import asyncio
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client
from homeassistant.data_entry_flow import FlowResult

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
    CONF_POOL_SIZE,
    CONF_POOL_TYPE,
    CONF_DISINFECTION_METHOD,
    DEFAULT_USE_SSL,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_POOL_SIZE,
    DEFAULT_POOL_TYPE,
    DEFAULT_DISINFECTION_METHOD,
    AVAILABLE_FEATURES,
)

_LOGGER = logging.getLogger(__name__)

# Konstanten für Validierung
MIN_POLLING_INTERVAL = 10
MAX_POLLING_INTERVAL = 3600
MIN_TIMEOUT = 1
MAX_TIMEOUT = 60
MIN_RETRIES = 1
MAX_RETRIES = 10
MIN_POOL_SIZE = 0.1
MAX_POOL_SIZE = 1000.0
MIN_DEVICE_ID = 1

# Retry-Konstanten
BASE_RETRY_DELAY = 2  # Basis für exponentielles Backoff
DEFAULT_API_TIMEOUT = 10

# Error Messages als Konstanten
ERROR_ALREADY_CONFIGURED = "already_configured"
ERROR_INVALID_IP = "invalid_ip_address"
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_AGREEMENT_DECLINED = "agreement_declined"

# Pool Type Options
POOL_TYPE_OPTIONS = {
    "outdoor": "🏖️ Freibad",
    "indoor": "🏠 Hallenbad",
    "whirlpool": "🛁 Whirlpool/Spa",
    "natural": "🌿 Naturpool/Schwimmteich",
    "combination": "🔄 Kombination",
}

# Disinfection Method Options
DISINFECTION_OPTIONS = {
    "chlorine": "🧪 Chlor (Flüssig/Tabletten)",
    "salt": "🧂 Salzelektrolyse",
    "bromine": "⚗️ Brom",
    "active_oxygen": "💧 Aktivsauerstoff/H₂O₂",
    "uv": "💡 UV-Desinfektion",
    "ozone": "🌀 Ozon-Desinfektion",
}

# Enhanced Features Info
ENHANCED_FEATURES = {
    "heating": {"icon": "🔥", "name": "Heizungssteuerung", "desc": "Poolheizung automatisch steuern"},
    "solar": {"icon": "☀️", "name": "Solarabsorber", "desc": "Kostenlose Sonnenenergie nutzen"},
    "ph_control": {"icon": "🧪", "name": "pH-Automatik", "desc": "Perfekte Wasserqualität rund um die Uhr"},
    "chlorine_control": {"icon": "💧", "name": "Chlor-Management", "desc": "Sichere Desinfektion automatisch"},
    "cover_control": {"icon": "🪟", "name": "Abdeckungssteuerung", "desc": "Intelligent öffnen und schließen"},
    "backwash": {"icon": "🔄", "name": "Rückspül-Automatik", "desc": "Filter automatisch reinigen"},
    "pv_surplus": {"icon": "🔋", "name": "PV-Überschuss", "desc": "Solarstrom optimal nutzen"},
    "filter_control": {"icon": "🌊", "name": "Filterpumpe", "desc": "Effiziente Wasserzirkulation"},
    "water_level": {"icon": "📏", "name": "Füllstand-Monitor", "desc": "Wasserstand überwachen"},
    "water_refill": {"icon": "🚰", "name": "Auto-Nachfüllung", "desc": "Nie wieder zu wenig Wasser"},
    "led_lighting": {"icon": "💡", "name": "LED-Beleuchtung", "desc": "Stimmungsvolle Pool-Atmosphäre"},
    "digital_inputs": {"icon": "🔌", "name": "Digitale Eingänge", "desc": "Externe Sensoren integrieren"},
    "extension_outputs": {"icon": "🔗", "name": "Erweiterungsmodule", "desc": "Zusätzliche Geräte anschließen"},
}


def validate_ip_address(ip: str) -> bool:
    """Validiere IP-Adresse."""
    try:
        ipaddress.ip_address(ip)
        _LOGGER.debug("IP-Adresse %s ist gültig", ip)
        return True
    except ValueError:
        _LOGGER.warning("Ungültige IP-Adresse: %s", ip)
        return False


async def fetch_api_data(
    session: aiohttp.ClientSession,
    api_url: str,
    auth: aiohttp.BasicAuth | None,
    use_ssl: bool,
    timeout: int,
    retries: int,
) -> dict[str, Any]:
    """API-Daten mit Retry-Logik abrufen."""
    _LOGGER.debug(
        "Rufe API-Daten ab von %s (SSL: %s, Timeout: %ds, Retries: %d)",
        api_url,
        use_ssl,
        timeout,
        retries,
    )

    for attempt in range(retries):
        try:
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            async with session.get(
                api_url, auth=auth, ssl=use_ssl if use_ssl else False, timeout=timeout_obj
            ) as response:
                response.raise_for_status()
                data = await response.json()
                _LOGGER.debug(
                    "API-Daten erfolgreich abgerufen (Versuch %d/%d)", attempt + 1, retries
                )
                return data
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            if attempt + 1 == retries:
                _LOGGER.error("API-Fehler nach %d Versuchen: %s", retries, err)
                raise ValueError(f"API-Anfrage fehlgeschlagen: {err}") from err

            retry_delay = BASE_RETRY_DELAY**attempt
            _LOGGER.warning(
                "API-Versuch %d/%d fehlgeschlagen, wiederhole in %ds: %s",
                attempt + 1,
                retries,
                retry_delay,
                err,
            )
            await asyncio.sleep(retry_delay)

    raise ValueError("Fehler nach allen Versuchen")


class VioletDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für Violet Pool Controller - OPTIMIZED VERSION."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self) -> None:
        """Initialisiere Config Flow."""
        self._config_data: dict[str, Any] = {}
        _LOGGER.info("Violet Pool Controller Setup gestartet")

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Options Flow zurückgeben."""
        return VioletOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Schritt 1: User-initiierter Setup-Start."""
        if user_input is None:
            return await self.async_step_disclaimer()
        return await self.async_step_connection()

    async def async_step_disclaimer(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """⚠️ Disclaimer und Nutzungsbedingungen."""
        if user_input:
            agreement = user_input.get("agreement", False)
            if agreement:
                _LOGGER.info("Nutzer hat Disclaimer akzeptiert")
                return await self.async_step_connection()
            else:
                _LOGGER.info("Nutzer hat Disclaimer abgelehnt - Setup abgebrochen")
                return self.async_abort(reason=ERROR_AGREEMENT_DECLINED)

        disclaimer_text = self._get_disclaimer_text()

        return self.async_show_form(
            step_id="disclaimer",
            data_schema=vol.Schema(
                {
                    vol.Required("agreement", default=False): bool,
                }
            ),
            description_placeholders={
                "disclaimer_text": disclaimer_text,
            },
        )

    async def async_step_connection(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """🌐 Schritt 2: Controller-Verbindung konfigurieren."""
        errors = {}

        if user_input:
            ip_address = user_input[CONF_API_URL]

            # Prüfe auf Duplikate
            if self._is_duplicate_entry(ip_address):
                errors["base"] = ERROR_ALREADY_CONFIGURED
                _LOGGER.warning("IP-Adresse %s bereits konfiguriert", ip_address)

            # Validiere IP-Adresse
            if not errors and not validate_ip_address(ip_address):
                errors[CONF_API_URL] = ERROR_INVALID_IP

            if not errors:
                self._config_data = self._build_config_data(user_input)

                # Setze Unique ID
                await self.async_set_unique_id(
                    f"{self._config_data[CONF_API_URL]}-{self._config_data[CONF_DEVICE_ID]}"
                )
                self._abort_if_unique_id_configured()

                # Teste API-Verbindung
                if await self._test_connection():
                    _LOGGER.info("Verbindung erfolgreich, fahre mit Pool-Setup fort")
                    return await self.async_step_pool_setup()
                else:
                    errors["base"] = ERROR_CANNOT_CONNECT

        return self.async_show_form(
            step_id="connection",
            data_schema=self._get_connection_schema(),
            errors=errors,
            description_placeholders={
                "step_icon": "🌐",
                "step_title": "Controller-Verbindung",
                "step_description": "Konfiguriere die Verbindung zu deinem Violet Pool Controller",
            },
        )

    async def async_step_pool_setup(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """🏊 Schritt 3: Pool-Konfiguration."""
        if user_input:
            self._config_data.update(
                {
                    CONF_POOL_SIZE: float(user_input[CONF_POOL_SIZE]),
                    CONF_POOL_TYPE: user_input[CONF_POOL_TYPE],
                    CONF_DISINFECTION_METHOD: user_input[CONF_DISINFECTION_METHOD],
                }
            )
            _LOGGER.info(
                "Pool konfiguriert: %sm³, Typ: %s, Desinfektion: %s",
                self._config_data[CONF_POOL_SIZE],
                self._config_data[CONF_POOL_TYPE],
                self._config_data[CONF_DISINFECTION_METHOD],
            )
            return await self.async_step_feature_selection()

        return self.async_show_form(
            step_id="pool_setup",
            data_schema=self._get_pool_setup_schema(),
            description_placeholders={
                "device_name": self._config_data.get(
                    CONF_DEVICE_NAME, "🌊 Violet Pool Controller"
                ),
                "step_icon": "🏊",
                "step_title": "Pool-Konfiguration",
                "step_description": f"Konfiguriere die Eigenschaften deines Pools für {self._config_data.get(CONF_DEVICE_NAME, 'den Controller')}",
            },
        )

    async def async_step_feature_selection(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """⚙️ Schritt 4: Feature-Auswahl."""
        if user_input:
            active_features = self._extract_active_features(user_input)
            self._config_data[CONF_ACTIVE_FEATURES] = active_features

            _LOGGER.info("Features aktiviert: %s", ", ".join(active_features))

            title = self._generate_entry_title()
            _LOGGER.info("Integration erfolgreich eingerichtet: %s", title)

            return self.async_create_entry(title=title, data=self._config_data)

        return self.async_show_form(
            step_id="feature_selection",
            data_schema=self._get_feature_selection_schema(),
            description_placeholders={
                "device_name": self._config_data.get(
                    CONF_DEVICE_NAME, "🌊 Violet Pool Controller"
                ),
                "pool_size": str(self._config_data.get(CONF_POOL_SIZE, DEFAULT_POOL_SIZE)),
                "step_icon": "⚙️",
                "step_title": "Smart-Features aktivieren",
                "step_description": f"Wähle die gewünschten Automatisierungsfunktionen für deinen {self._config_data.get(CONF_POOL_SIZE, DEFAULT_POOL_SIZE)}m³ Pool",
                "features_info": ENHANCED_FEATURES,
            },
        )

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _is_duplicate_entry(self, ip_address: str) -> bool:
        """Prüfe ob IP-Adresse bereits konfiguriert ist."""
        for entry in self._async_current_entries():
            existing_ip = (
                entry.data.get(CONF_API_URL)
                or entry.data.get("host")
                or entry.data.get("base_ip")
            )
            if existing_ip == ip_address:
                return True
        return False

    def _build_config_data(self, user_input: dict[str, Any]) -> dict[str, Any]:
        """Baue Config-Dictionary aus User-Input."""
        return {
            CONF_API_URL: user_input[CONF_API_URL],
            CONF_USE_SSL: user_input.get(CONF_USE_SSL, DEFAULT_USE_SSL),
            CONF_DEVICE_NAME: user_input.get(
                CONF_DEVICE_NAME, "🌊 Violet Pool Controller"
            ),
            CONF_USERNAME: user_input.get(CONF_USERNAME, ""),
            CONF_PASSWORD: user_input.get(CONF_PASSWORD, ""),
            CONF_DEVICE_ID: int(user_input.get(CONF_DEVICE_ID, 1)),
            CONF_POLLING_INTERVAL: int(
                user_input.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
            ),
            CONF_TIMEOUT_DURATION: int(
                user_input.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION)
            ),
            CONF_RETRY_ATTEMPTS: int(
                user_input.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS)
            ),
        }

    async def _test_connection(self) -> bool:
        """Teste API-Verbindung."""
        try:
            protocol = "https" if self._config_data[CONF_USE_SSL] else "http"
            api_url = f"{protocol}://{self._config_data[CONF_API_URL]}{API_READINGS}?ALL"

            _LOGGER.info("Teste Verbindung zu %s", api_url)
            session = aiohttp_client.async_get_clientsession(self.hass)

            auth = None
            if self._config_data[CONF_USERNAME]:
                auth = aiohttp.BasicAuth(
                    self._config_data[CONF_USERNAME], self._config_data[CONF_PASSWORD]
                )

            await fetch_api_data(
                session,
                api_url,
                auth,
                self._config_data[CONF_USE_SSL],
                self._config_data[CONF_TIMEOUT_DURATION],
                self._config_data[CONF_RETRY_ATTEMPTS],
            )
            return True

        except ValueError as err:
            _LOGGER.error("Verbindungstest fehlgeschlagen: %s", err)
            return False

    def _extract_active_features(self, user_input: dict[str, Any]) -> list[str]:
        """Extrahiere aktive Features aus User-Input."""
        active_features = []
        for feature in AVAILABLE_FEATURES:
            checkbox_key = f"enable_{feature['id']}"
            if user_input.get(checkbox_key, feature["default"]):
                active_features.append(feature["id"])
        return active_features

    def _generate_entry_title(self) -> str:
        """Generiere Titel für Config Entry."""
        device_name = self._config_data.get(CONF_DEVICE_NAME, "🌊 Violet Pool Controller")
        device_id = self._config_data.get(CONF_DEVICE_ID, 1)
        pool_size = self._config_data.get(CONF_POOL_SIZE, DEFAULT_POOL_SIZE)
        return f"{device_name} (ID {device_id}) • {pool_size}m³"

    def _get_disclaimer_text(self) -> str:
        """Generiere Disclaimer-Text."""
        return """
⚠️ WICHTIGE SICHERHEITSHINWEISE

Diese Integration steuert Pool-Hardware und Chemikaliendosierung.

🔴 HAUPTRISIKEN:
• Automatische Steuerung von Pumpen, Heizungen und Chemikaliendosierung
• Fernzugriff ohne lokale Überwachung möglich
• Fehlfunktionen können Sach- und Gesundheitsschäden verursachen

✅ IHRE VERANTWORTUNG:
• Regelmäßige manuelle Kontrolle der Wasserwerte
• Notfall-Zugang zu allen Systemen sicherstellen
• Bei Störungen: Automatik sofort deaktivieren

⚖️ HAFTUNGSAUSSCHLUSS:
Der Entwickler übernimmt keine Haftung für Schäden jeglicher Art durch die 
Nutzung dieser Software. Sie verwenden die Integration auf eigene Gefahr.

📚 Vollständige Nutzungsbedingungen: https://github.com/Xerolux/violet-hass

Durch Akzeptieren bestätigen Sie:
✓ Die Risiken verstanden zu haben
✓ Die volle Verantwortung zu übernehmen
✓ Den Entwickler von jeder Haftung freizustellen
        """

    def _get_connection_schema(self) -> vol.Schema:
        """Schema für Connection Step."""
        return vol.Schema(
            {
                vol.Required(CONF_API_URL, default="192.168.178.55"): str,
                vol.Optional(CONF_USERNAME, default=""): str,
                vol.Optional(CONF_PASSWORD, default=""): str,
                vol.Required(CONF_USE_SSL, default=DEFAULT_USE_SSL): bool,
                vol.Required(CONF_DEVICE_ID, default=1): vol.All(
                    vol.Coerce(int), vol.Range(min=MIN_DEVICE_ID)
                ),
                vol.Required(
                    CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_POLLING_INTERVAL, max=MAX_POLLING_INTERVAL),
                ),
                vol.Required(CONF_TIMEOUT_DURATION, default=DEFAULT_TIMEOUT_DURATION): vol.All(
                    vol.Coerce(int), vol.Range(min=MIN_TIMEOUT, max=MAX_TIMEOUT)
                ),
                vol.Required(CONF_RETRY_ATTEMPTS, default=DEFAULT_RETRY_ATTEMPTS): vol.All(
                    vol.Coerce(int), vol.Range(min=MIN_RETRIES, max=MAX_RETRIES)
                ),
                vol.Optional(
                    CONF_DEVICE_NAME, default="🌊 Violet Pool Controller"
                ): str,
            }
        )

    def _get_pool_setup_schema(self) -> vol.Schema:
        """Schema für Pool Setup Step."""
        return vol.Schema(
            {
                vol.Required(CONF_POOL_SIZE, default=DEFAULT_POOL_SIZE): vol.All(
                    vol.Coerce(float), vol.Range(min=MIN_POOL_SIZE, max=MAX_POOL_SIZE)
                ),
                vol.Required(CONF_POOL_TYPE, default=DEFAULT_POOL_TYPE): vol.In(
                    POOL_TYPE_OPTIONS
                ),
                vol.Required(
                    CONF_DISINFECTION_METHOD, default=DEFAULT_DISINFECTION_METHOD
                ): vol.In(DISINFECTION_OPTIONS),
            }
        )

    def _get_feature_selection_schema(self) -> vol.Schema:
        """Schema für Feature Selection Step."""
        schema_dict = {}
        for feature in AVAILABLE_FEATURES:
            checkbox_key = f"enable_{feature['id']}"
            schema_dict[vol.Optional(checkbox_key, default=feature["default"])] = bool
        return vol.Schema(schema_dict)


class VioletOptionsFlowHandler(config_entries.OptionsFlow):
    """Options Flow für Violet Pool Controller - OPTIMIZED VERSION."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialisiere Options Flow."""
        self._config_entry = config_entry
        self.current_config = {**config_entry.data, **config_entry.options}
        _LOGGER.debug("Options Flow gestartet für %s", config_entry.title)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """🔧 Erweiterte Einstellungen verwalten."""
        if user_input:
            active_features = self._extract_active_features(user_input)
            user_input[CONF_ACTIVE_FEATURES] = active_features

            _LOGGER.info(
                "Konfiguration aktualisiert für %s - Features: %s",
                self._config_entry.title,
                ", ".join(active_features),
            )

            return self.async_create_entry(title="", data=user_input)

        device_name = self._config_entry.data.get(
            CONF_DEVICE_NAME, "🌊 Violet Pool Controller"
        )

        return self.async_show_form(
            step_id="init",
            data_schema=self._get_options_schema(),
            description_placeholders={
                "device_name": device_name,
                "step_icon": "🔧",
                "step_title": "Erweiterte Konfiguration",
                "step_description": f"Optimiere die Einstellungen für {device_name}",
                "features_info": ENHANCED_FEATURES,
            },
        )

    def _extract_active_features(self, user_input: dict[str, Any]) -> list[str]:
        """Extrahiere aktive Features aus User-Input."""
        active_features = []
        for feature in AVAILABLE_FEATURES:
            checkbox_key = f"feature_{feature['id']}"
            if user_input.pop(checkbox_key, False):
                active_features.append(feature["id"])
        return active_features

    def _get_options_schema(self) -> vol.Schema:
        """Schema für Options Flow."""
        schema_dict = {
            vol.Optional(
                CONF_POLLING_INTERVAL,
                default=self.current_config.get(
                    CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL
                ),
            ): vol.All(
                vol.Coerce(int),
                vol.Range(min=MIN_POLLING_INTERVAL, max=MAX_POLLING_INTERVAL),
            ),
            vol.Optional(
                CONF_TIMEOUT_DURATION,
                default=self.current_config.get(
                    CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION
                ),
            ): vol.All(vol.Coerce(int), vol.Range(min=MIN_TIMEOUT, max=MAX_TIMEOUT)),
            vol.Optional(
                CONF_RETRY_ATTEMPTS,
                default=self.current_config.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS),
            ): vol.All(vol.Coerce(int), vol.Range(min=MIN_RETRIES, max=MAX_RETRIES)),
            vol.Optional(
                CONF_POOL_SIZE,
                default=self.current_config.get(CONF_POOL_SIZE, DEFAULT_POOL_SIZE),
            ): vol.All(vol.Coerce(float), vol.Range(min=MIN_POOL_SIZE, max=MAX_POOL_SIZE)),
            vol.Optional(
                CONF_POOL_TYPE,
                default=self.current_config.get(CONF_POOL_TYPE, DEFAULT_POOL_TYPE),
            ): vol.In(POOL_TYPE_OPTIONS),
            vol.Optional(
                CONF_DISINFECTION_METHOD,
                default=self.current_config.get(
                    CONF_DISINFECTION_METHOD, DEFAULT_DISINFECTION_METHOD
                ),
            ): vol.In(DISINFECTION_OPTIONS),
        }

        # Add feature checkboxes
        current_features = self.current_config.get(CONF_ACTIVE_FEATURES, [])
        for feature in AVAILABLE_FEATURES:
            checkbox_key = f"feature_{feature['id']}"
            default_value = feature["id"] in current_features
            schema_dict[vol.Optional(checkbox_key, default=default_value)] = bool

        return vol.Schema(schema_dict)