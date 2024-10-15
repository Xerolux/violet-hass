import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
import async_timeout
import aiohttp
import asyncio
from typing import Any, Dict

from .const import (
    DOMAIN, 
    CONF_API_URL, 
    CONF_POLLING_INTERVAL, 
    CONF_USE_SSL, 
    CONF_DEVICE_ID,
    CONF_USERNAME, 
    CONF_PASSWORD,
    DEFAULT_POLLING_INTERVAL, 
    DEFAULT_USE_SSL,
    API_READINGS,
    API_SET_FUNCTION_MANUALLY
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Violet Pool Controller from a config entry."""
    
    # Retrieve configuration data from the config entry
    config = {
        "ip_address": entry.data[CONF_API_URL],
        "polling_interval": entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL),
        "use_ssl": entry.data.get(CONF_USE_SSL, DEFAULT_USE_SSL),
        "device_id": entry.data.get(CONF_DEVICE_ID, 1),
        "username": entry.data.get(CONF_USERNAME),
        "password": entry.data.get(CONF_PASSWORD)
    }

    # Log configuration data
    _LOGGER.info(f"Setting up Violet Pool Controller with config: {config}")

    # Get a shared aiohttp session
    session = aiohttp_client.async_get_clientsession(hass)

    # Create a coordinator for data updates
    coordinator = VioletDataUpdateCoordinator(
        hass,
        config=config,
        session=session,
    )

    # Log before first data fetch
    _LOGGER.debug("First data fetch for Violet Pool Controller is being performed")

    try:
        # Ensure the first data fetch happens during setup
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error(f"First data fetch failed: {err}")
        return False

    # Store the coordinator in hass.data for access by platform files
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register custom services for turning switches on/off/auto
    async def handle_turn_auto_service(call):
        """Handle the custom turn_auto service."""
        entity_id = call.data.get("entity_id")
        duration = call.data.get("duration", 0)
        last_value = call.data.get("last_value", 0)

        _LOGGER.info(f"Setting {entity_id} to AUTO mode with duration {duration} seconds and last value {last_value}")

        entity = hass.states.get(entity_id)
        if entity:
            await entity.async_turn_auto(duration=duration, last_value=last_value)
        else:
            _LOGGER.error(f"Entity {entity_id} not found")

    async def handle_turn_on_service(call):
        """Handle the custom turn_on service."""
        entity_id = call.data.get("entity_id")
        duration = call.data.get("duration", 0)
        last_value = call.data.get("last_value", 0)

        _LOGGER.info(f"Turning {entity_id} ON with duration {duration} seconds and last value {last_value}")

        entity = hass.states.get(entity_id)
        if entity:
            await entity.async_turn_on(duration=duration, last_value=last_value)
        else:
            _LOGGER.error(f"Entity {entity_id} not found")

    async def handle_turn_off_service(call):
        """Handle the custom turn_off service."""
        entity_id = call.data.get("entity_id")

        _LOGGER.info(f"Turning {entity_id} OFF")

        entity = hass.states.get(entity_id)
        if entity:
            await entity.async_turn_off()
        else:
            _LOGGER.error(f"Entity {entity_id} not found")

    # Register the services
    hass.services.async_register(DOMAIN, "turn_auto", handle_turn_auto_service)
    hass.services.async_register(DOMAIN, "turn_on", handle_turn_on_service)
    hass.services.async_register(DOMAIN, "turn_off", handle_turn_off_service)

    # Forward setup to platforms (e.g., switch, sensor, binary sensor)
    await hass.config_entries.async_forward_entry_setups(entry, ["switch", "sensor", "binary_sensor"])

    _LOGGER.info("Violet Pool Controller setup completed successfully")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["switch", "sensor", "binary_sensor"]
    )

    # Remove the coordinator from hass.data
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    _LOGGER.info(f"Violet Pool Controller (device {entry.entry_id}) unloaded successfully")
    return unload_ok


class VioletDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Violet Pool Controller data and dynamically adding new entities."""

    def __init__(self, hass: HomeAssistant, config: Dict[str, Any], session: aiohttp.ClientSession) -> None:
        """Initialize the coordinator."""
        self.ip_address: str = config["ip_address"]
        self.username: str = config["username"]
        self.password: str = config["password"]
        self.session: aiohttp.ClientSession = session
        self.use_ssl: bool = config["use_ssl"]
        self.device_id: int = config["device_id"]

        self._existing_entities: Dict[str, Any] = {}  # Track existing entities and their states

        _LOGGER.info(f"Initializing data coordinator for device {self.device_id} (IP: {self.ip_address}, SSL: {self.use_ssl})")

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.device_id}",
            update_interval=timedelta(seconds=config["polling_interval"]),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from the Violet Pool Controller API and detect new or changed entities."""
        retries = 3
        for attempt in range(retries):
            try:
                protocol = "https" if self.use_ssl else "http"
                url = f"{protocol}://{self.ip_address}{API_READINGS}"
                _LOGGER.debug(f"Fetching data from: {url}")

                if self.username and self.password:
                    auth = aiohttp.BasicAuth(self.username, self.password)
                else:
                    auth = None

                async with async_timeout.timeout(10):
                    async with self.session.get(url, auth=auth, ssl=self.use_ssl) as response:
                        _LOGGER.debug(f"Status Code: {response.status}")
                        _LOGGER.debug(f"Response Headers: {response.headers}")
                        response.raise_for_status()
                        data = await response.json()
                        _LOGGER.debug(f"Data received: {data}")
                        
                        # Check for new entities or changes
                        self._detect_new_or_changed_entities(data)

                        return data

            except aiohttp.ClientError as client_err:
                _LOGGER.warning(f"Attempt {attempt + 1}/{retries} - HTTP error while fetching data: {client_err}")
                if attempt + 1 == retries:
                    raise UpdateFailed(f"HTTP error after {retries} attempts (Device ID: {self.device_id}, URL: {url}): {client_err}")
            except asyncio.TimeoutError:
                _LOGGER.warning(f"Attempt {attempt + 1}/{retries} - Timeout while fetching data from {self.ip_address}")
                if attempt + 1 == retries:
                    raise UpdateFailed(f"Timeout after {retries} attempts (Device ID: {self.device_id}, IP: {self.ip_address})")
            except Exception as err:
                _LOGGER.error(f"Unexpected error while fetching data from {self.ip_address}: {err}")
                raise UpdateFailed(f"Unexpected error (Device ID: {self.device_id}, IP: {self.ip_address}): {err}")

            await asyncio.sleep(2 ** attempt)  # Exponential backoff on retries

    def _detect_new_or_changed_entities(self, data: Dict[str, Any]) -> None:
        """Detect and add new or changed entities based on the received data."""
        new_entities = set(data.keys()) - set(self._existing_entities.keys())
        changed_entities = {
            entity: data[entity]
            for entity in self._existing_entities
            if self._existing_entities[entity] != data[entity]
        }

        if new_entities:
            _LOGGER.info(f"New entities detected: {new_entities}")
            for entity in new_entities:
                self._create_new_entity(entity, data[entity])
            self._existing_entities.update({entity: data[entity] for entity in new_entities})

        if changed_entities:
            _LOGGER.info(f"Changed entities detected: {changed_entities}")
            for entity, new_value in changed_entities.items():
                self._update_existing_entity(entity, new_value)
            self._existing_entities.update(changed_entities)

    def _create_new_entity(self, entity: str, value: Any) -> None:
        """Create and register a new entity dynamically."""
        _LOGGER.info(f"Creating new entity: {entity} with value: {value}")
        # Dynamically create new entity and forward to the appropriate platform (e.g., sensor, switch, etc.)
        # This would involve Home Assistant platform specific logic.
        # You would register the entity as a new sensor, switch, etc., using hass.helpers.entity_component.async_add_entities

    def _update_existing_entity(self, entity: str, new_value: Any) -> None:
        """Update the state of an existing entity."""
        _LOGGER.info(f"Updating entity: {entity} to new value: {new_value}")
        # Dynamically update the entity's state in Home Assistant
        # This could trigger a state update for the entity in Home Assistant

