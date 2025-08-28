"""Enhanced Config Flow für Violet Pool Controller mit modernem UI Design."""
import logging
import ipaddress
import asyncio
import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client
from homeassistant.data_entry_flow import FlowResult
from .const import (
    DOMAIN, API_READINGS, CONF_API_URL, CONF_USE_SSL, CONF_DEVICE_NAME, CONF_USERNAME,
    CONF_PASSWORD, CONF_DEVICE_ID, CONF_POLLING_INTERVAL, CONF_TIMEOUT_DURATION,
    CONF_RETRY_ATTEMPTS, CONF_ACTIVE_FEATURES, DEFAULT_USE_SSL, DEFAULT_POLLING_INTERVAL,
    DEFAULT_TIMEOUT_DURATION, DEFAULT_RETRY_ATTEMPTS, CONF_POOL_SIZE, CONF_POOL_TYPE,
    CONF_DISINFECTION_METHOD, DEFAULT_POOL_SIZE, DEFAULT_POOL_TYPE, DEFAULT_DISINFECTION_METHOD,
    POOL_TYPES, DISINFECTION_METHODS, AVAILABLE_FEATURES
)

_LOGGER = logging.getLogger(__name__)

def validate_ip_address(ip: str) -> bool:
    """Validiere IP-Adresse."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

async def fetch_api_data(
    session: aiohttp.ClientSession, api_url: str, auth: aiohttp.BasicAuth | None,
    use_ssl: bool, timeout: int, retries: int
) -> dict:
    """API-Daten mit Retry-Logik abrufen."""
    for attempt in range(retries):
        try:
            async with async_timeout.timeout(timeout):
                async with session.get(api_url, auth=auth, ssl=use_ssl) as response:
                    response.raise_for_status()
                    return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            if attempt + 1 == retries:
                _LOGGER.error("API-Fehler nach %d Versuchen: %s", retries, err)
                raise ValueError(f"API-Anfrage fehlgeschlagen: {err}")
            await asyncio.sleep(2 ** attempt)
    raise ValueError("Fehler nach allen Versuchen")

class VioletDeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Enhanced Config Flow für Violet Pool Controller mit modernem UI."""
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Options Flow zurückgeben."""
        return VioletOptionsFlowHandler(config_entry)

    def __init__(self) -> None:
        self._config_data: dict = {}

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """🌊 Schritt 1: Controller-Verbindung konfigurieren."""
        errors = {}
        if user_input:
            ip_address = user_input[CONF_API_URL]
            
            # Prüfung auf doppelte IP-Adressen
            for entry in self._async_current_entries():
                existing_ip = entry.data.get(CONF_API_URL) or entry.data.get("host") or entry.data.get("base_ip")
                if existing_ip == ip_address:
                    errors["base"] = "already_configured"
                    _LOGGER.warning("IP-Adresse %s bereits konfiguriert", ip_address)
                    break
            
            if not errors and not validate_ip_address(ip_address):
                errors[CONF_API_URL] = "invalid_ip_address"
            
            if not errors:
                self._config_data = {
                    CONF_API_URL: ip_address,
                    CONF_USE_SSL: user_input.get(CONF_USE_SSL, DEFAULT_USE_SSL),
                    CONF_DEVICE_NAME: user_input.get(CONF_DEVICE_NAME, "🌊 Violet Pool Controller"),
                    CONF_USERNAME: user_input.get(CONF_USERNAME, ""),
                    CONF_PASSWORD: user_input.get(CONF_PASSWORD, ""),
                    CONF_DEVICE_ID: int(user_input.get(CONF_DEVICE_ID, 1)),
                    CONF_POLLING_INTERVAL: int(user_input.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)),
                    CONF_TIMEOUT_DURATION: int(user_input.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION)),
                    CONF_RETRY_ATTEMPTS: int(user_input.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS)),
                }
                
                protocol = "https" if self._config_data[CONF_USE_SSL] else "http"
                api_url = f"{protocol}://{self._config_data[CONF_API_URL]}{API_READINGS}?ALL"
                
                await self.async_set_unique_id(f"{self._config_data[CONF_API_URL]}-{self._config_data[CONF_DEVICE_ID]}")
                self._abort_if_unique_id_configured()

                try:
                    session = aiohttp_client.async_get_clientsession(self.hass)
                    auth = aiohttp.BasicAuth(self._config_data[CONF_USERNAME], self._config_data[CONF_PASSWORD]) if self._config_data[CONF_USERNAME] else None
                    await fetch_api_data(
                        session, api_url, auth, self._config_data[CONF_USE_SSL],
                        self._config_data[CONF_TIMEOUT_DURATION], self._config_data[CONF_RETRY_ATTEMPTS]
                    )
                    return await self.async_step_pool_setup()
                except ValueError:
                    errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_URL, default="192.168.1.100", description="🌐 Controller IP-Adresse"): str,
                vol.Optional(CONF_USERNAME, default="", description="👤 Benutzername (optional)"): str,
                vol.Optional(CONF_PASSWORD, default="", description="🔐 Passwort (optional)"): str,
                vol.Required(CONF_USE_SSL, default=DEFAULT_USE_SSL, description="🔒 SSL/HTTPS verwenden"): bool,
                vol.Required(CONF_DEVICE_ID, default=1, description="🏷️ Geräte-ID"): vol.All(vol.Coerce(int), vol.Range(min=1)),
                vol.Required(CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL, description="⏱️ Abrufintervall (Sekunden)"): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
                vol.Required(CONF_TIMEOUT_DURATION, default=DEFAULT_TIMEOUT_DURATION, description="⏰ Timeout (Sekunden)"): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
                vol.Required(CONF_RETRY_ATTEMPTS, default=DEFAULT_RETRY_ATTEMPTS, description="🔄 Wiederholungsversuche"): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
                vol.Optional(CONF_DEVICE_NAME, default="🌊 Violet Pool Controller", description="📝 Gerätename"): str,
            }),
            errors=errors,
            description_placeholders={
                "step_icon": "🌐",
                "step_title": "Controller-Verbindung",
                "step_description": "Konfiguriere die Verbindung zu deinem Violet Pool Controller"
            }
        )

    async def async_step_pool_setup(self, user_input: dict | None = None) -> FlowResult:
        """🏊 Schritt 2: Pool-Konfiguration."""
        if user_input:
            self._config_data.update({
                CONF_POOL_SIZE: float(user_input[CONF_POOL_SIZE]),
                CONF_POOL_TYPE: user_input[CONF_POOL_TYPE],
                CONF_DISINFECTION_METHOD: user_input[CONF_DISINFECTION_METHOD],
            })
            return await self.async_step_feature_selection()

        # Enhanced pool type options mit Icons
        pool_type_options = {
            "outdoor": "🏖️ Freibad",
            "indoor": "🏠 Hallenbad", 
            "whirlpool": "🛁 Whirlpool/Spa",
            "natural": "🌿 Naturpool/Schwimmteich",
            "combination": "🔄 Kombination"
        }

        disinfection_options = {
            "chlorine": "🧪 Chlor (Flüssig/Tabletten)",
            "salt": "🧂 Salzelektrolyse",
            "bromine": "⚗️ Brom",
            "active_oxygen": "💧 Aktivsauerstoff/H₂O₂",
            "uv": "💡 UV-Desinfektion",
            "ozone": "🌀 Ozon-Desinfektion"
        }

        return self.async_show_form(
            step_id="pool_setup",
            data_schema=vol.Schema({
                vol.Required(CONF_POOL_SIZE, default=DEFAULT_POOL_SIZE, description="📏 Pool-Volumen in m³"): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=1000)),
                vol.Required(CONF_POOL_TYPE, default=DEFAULT_POOL_TYPE, description="🏊 Pool-Typ"): vol.In(pool_type_options),
                vol.Required(CONF_DISINFECTION_METHOD, default=DEFAULT_DISINFECTION_METHOD, description="🧼 Desinfektionsmethode"): vol.In(disinfection_options),
            }),
            description_placeholders={
                "device_name": self._config_data.get(CONF_DEVICE_NAME, "🌊 Violet Pool Controller"),
                "step_icon": "🏊",
                "step_title": "Pool-Konfiguration", 
                "step_description": f"Konfiguriere die Eigenschaften deines Pools für {self._config_data.get(CONF_DEVICE_NAME, 'den Controller')}"
            }
        )

    async def async_step_feature_selection(self, user_input: dict | None = None) -> FlowResult:
        """⚙️ Schritt 3: Feature-Auswahl mit visuellen Icons."""
        if user_input:
            # Enhanced feature processing mit besserer Visualisierung
            active_features = []
            for feature in AVAILABLE_FEATURES:
                checkbox_key = f"enable_{feature['id']}"
                if user_input.get(checkbox_key, feature["default"]):
                    active_features.append(feature["id"])
            
            self._config_data[CONF_ACTIVE_FEATURES] = active_features
            
            device_name = self._config_data.get(CONF_DEVICE_NAME, "🌊 Violet Pool Controller")
            device_id = self._config_data.get(CONF_DEVICE_ID, 1)
            pool_size = self._config_data.get(CONF_POOL_SIZE, DEFAULT_POOL_SIZE)
            
            title = f"{device_name} (ID {device_id}) • {pool_size}m³"
            
            return self.async_create_entry(title=title, data=self._config_data)

        # Enhanced feature descriptions mit Icons und Emojis
        enhanced_features = {
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

        # Build schema with enhanced descriptions
        schema_dict = {}
        for feature in AVAILABLE_FEATURES:
            feature_info = enhanced_features.get(feature["id"], {"icon": "⚙️", "name": feature["name"], "desc": ""})
            checkbox_key = f"enable_{feature['id']}"
            description = f"{feature_info['icon']} {feature_info['name']} - {feature_info['desc']}"
            
            schema_dict[vol.Optional(checkbox_key, default=feature["default"], description=description)] = bool

        return self.async_show_form(
            step_id="feature_selection",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={
                "device_name": self._config_data.get(CONF_DEVICE_NAME, "🌊 Violet Pool Controller"),
                "pool_size": str(self._config_data.get(CONF_POOL_SIZE, DEFAULT_POOL_SIZE)),
                "step_icon": "⚙️",
                "step_title": "Smart-Features aktivieren",
                "step_description": f"Wähle die gewünschten Automatisierungsfunktionen für deinen {self._config_data.get(CONF_POOL_SIZE, DEFAULT_POOL_SIZE)}m³ Pool"
            }
        )

class VioletOptionsFlowHandler(config_entries.OptionsFlow):
    """Enhanced Options Flow mit modernem UI Design."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialisiere Enhanced Options Flow."""
        self._config_entry = config_entry
        self.current_config = {**config_entry.data, **config_entry.options}

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        """🔧 Erweiterte Einstellungen verwalten."""
        if user_input:
            # Enhanced feature processing
            active_features = []
            for feature in AVAILABLE_FEATURES:
                checkbox_key = f"feature_{feature['id']}"
                if user_input.pop(checkbox_key, False):
                    active_features.append(feature["id"])
            
            user_input[CONF_ACTIVE_FEATURES] = active_features
            return self.async_create_entry(title="", data=user_input)

        # Enhanced pool type and disinfection options mit Icons
        pool_type_options = {
            "outdoor": "🏖️ Freibad",
            "indoor": "🏠 Hallenbad",
            "whirlpool": "🛁 Whirlpool/Spa", 
            "natural": "🌿 Naturpool/Schwimmteich",
            "combination": "🔄 Kombination"
        }

        disinfection_options = {
            "chlorine": "🧪 Chlor (Flüssig/Tabletten)",
            "salt": "🧂 Salzelektrolyse",
            "bromine": "⚗️ Brom",
            "active_oxygen": "💧 Aktivsauerstoff/H₂O₂",
            "uv": "💡 UV-Desinfektion", 
            "ozone": "🌀 Ozon-Desinfektion"
        }

        # Schema für erweiterte Optionen
        schema_dict = {
            vol.Optional(CONF_POLLING_INTERVAL, default=self.current_config.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL), description="⏱️ Datenabfrage alle X Sekunden"): 
                vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
            vol.Optional(CONF_TIMEOUT_DURATION, default=self.current_config.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION), description="⏰ Verbindungs-Timeout"): 
                vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
            vol.Optional(CONF_RETRY_ATTEMPTS, default=self.current_config.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS), description="🔄 Wiederholungsversuche bei Fehlern"): 
                vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
            vol.Optional(CONF_POOL_SIZE, default=self.current_config.get(CONF_POOL_SIZE, DEFAULT_POOL_SIZE), description="📏 Pool-Volumen in m³"): 
                vol.All(vol.Coerce(float), vol.Range(min=0.1, max=1000)),
            vol.Optional(CONF_POOL_TYPE, default=self.current_config.get(CONF_POOL_TYPE, DEFAULT_POOL_TYPE), description="🏊 Pool-Typ"): 
                vol.In(pool_type_options),
            vol.Optional(CONF_DISINFECTION_METHOD, default=self.current_config.get(CONF_DISINFECTION_METHOD, DEFAULT_DISINFECTION_METHOD), description="🧼 Desinfektionsmethode"): 
                vol.In(disinfection_options),
        }

        # Enhanced Feature-Checkboxen mit Icons
        enhanced_features = {
            "heating": "🔥 Heizungssteuerung",
            "solar": "☀️ Solarabsorber", 
            "ph_control": "🧪 pH-Automatik",
            "chlorine_control": "💧 Chlor-Management",
            "cover_control": "🪟 Abdeckungssteuerung",
            "backwash": "🔄 Rückspül-Automatik",
            "pv_surplus": "🔋 PV-Überschuss",
            "filter_control": "🌊 Filterpumpe",
            "water_level": "📏 Füllstand-Monitor",
            "water_refill": "🚰 Auto-Nachfüllung",
            "led_lighting": "💡 LED-Beleuchtung",
            "digital_inputs": "🔌 Digitale Eingänge",
            "extension_outputs": "🔗 Erweiterungsmodule",
        }

        current_features = self.current_config.get(CONF_ACTIVE_FEATURES, [])
        for feature in AVAILABLE_FEATURES:
            checkbox_key = f"feature_{feature['id']}"
            default_value = feature["id"] in current_features
            feature_name = enhanced_features.get(feature["id"], f"⚙️ {feature['name']}")
            
            schema_dict[vol.Optional(checkbox_key, default=default_value, description=feature_name)] = bool

        device_name = self._config_entry.data.get(CONF_DEVICE_NAME, "🌊 Violet Pool Controller")
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={
                "device_name": device_name,
                "step_icon": "🔧",
                "step_title": "Erweiterte Konfiguration",
                "step_description": f"Optimiere die Einstellungen für {device_name}"
            }
        )
