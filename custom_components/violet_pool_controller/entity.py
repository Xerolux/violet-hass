import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.helpers.entity import EntityDescription
from .const import DOMAIN, CONF_DEVICE_NAME, CONF_API_URL, CONF_POLLING_INTERVAL


class VioletPoolControllerEntity(CoordinatorEntity):
    """Basisklasse für eine Violet Pool Controller Entität."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        config_entry: ConfigEntry,
        entity_description: EntityDescription,
    ) -> None:
        """Initialisiere die Entität."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.entity_description = entity_description
        self._name = f"{config_entry.data.get(CONF_DEVICE_NAME)} {entity_description.name}"
        # Verwende entry_id zur Erzeugung einer eindeutigen ID (wichtig bei mehreren Geräten)
        self._unique_id = f"{config_entry.entry_id}_{entity_description.key}"
        self._state = None
        self._available = True  # Initial als verfügbar annehmen
        self.api_url = config_entry.data.get(CONF_API_URL)
        self.polling_interval = config_entry.data.get(CONF_POLLING_INTERVAL)
        self._logger = logging.getLogger(f"{DOMAIN}.{self._unique_id}")

        self._logger.info("Initialisiert %s mit eindeutiger ID: %s", self._name, self._unique_id)

        # Geräteinformationen setzen – entry_id als eindeutiger Bezeichner verwenden
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"{config_entry.data.get(CONF_DEVICE_NAME)} ({config_entry.data.get(CONF_API_URL)})",  # IP im Gerätenamen
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Model X",  # Falls möglich dynamisch abrufbar machen
            "sw_version": self.coordinator.data.get("fw", "Unknown"),
            "configuration_url": f"http://{config_entry.data.get(CONF_API_URL)}",
        }

    @property
    def name(self) -> str:
        """Gibt den Namen der Entität zurück."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Gibt die eindeutige ID der Entität zurück."""
        return self._unique_id

    @property
    def available(self) -> bool:
        """Gibt an, ob die Entität verfügbar ist."""
        return self._available and self.coordinator.last_update_success

    @property
    def state(self):
        """Gibt den Zustand der Entität zurück."""
        return self._state

    @property
    def extra_state_attributes(self) -> dict:
        """Gibt zusätzliche Zustandsattribute zurück."""
        return {
            "polling_interval": self.polling_interval,
            "api_url": self.api_url,
            "last_updated": self.coordinator.last_update_success_time,
        }

    async def async_update(self) -> None:
        """Aktualisiert den Zustand der Entität anhand der Daten des Coordinators."""
        try:
            if self.coordinator.data:
                self._update_state(self.coordinator.data)
                self._available = True
                self._logger.debug("Aktualisiert %s Zustand: %s", self._name, self._state)
            else:
                self._available = False
                self._logger.warning("Keine Daten vom Coordinator für %s verfügbar.", self._name)
        except Exception as e:
            self._available = False
            self._logger.error("Unerwarteter Fehler bei der Aktualisierung von %s: %s", self._name, e)

    def _update_state(self, data: dict) -> None:
        """Aktualisiert den Zustand der Entität anhand der Coordinator-Daten."""
        try:
            new_state = data.get(self.entity_description.key)
            if new_state is not None:
                self._state = new_state
                self._logger.debug("Neuer Zustand für %s: %s", self.name, self._state)
            else:
                self._logger.warning(
                    "Schlüssel %s nicht gefunden oder ohne Wert in den Daten.",
                    self.entity_description.key,
                )
                self._available = False
        except KeyError:
            self._logger.error("Schlüssel %s nicht in der Antwort enthalten.", self.entity_description.key)
            self._available = False
