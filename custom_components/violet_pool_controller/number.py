"""Number Integration für den Violet Pool Controller - WITH INPUT SANITIZATION."""

import logging

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import VioletPoolAPIError
from .const import CONF_ACTIVE_FEATURES, DOMAIN, SETPOINT_DEFINITIONS
from .device import VioletPoolDataUpdateCoordinator
from .entity import VioletPoolControllerEntity
from .utils_sanitizer import InputSanitizer

_LOGGER = logging.getLogger(__name__)


class VioletNumber(VioletPoolControllerEntity, NumberEntity):
    """Representation of a Violet Pool number entity (setpoint)."""

    entity_description: NumberEntityDescription

    def __init__(
        self,
        coordinator: VioletPoolDataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: NumberEntityDescription,
        setpoint_config: dict,
    ) -> None:
        """
        Initialize the number entity.

        Args:
            coordinator: The update coordinator.
            config_entry: The config entry.
            description: The entity description.
            setpoint_config: The setpoint configuration.
        """
        super().__init__(coordinator, config_entry, description)

        # Min/Max/Step Werte setzen
        self._attr_native_min_value = setpoint_config["min_value"]
        self._attr_native_max_value = setpoint_config["max_value"]
        self._attr_native_step = setpoint_config["step"]

        # Zusätzliche Attribute speichern
        self._setpoint_fields = setpoint_config["setpoint_fields"]
        self._indicator_fields = setpoint_config["indicator_fields"]
        self._default_value = setpoint_config["default_value"]
        self._api_key = setpoint_config["api_key"]

        # ✅ FIXED: Lokale Cache-Variable für thread-sichere optimistische Updates
        self._optimistic_value: float | None = None

        _LOGGER.info(
            "Number-Entity initialisiert: %s (Range: %.1f-%.1f, Step: %.1f, API-Key: %s)",
            description.name,
            self._attr_native_min_value,
            self._attr_native_max_value,
            self._attr_native_step,
            self._api_key,
        )

    @property
    def native_value(self) -> float | None:
        """
        Return the current setpoint value.

        Tries to read the value from various possible fields.
        If no value is found, returns the default value.

        Returns:
            The current setpoint or default value.
        """
        # ✅ FIXED: Prüfe zuerst optimistischen Cache
        if self._optimistic_value is not None:
            return self._optimistic_value

        # Spezialfall: Pumpengeschwindigkeit - aktive Stufe aus PUMP_RPM_{i} ermitteln
        # PUMP_RPM_{i} liefert Statuscodes (0-6); Werte 1,2,3,4 = Ausgang EIN
        if self._api_key == "PUMP_SPEED":
            for level in range(1, 4):  # Stufen 1 (Eco), 2 (Normal), 3 (Boost)
                rpm_val = self.get_value(f"PUMP_RPM_{level}")
                if rpm_val is not None:
                    try:
                        if int(rpm_val) in (1, 2, 3, 4):  # Statuscode = EIN
                            _LOGGER.debug(
                                "Pumpengeschwindigkeit aktiv: Stufe %d (PUMP_RPM_%d=%s)",
                                level,
                                level,
                                rpm_val,
                            )
                            return float(level)
                    except (ValueError, TypeError):
                        pass

        # Versuche Sollwert aus den konfigurierten Feldern zu lesen
        if self._setpoint_fields:
            for field in self._setpoint_fields:
                value = self.get_float_value(field)
                if value is not None:
                    _LOGGER.debug(
                        "Sollwert für %s aus Feld '%s': %.2f",
                        self.entity_description.name,
                        field,
                        value,
                    )
                    return value

        # Fallback auf Standardwert
        _LOGGER.debug(
            "Kein Sollwert gefunden für %s, verwende default: %.2f",
            self.entity_description.name,
            self._default_value,
        )
        return float(self._default_value)

    @property
    def available(self) -> bool:
        """
        Check if the entity is available.

        Entity is available if at least one indicator field
        is present in the coordinator data.

        Returns:
            True if available, False otherwise.
        """
        # None-Check für coordinator.data
        if self.coordinator.data is None:
            return False

        # Prüfe ob Indikator-Felder verfügbar sind
        if self._indicator_fields:
            for field in self._indicator_fields:
                if field in self.coordinator.data:
                    _LOGGER.debug(
                        "Entity %s verfügbar (Indikator '%s' gefunden)",
                        self.entity_description.name,
                        field,
                    )
                    return super().available

            _LOGGER.debug(
                "Entity %s nicht verfügbar (keine Indikator-Felder gefunden)",
                self.entity_description.name,
            )

        return super().available

    async def async_set_native_value(self, value: float) -> None:
        """
        Set a new setpoint value.

        Uses the corresponding API method based on the setpoint type.

        Args:
            value: The new setpoint value.

        Raises:
            HomeAssistantError: If the API call fails.
        """
        if not self._api_key:
            _LOGGER.error(
                "Kein API-Key für %s definiert - kann Sollwert nicht setzen",
                self.entity_description.name,
            )
            raise HomeAssistantError(
                f"Kein API-Key für {self.entity_description.name} definiert"
            )

        # ✅ INPUT SANITIZATION: Validiere und sanitize den Wert basierend auf Typ
        try:
            if self._api_key == "pH":
                sanitized_value = InputSanitizer.validate_ph_value(value)
            elif self._api_key == "ORP":
                sanitized_value = float(InputSanitizer.validate_orp_value(value))
            elif self._api_key == "MinChlorine":
                sanitized_value = InputSanitizer.validate_chlorine_level(value)
            else:
                # Generic float validation mit Range
                sanitized_value = InputSanitizer.sanitize_float(
                    value,
                    min_value=self._attr_native_min_value,
                    max_value=self._attr_native_max_value,
                    precision=1 if self._attr_native_step >= 0.1 else 2,
                )
        except (ValueError, TypeError) as err:
            _LOGGER.error(
                "Input Sanitization fehlgeschlagen für %s (Wert: %s): %s",
                self.entity_description.name,
                value,
                err,
            )
            raise HomeAssistantError(f"Ungültiger Wert: {err}") from err

        # Validiere finalen Wertebereich (zusätzliche Sicherheit)
        if (
            sanitized_value < self._attr_native_min_value
            or sanitized_value > self._attr_native_max_value
        ):
            _LOGGER.error(
                "Wert %.2f außerhalb des gültigen Bereichs (%.1f-%.1f) für %s",
                sanitized_value,
                self._attr_native_min_value,
                self._attr_native_max_value,
                self.entity_description.name,
            )
            raise HomeAssistantError(
                f"Wert {sanitized_value} außerhalb des gültigen Bereichs "
                f"({self._attr_native_min_value}-{self._attr_native_max_value})"
            )

        try:
            unit = self.entity_description.native_unit_of_measurement or ""
            _LOGGER.info(
                "Setze %s auf %.2f%s (vorher: %.2f%s) [sanitized: %.2f]",
                self.entity_description.name,
                value,
                unit,
                self.native_value or 0,
                unit,
                sanitized_value,
            )

            # Wähle die passende API-Methode basierend auf dem API-Key
            api_key = self._api_key

            if api_key == "pH":
                _LOGGER.debug(
                    "Verwende set_ph_target für pH-Wert (sanitized: %.2f)",
                    sanitized_value,
                )
                result = await self.device.api.set_ph_target(sanitized_value)
            elif api_key == "ORP":
                _LOGGER.debug(
                    "Verwende set_orp_target für ORP-Wert (sanitized: %.1f)",
                    sanitized_value,
                )
                # ORP values can be decimal (e.g., 650.5), preserve precision
                result = await self.device.api.set_orp_target(sanitized_value)
            elif api_key == "MinChlorine":
                _LOGGER.debug(
                    "Verwende set_min_chlorine_level für Chlor-Wert (sanitized: %.2f)",
                    sanitized_value,
                )
                result = await self.device.api.set_min_chlorine_level(sanitized_value)
            elif api_key == "PUMP_SPEED":
                _LOGGER.debug(
                    "Verwende set_pump_speed für Pumpengeschwindigkeit (sanitized: %d)",
                    int(sanitized_value),
                )
                result = await self.device.api.set_pump_speed(int(sanitized_value))
            elif api_key in ("HEATER_TARGET_TEMP", "SOLAR_TARGET_TEMP"):
                _LOGGER.debug(
                    "Verwende set_device_temperature für %s (sanitized: %.1f)",
                    api_key.replace("_TARGET_TEMP", ""),
                    sanitized_value,
                )
                climate_key = api_key.replace("_TARGET_TEMP", "")
                result = await self.device.api.set_device_temperature(
                    climate_key, sanitized_value
                )
            elif api_key.endswith("_TOTAL_CAN_AMOUNT_ML"):
                # Dosing canister volume parameters
                _LOGGER.debug(
                    "Verwende set_dosing_parameters für %s (sanitized: %.0f ml)",
                    api_key,
                    sanitized_value,
                )
                result = await self.device.api.set_dosing_parameters(
                    {api_key: int(sanitized_value)}
                )
            else:
                _LOGGER.debug(
                    "Verwende set_target_value für %s (sanitized: %.2f)",
                    api_key,
                    sanitized_value,
                )
                result = await self.device.api.set_target_value(
                    api_key, sanitized_value
                )

            # Prüfe Ergebnis
            if result.get("success") is True:
                _LOGGER.info(
                    "%s erfolgreich auf %.2f%s gesetzt",
                    self.entity_description.name,
                    value,
                    unit,
                )

                # ✅ FIXED: Optimistisches Update mit lokalem Cache (thread-safe)
                self._optimistic_value = value
                _LOGGER.debug(
                    "Optimistischer Cache für '%s' auf %.2f gesetzt",
                    self.entity_description.name,
                    value,
                )

                # State sofort aktualisieren
                self.async_write_ha_state()

                # Daten vom Controller neu abrufen und dann Cache zurücksetzen
                await self.coordinator.async_request_refresh()

                # ✅ FIXED: Cache nach erfolgreichem Refresh zurücksetzen
                self._optimistic_value = None
                _LOGGER.debug(
                    "Optimistischer Cache für '%s' zurückgesetzt",
                    self.entity_description.name,
                )
            else:
                error_msg = result.get("response", result)
                _LOGGER.warning(
                    "%s setzen möglicherweise fehlgeschlagen: %s",
                    self.entity_description.name,
                    error_msg,
                )
                raise HomeAssistantError(f"Sollwert setzen fehlgeschlagen: {error_msg}")

        except VioletPoolAPIError as err:
            _LOGGER.error(
                "API-Fehler beim Setzen von %s auf %.2f: %s",
                self.entity_description.name,
                value,
                err,
            )
            raise HomeAssistantError(f"Sollwert setzen fehlgeschlagen: {err}") from err

        except Exception as err:
            _LOGGER.exception(
                "Unerwarteter Fehler beim Setzen von %s auf %.2f: %s",
                self.entity_description.name,
                value,
                err,
            )
            raise HomeAssistantError(f"Unerwarteter Fehler: {err}") from err


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Set up number entities for the config entry.

    Creates number entities for all configured setpoints that are
    included in the active features and whose indicator fields are available.

    Args:
        hass: The Home Assistant instance.
        config_entry: The config entry.
        async_add_entities: Callback to add entities.
    """
    coordinator: VioletPoolDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    # Aktive Features aus Options oder Data holen
    active_features = config_entry.options.get(
        CONF_ACTIVE_FEATURES, config_entry.data.get(CONF_ACTIVE_FEATURES, [])
    )

    _LOGGER.debug(
        "Setup Number-Entities für '%s' mit aktiven Features: %s",
        config_entry.title,
        ", ".join(active_features),
    )

    # None-Check für coordinator.data
    if coordinator.data is None:
        _LOGGER.warning(
            "Coordinator-Daten sind None für '%s'. "
            "Number-Entities werden nicht erstellt.",
            config_entry.title,
        )
        return

    entities: list[NumberEntity] = []

    for setpoint_config in SETPOINT_DEFINITIONS:
        setpoint_name = str(setpoint_config["name"])
        setpoint_key = str(setpoint_config["key"])
        feature_id = setpoint_config["feature_id"]

        # Prüfe ob Feature aktiviert ist
        if feature_id and feature_id not in active_features:
            _LOGGER.debug(
                "Überspringe Number '%s': Feature '%s' nicht aktiv",
                setpoint_name,
                feature_id,
            )
            continue

        # Prüfe ob Indikator-Felder verfügbar sind
        # (zeigt an, dass dieser Sollwert relevant ist)
        indicator_fields = setpoint_config.get("indicator_fields", [])
        if isinstance(indicator_fields, list):
            has_indicators = any(
                field in coordinator.data for field in indicator_fields
            )

            if not has_indicators:
                _LOGGER.debug(
                    "Überspringe Number '%s': Keine Indikator-Felder verfügbar (%s)",
                    setpoint_name,
                    ", ".join(str(f) for f in indicator_fields),
                )
                continue

        # Erstelle NumberEntityDescription
        description = NumberEntityDescription(
            key=setpoint_key,
            name=setpoint_name,
            icon=setpoint_config.get("icon"),  # type: ignore[arg-type]
            native_unit_of_measurement=setpoint_config.get("unit_of_measurement"),  # type: ignore[arg-type]
            device_class=setpoint_config.get("device_class"),  # type: ignore[arg-type]
            entity_category=setpoint_config.get("entity_category"),  # type: ignore[arg-type]
        )

        _LOGGER.debug(
            "Erstelle Number-Entity für '%s' (Key: %s)", setpoint_name, setpoint_key
        )

        entities.append(
            VioletNumber(coordinator, config_entry, description, setpoint_config)
        )

    # Entities hinzufügen
    if entities:
        async_add_entities(entities)
        # Type ignore: we know that entity_description.name is a string or None, and we handle None via str() if needed.
        # But actually NumberEntityDescription name is expected to be str | None.
        entity_names = [str(e.entity_description.name) for e in entities]
        _LOGGER.info(
            "%d Number-Entities für '%s' eingerichtet: %s",
            len(entities),
            config_entry.title,
            ", ".join(entity_names),
        )
    else:
        _LOGGER.info("Keine Number-Entities für '%s' eingerichtet", config_entry.title)
