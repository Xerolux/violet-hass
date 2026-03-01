
"""Cover platform for Violet Pool Controller."""
from __future__ import annotations

import logging

from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntity,
    CoverEntityDescription,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import VioletPoolAPIError
from .const import (
    ACTION_PUSH,
    CONF_ACTIVE_FEATURES,
    COVER_FUNCTIONS,
    COVER_STATE_MAP,
    DOMAIN,
)
from .device import VioletPoolDataUpdateCoordinator
from .entity import VioletPoolControllerEntity

_LOGGER = logging.getLogger(__name__)

# Coordinator-based platforms; HA should not throttle entity state writes
PARALLEL_UPDATES = 0


class VioletCover(VioletPoolControllerEntity, CoverEntity):
    """Representation of the pool cover."""

    _attr_device_class = CoverDeviceClass.SHUTTER
    _attr_supported_features = (
        CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
    )

    def __init__(
        self, coordinator: VioletPoolDataUpdateCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialisiert die Cover-Entity."""
        entity_description = CoverEntityDescription(
            key="COVER_STATE",
            name="Abdeckung",
            icon="mdi:window-shutter",
        )
        super().__init__(coordinator, config_entry, entity_description)
        self._last_action: str | None = None
        _LOGGER.debug("Cover-Entity initialisiert für %s", config_entry.title)

    @property
    def is_closed(self) -> bool:
        """Gibt True zurück, wenn das Cover geschlossen ist."""
        state = COVER_STATE_MAP.get(self.get_str_value("COVER_STATE", "") or "", "")
        return state == "closed"

    @property
    def is_opening(self) -> bool:
        """Gibt True zurück, wenn das Cover öffnet."""
        state = COVER_STATE_MAP.get(self.get_str_value("COVER_STATE", "") or "", "")
        direction = self.get_str_value("LAST_MOVING_DIRECTION", "") or ""

        # Cover ist am Öffnen wenn:
        # 1. State explizit "opening" ist
        # 2. Letzte Aktion war OPEN und Cover ist noch nicht offen
        # 3. Bewegungsrichtung ist OPEN und Cover ist in Bewegung
        return (
            state == "opening"
            or (self._last_action == "OPEN" and not self.is_open)
            or (direction == "OPEN" and not self.is_closed and not self.is_open)
        )

    @property
    def is_closing(self) -> bool:
        """Gibt True zurück, wenn das Cover schließt."""
        state = COVER_STATE_MAP.get(self.get_str_value("COVER_STATE", "") or "", "")
        direction = self.get_str_value("LAST_MOVING_DIRECTION", "") or ""

        # Cover ist am Schließen wenn:
        # 1. State explizit "closing" ist
        # 2. Letzte Aktion war CLOSE und Cover ist noch nicht geschlossen
        # 3. Bewegungsrichtung ist CLOSE und Cover ist in Bewegung
        return (
            state == "closing"
            or (self._last_action == "CLOSE" and not self.is_closed)
            or (direction == "CLOSE" and not self.is_closed and not self.is_open)
        )

    @property
    def is_open(self) -> bool:
        """Gibt True zurück, wenn das Cover geöffnet ist."""
        state = COVER_STATE_MAP.get(self.get_str_value("COVER_STATE", "") or "", "")
        return state == "open"

    async def async_open_cover(self, **kwargs) -> None:
        """Öffnet das Cover."""
        _LOGGER.info("Öffne Pool-Abdeckung")
        await self._send_cover_command("OPEN")

    async def async_close_cover(self, **kwargs) -> None:
        """Schließt das Cover."""
        _LOGGER.info("Schließe Pool-Abdeckung")
        await self._send_cover_command("CLOSE")

    async def async_stop_cover(self, **kwargs) -> None:
        """Stoppt das Cover."""
        _LOGGER.info("Stoppe Pool-Abdeckung")
        await self._send_cover_command("STOP")

    async def _send_cover_command(self, action: str) -> None:
        """
        Sendet Cover-Befehl an den Controller.

        Args:
            action: Aktion (OPEN, CLOSE, STOP)

        Raises:
            HomeAssistantError: Bei API-Fehlern
        """
        cover_api_key = COVER_FUNCTIONS.get(action.upper())

        if not cover_api_key:
            _LOGGER.error("Ungültige Cover-Aktion: %s", action)
            raise HomeAssistantError(f"Ungültige Aktion: {action}")

        self._last_action = action

        try:
            _LOGGER.debug("Sende Cover-Befehl: %s", action)

            result = await self.device.api.set_switch_state(
                key=cover_api_key, action=ACTION_PUSH
            )

            if result.get("success") is True:
                _LOGGER.info("Cover-Befehl '%s' erfolgreich gesendet", action)
            else:
                error_msg = result.get("response", result)
                _LOGGER.warning(
                    "Cover-Befehl '%s' möglicherweise fehlgeschlagen: %s",
                    action,
                    error_msg,
                )

            # Aktualisiere Daten nach Befehl
            await self.coordinator.async_request_refresh()

        except VioletPoolAPIError as err:
            _LOGGER.error("API-Fehler bei Cover-Befehl '%s': %s", action, err)
            raise HomeAssistantError(
                f"Cover-Aktion '{action}' fehlgeschlagen: {err}"
            ) from err

        except Exception as err:
            _LOGGER.exception(
                "Unerwarteter Fehler bei Cover-Befehl '%s': %s", action, err
            )
            raise HomeAssistantError(
                f"Unerwarteter Fehler bei Aktion '{action}': {err}"
            ) from err


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Richtet Cover-Entity ein."""
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    # Features aus Options oder Data holen
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )

    # Prüfe ob Cover-Control aktiviert ist und Daten verfügbar sind
    if "cover_control" in active_features:
        # None-Check für coordinator.data
        if coordinator.data is None:
            _LOGGER.warning(
                "Cover-Control aktiviert, aber Coordinator-Daten sind None. "
                "Cover wird nicht erstellt."
            )
            return

        if "COVER_STATE" in coordinator.data:
            async_add_entities([VioletCover(coordinator, config_entry)])
            _LOGGER.info("Cover-Entity für '%s' hinzugefügt", config_entry.title)
        else:
            _LOGGER.info(
                "Cover-Control aktiviert, aber Controller liefert keine COVER_STATE Daten. "
                "Dies ist normal wenn keine Abdeckung konfiguriert ist."
            )
    else:
        _LOGGER.debug("Cover-Control nicht aktiviert")
