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
        """⚠️ Schritt 1: Rechtlicher Disclaimer und Nutzungsbedingungen."""
        if user_input is None:
            return await self.async_step_disclaimer()
        return await self.async_step_connection()

    async def async_step_disclaimer(self, user_input: dict | None = None) -> FlowResult:
        """⚠️ Disclaimer und Nutzungsbedingungen für Violet Pool Controller Integration."""
        errors = {}
        
        if user_input:
            agreement = user_input.get("agreement", False)
            if agreement:
                return await self.async_step_connection()
            else:
                return self.async_abort(reason="agreement_declined")
        
        # Disclaimer-Text direkt als Teil der Schema-Description
        disclaimer_text = """
⚠️ WICHTIGER RECHTLICHER HINWEIS ⚠️

NUTZUNG AUF EIGENE GEFAHR - VOLLSTÄNDIGER HAFTUNGSAUSSCHLUSS

🔴 ACHTUNG: Diese Integration steuert kritische Poolsysteme und Chemikaliendosierung!

SICHERHEITSHINWEISE UND HAFTUNGSAUSSCHLUSS:
• EIGENVERANTWORTUNG: Sie nutzen diese Software vollständig auf eigene Verantwortung
• CHEMISCHE GEFAHREN: Falsche Dosierung kann zu Gesundheitsschäden führen
• TECHNISCHE RISIKEN: Fehlfunktionen können Sachschäden verursachen
• SICHERHEITSÜBERSTEUERUNG: Diese Software kann Sicherheitsmechanismen übersteuern

FUNKTIONSUMFANG UND RISIKEN:
• Automatische Steuerung von Pumpen, Heizungen und elektrischen Geräten
• Dosierung von Chemikalien (pH-Regulatoren, Chlor, Flockmittel)
• Fernsteuerung kritischer Poolsysteme ohne lokale Aufsicht
• Steuerung von Abdeckungen und beweglichen Teilen

RECHTLICHER HAFTUNGSAUSSCHLUSS:
Der Entwickler übernimmt KEINERLEI HAFTUNG für:
• Personen- oder Sachschäden jeder Art
• Gesundheitsschäden durch falsche Wasserchemie
• Geräteschäden oder Betriebsausfälle
• Finanzielle Verluste oder Folgeschäden

NOTFALL-VERHALTEN:
• Immer manuellen Zugang zu allen Systemen sicherstellen
• Bei Störungen sofort alle automatischen Funktionen deaktivieren
• Chemische Notfallmaßnahmen bereithalten

Durch das Akzeptieren bestätigen Sie, dass Sie:
1. Diesen Disclaimer vollständig gelesen und verstanden haben
2. Alle Risiken akzeptieren und die volle Verantwortung übernehmen
3. Den Entwickler von jeder Haftung freistellen
4. Die Software auf eigene Gefahr verwenden

Bei Unsicherheit: INSTALLATION ABBRECHEN!
        """
        
        return self.async_show_form(
            step_id="disclaimer",
            data_schema=vol.Schema({
                vol.Required("agreement", default=False): bool,
            }),
            errors=errors,
            description_placeholders={
                "title": "⚠️ Rechtlicher Disclaimer - Violet Pool Controller",
                "subtitle": "Bitte lesen Sie die Nutzungsbedingungen sorgfältig durch",
                "disclaimer_text": disclaimer_text,
                "agreement_text": "✅ Ich habe den Disclaimer gelesen und stimme allen Bedingungen zu"
            }
        )

    async def async_step_connection(self, user_input: dict | None = None) -> FlowResult:
        """🌐 Schritt 2: Controller-Verbindung konfigurieren."""
        errors = {}
        if user_input:
            ip_address = user_input[CONF_API_URL]
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
            step_id="connection",
            data_schema=vol.Schema({
                vol.Required(CONF_API_URL, default="192.168.1.100"): str,
                vol.Optional(CONF_USERNAME, default=""): str,
                vol.Optional(CONF_PASSWORD, default=""): str,
                vol.Required(CONF_USE_SSL, default=DEFAULT_USE_SSL): bool,
                vol.Required(CONF_DEVICE_ID, default=1): vol.All(vol.Coerce(int), vol.Range(min=1)),
                vol.Required(CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
                vol.Required(CONF_TIMEOUT_DURATION, default=DEFAULT_TIMEOUT_DURATION): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
                vol.Required(CONF_RETRY_ATTEMPTS, default=DEFAULT_RETRY_ATTEMPTS): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
                vol.Optional(CONF_DEVICE_NAME, default="🌊 Violet Pool Controller"): str,
            }),
            errors=errors,
            description_placeholders={
                "step_icon": "🌐",
                "step_title": "Controller-Verbindung",
                "step_description": "Konfiguriere die Verbindung zu deinem Violet Pool Controller",
                "api_url_desc": "🌐 Controller IP-Adresse",
                "username_desc": "👤 Benutzername (optional)",
                "password_desc": "🔐 Passwort (optional)", 
                "use_ssl_desc": "🔒 SSL/HTTPS verwenden",
                "device_id_desc": "🏷️ Geräte-ID",
                "polling_desc": "⏱️ Abrufintervall (Sekunden)",
                "timeout_desc": "⏰ Timeout (Sekunden)",
                "retry_desc": "🔄 Wiederholungsversuche",
                "device_name_desc": "📝 Gerätename"
            }
        )

    async def async_step_pool_setup(self, user_input: dict | None = None) -> FlowResult:
        """🏊 Schritt 3: Pool-Konfiguration."""
        if user_input:
            self._config_data.update({
                CONF_POOL_SIZE: float(user_input[CONF_POOL_SIZE]),
                CONF_POOL_TYPE: user_input[CONF_POOL_TYPE],
                CONF_DISINFECTION_METHOD: user_input[CONF_DISINFECTION_METHOD],
            })
            return await self.async_step_feature_selection()
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
                vol.Required(CONF_POOL_SIZE, default=DEFAULT_POOL_SIZE): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=1000)),
                vol.Required(CONF_POOL_TYPE, default=DEFAULT_POOL_TYPE): vol.In(pool_type_options),
                vol.Required(CONF_DISINFECTION_METHOD, default=DEFAULT_DISINFECTION_METHOD): vol.In(disinfection_options),
            }),
            description_placeholders={
                "device_name": self._config_data.get(CONF_DEVICE_NAME, "🌊 Violet Pool Controller"),
                "step_icon": "🏊",
                "step_title": "Pool-Konfiguration",
                "step_description": f"Konfiguriere die Eigenschaften deines Pools für {self._config_data.get(CONF_DEVICE_NAME, 'den Controller')}",
                "pool_size_desc": "📏 Pool-Volumen in m³",
                "pool_type_desc": "🏊 Pool-Typ",
                "disinfection_desc": "🧼 Desinfektionsmethode"
            }
        )

    async def async_step_feature_selection(self, user_input: dict | None = None) -> FlowResult:
        """⚙️ Schritt 4: Feature-Auswahl mit visuellen Icons."""
        if user_input:
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
        schema_dict = {}
        for feature in AVAILABLE_FEATURES:
            feature_info = enhanced_features.get(feature["id"], {"icon": "⚙️", "name": feature["name"], "desc": ""})
            checkbox_key = f"enable_{feature['id']}"
            schema_dict[vol.Optional(checkbox_key, default=feature["default"])] = bool
        return self.async_show_form(
            step_id="feature_selection",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={
                "device_name": self._config_data.get(CONF_DEVICE_NAME, "🌊 Violet Pool Controller"),
                "pool_size": str(self._config_data.get(CONF_POOL_SIZE, DEFAULT_POOL_SIZE)),
                "step_icon": "⚙️",
                "step_title": "Smart-Features aktivieren",
                "step_description": f"Wähle die gewünschten Automatisierungsfunktionen für deinen {self._config_data.get(CONF_POOL_SIZE, DEFAULT_POOL_SIZE)}m³ Pool",
                "features_info": enhanced_features
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
            active_features = []
            for feature in AVAILABLE_FEATURES:
                checkbox_key = f"feature_{feature['id']}"
                if user_input.pop(checkbox_key, False):
                    active_features.append(feature["id"])
            user_input[CONF_ACTIVE_FEATURES] = active_features
            return self.async_create_entry(title="", data=user_input)
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
        schema_dict = {
            vol.Optional(CONF_POLLING_INTERVAL, default=self.current_config.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)):
                vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
            vol.Optional(CONF_TIMEOUT_DURATION, default=self.current_config.get(CONF_TIMEOUT_DURATION, DEFAULT_TIMEOUT_DURATION)):
                vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
            vol.Optional(CONF_RETRY_ATTEMPTS, default=self.current_config.get(CONF_RETRY_ATTEMPTS, DEFAULT_RETRY_ATTEMPTS)):
                vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
            vol.Optional(CONF_POOL_SIZE, default=self.current_config.get(CONF_POOL_SIZE, DEFAULT_POOL_SIZE)):
                vol.All(vol.Coerce(float), vol.Range(min=0.1, max=1000)),
            vol.Optional(CONF_POOL_TYPE, default=self.current_config.get(CONF_POOL_TYPE, DEFAULT_POOL_TYPE)):
                vol.In(pool_type_options),
            vol.Optional(CONF_DISINFECTION_METHOD, default=self.current_config.get(CONF_DISINFECTION_METHOD, DEFAULT_DISINFECTION_METHOD)):
                vol.In(disinfection_options),
        }
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
            schema_dict[vol.Optional(checkbox_key, default=default_value)] = bool
        device_name = self._config_entry.data.get(CONF_DEVICE_NAME, "🌊 Violet Pool Controller")
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={
                "device_name": device_name,
                "step_icon": "🔧",
                "step_title": "Erweiterte Konfiguration",
                "step_description": f"Optimiere die Einstellungen für {device_name}",
                "polling_desc": "⏱️ Datenabfrage alle X Sekunden",
                "timeout_desc": "⏰ Verbindungs-Timeout",
                "retry_desc": "🔄 Wiederholungsversuche bei Fehlern",
                "pool_size_desc": "📏 Pool-Volumen in m³",
                "pool_type_desc": "🏊 Pool-Typ",
                "disinfection_desc": "🧼 Desinfektionsmethode",
                "features_info": enhanced_features
            }
        )