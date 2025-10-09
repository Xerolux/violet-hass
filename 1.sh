#!/bin/bash
# violet_pool_fixes.sh - Complete fix script

echo "?? Starte Violet Pool Controller Fixes..."

# Fix 1: device.py vervollständigen
echo "?? Fix 1: device.py vervollständigen..."
cat >> custom_components/violet_pool_controller/device.py << 'DEVICE_EOF'

        # Username kann leer sein, aber sollte nicht None sein für API-Initialisierung
        username = entry.data.get(CONF_USERNAME, "")
        password = entry.data.get(CONF_PASSWORD, "")
        
        _LOGGER.info(
            "Initialisiere VioletPoolAPI: host=%s, ssl=%s, timeout=%ds",
            self.api_url, self.use_ssl, self.timeout
        )

    async def async_update(self) -> Dict[str, Any]:
        """Update-Methode für Coordinator - IMPROVED."""
        try:
            async with self._api_lock:
                _LOGGER.debug("Starte API-Update für %s", self.device_name)
                
                data = await self.api.get_readings()
                
                if not data or not isinstance(data, dict):
                    _LOGGER.warning("Leere oder ungültige Daten vom Controller")
                    self._consecutive_failures += 1
                    if self._consecutive_failures >= self._max_consecutive_failures:
                        self._available = False
                        raise UpdateFailed(
                            f"Controller antwortet nicht ({self._consecutive_failures} Fehler)"
                        )
                    return self._data
                
                self._data = data
                self._available = True
                self._consecutive_failures = 0
                self._last_error = None
                
                if "FW" in data or "fw" in data:
                    self._firmware_version = data.get("FW") or data.get("fw")
                
                _LOGGER.debug("Update erfolgreich: %d Datenpunkte empfangen", len(data))
                
                return data
                
        except VioletPoolAPIError as err:
            self._last_error = str(err)
            self._consecutive_failures += 1
            _LOGGER.error("API-Fehler bei Update (%d/%d): %s", self._consecutive_failures, self._max_consecutive_failures, err)
            
            if self._consecutive_failures >= self._max_consecutive_failures:
                self._available = False
                raise UpdateFailed(f"Controller nicht erreichbar: {err}") from err
            
            return self._data
            
        except Exception as err:
            self._last_error = str(err)
            self._consecutive_failures += 1
            _LOGGER.exception("Unerwarteter Fehler bei Update (%d/%d): %s", self._consecutive_failures, self._max_consecutive_failures, err)
            
            if self._consecutive_failures >= self._max_consecutive_failures:
                self._available = False
                raise UpdateFailed(f"Update-Fehler: {err}") from err
            
            return self._data

    @property
    def available(self) -> bool:
        return self._available

    @property
    def firmware_version(self) -> Optional[str]:
        return self._firmware_version

    @property
    def data(self) -> Dict[str, Any]:
        return self._data

    @property
    def device_info(self) -> Dict[str, Any]:
        if not self._device_info:
            self._device_info = {
                "identifiers": {(DOMAIN, f"{self.api_url}_{self.device_id}")},
                "name": self.device_name,
                "manufacturer": "PoolDigital GmbH & Co. KG",
                "model": "Violet Pool Controller",
                "sw_version": self._firmware_version or "unknown",
            }
        return self._device_info

    def _extract_api_url(self, entry_data: Dict) -> str:
        url = (
            entry_data.get(CONF_API_URL) or
            entry_data.get("host") or
            entry_data.get("base_ip")
        )
        
        if not url:
            raise ValueError("Keine IP-Adresse in Config Entry gefunden")
        
        return url.strip()


class VioletPoolDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, device: VioletPoolControllerDevice, name: str, polling_interval: int = DEFAULT_POLLING_INTERVAL) -> None:
        super().__init__(hass, logging.getLogger(__name__), name=name, update_interval=timedelta(seconds=polling_interval))
        self.device = device
        _LOGGER.debug("Coordinator initialisiert für %s (Intervall: %ds)", name, polling_interval)

    async def _async_update_data(self) -> Dict[str, Any]:
        try:
            return await self.device.async_update()
        except VioletPoolAPIError as err:
            _LOGGER.error("Fehler beim Datenabruf: %s", err)
            raise UpdateFailed(f"Fehler: {err}") from err


async def async_setup_device(hass: HomeAssistant, config_entry: ConfigEntry, api: VioletPoolAPI) -> VioletPoolDataUpdateCoordinator:
    try:
        device = VioletPoolControllerDevice(hass, config_entry, api)
        await device.async_update()
        
        if not device.available:
            raise ConfigEntryNotReady("Controller nicht erreichbar bei Setup")
        
        polling_interval = config_entry.options.get(CONF_POLLING_INTERVAL, config_entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL))
        
        coordinator = VioletPoolDataUpdateCoordinator(hass, device, config_entry.data.get(CONF_DEVICE_NAME, "Violet Pool Controller"), polling_interval)
        
        await coordinator.async_config_entry_first_refresh()
        
        _LOGGER.info("Device Setup erfolgreich: %s (FW: %s)", device.device_name, device.firmware_version or "unknown")
        
        return coordinator
        
    except Exception as err:
        _LOGGER.error("Device Setup fehlgeschlagen: %s", err)
        raise ConfigEntryNotReady(f"Setup-Fehler: {err}") from err
DEVICE_EOF

# Fix 2: API-Methoden hinzufügen  
echo "?? Fix 2: Fehlende API-Methoden hinzufügen..."

# Finde Ende der VioletPoolAPI Klasse und füge neue Methoden ein
cat >> custom_components/violet_pool_controller/api.py << 'API_EOF'

    # =========================================================================
    # MISSING API METHODS - ADDED FOR FULL FUNCTIONALITY
    # =========================================================================

    async def set_device_temperature(self, device_key: str, temperature: float) -> Dict[str, Any]:
        """Setze Zieltemperatur für Heizung oder Solar."""
        if not 20.0 <= temperature <= 40.0:
            raise VioletPoolValidationError(f"Temperatur {temperature}°C außerhalb gültigen Bereichs (20-40°C)")
        
        target_key = f"{device_key}_TARGET_TEMP"
        _LOGGER.info("Setze %s auf %.1f°C", device_key, temperature)
        
        result = await self.api_request(
            endpoint=API_SET_TARGET_VALUES,
            method="POST",
            raw_query=f"{target_key},{temperature}",
            require_auth=True,
            expected_format=ResponseFormat.AUTO
        )
        return self._normalize_response(result)

    async def set_ph_target(self, value: float) -> Dict[str, Any]:
        """Setze pH-Sollwert."""
        return await self.set_target_value(TARGET_PH, value)

    async def set_orp_target(self, value: int) -> Dict[str, Any]:
        """Setze ORP/Redox-Sollwert."""
        return await self.set_target_value(TARGET_ORP, value)

    async def set_min_chlorine_level(self, value: float) -> Dict[str, Any]:
        """Setze Mindest-Chlor-Level."""
        return await self.set_target_value(TARGET_MIN_CHLORINE, value)

    async def manual_dosing(self, dosing_type: str, duration: int) -> Dict[str, Any]:
        """Führe manuelle Dosierung durch."""
        device_mapping = {
            "pH-": "DOS_4_PHM",
            "pH+": "DOS_5_PHP",
            "Chlor": "DOS_1_CL",
            "Flockmittel": "DOS_6_FLOC"
        }
        
        device_key = device_mapping.get(dosing_type)
        if not device_key:
            raise VioletPoolCommandError(f"Unbekannter Dosiertyp: {dosing_type}")
        
        if not 5 <= duration <= 300:
            raise VioletPoolValidationError(f"Dosierdauer {duration}s außerhalb gültigen Bereichs (5-300s)")
        
        _LOGGER.info("Manuelle Dosierung %s für %ds", dosing_type, duration)
        
        return await self.set_switch_state(key=device_key, action=ACTION_MAN, duration=duration)

    async def set_pv_surplus(self, active: bool, pump_speed: int = 2) -> Dict[str, Any]:
        """Setze PV-Überschuss Modus."""
        action = ACTION_ON if active else ACTION_OFF
        _LOGGER.info("PV-Überschuss %s (Speed %d)", action, pump_speed)
        return await self.set_switch_state(key="PVSURPLUS", action=action, last_value=pump_speed)

    async def set_all_dmx_scenes(self, dmx_action: str) -> Dict[str, Any]:
        """Setze alle DMX-Szenen gleichzeitig."""
        valid_actions = [ACTION_ALLON, ACTION_ALLOFF, ACTION_ALLAUTO]
        if dmx_action not in valid_actions:
            raise VioletPoolCommandError(f"Ungültige DMX-Aktion: {dmx_action}")
        
        _LOGGER.info("Setze alle DMX-Szenen auf %s", dmx_action)
        return await self.set_switch_state(key="DMX_SCENE1", action=dmx_action)

    async def trigger_digital_input_rule(self, rule_key: str) -> Dict[str, Any]:
        """Löse digitale Schaltregel aus."""
        valid_rules = [f"DIRULE_{i}" for i in range(1, 8)]
        if rule_key not in valid_rules:
            raise VioletPoolCommandError(f"Ungültige Regel: {rule_key}")
        
        _LOGGER.info("Triggere Regel %s", rule_key)
        return await self.set_switch_state(key=rule_key, action=ACTION_PUSH)

    async def set_digital_input_rule_lock(self, rule_key: str, lock_state: bool) -> Dict[str, Any]:
        """Sperre oder entsperre digitale Schaltregel."""
        valid_rules = [f"DIRULE_{i}" for i in range(1, 8)]
        if rule_key not in valid_rules:
            raise VioletPoolCommandError(f"Ungültige Regel: {rule_key}")
        
        action = ACTION_LOCK if lock_state else ACTION_UNLOCK
        _LOGGER.info("%s Regel %s", action, rule_key)
        return await self.set_switch_state(key=rule_key, action=action)

    async def set_light_color_pulse(self) -> Dict[str, Any]:
        """Sende Farbpuls an Beleuchtung."""
        _LOGGER.info("Sende Licht-Farbpuls")
        return await self.set_switch_state(key="LIGHT", action=ACTION_COLOR)
API_EOF

# Fix 3: Cover State Map Fix
echo "?? Fix 3: Cover String-State Fix..."
sed -i 's/from \.const import DOMAIN, CONF_ACTIVE_FEATURES, COVER_FUNCTIONS/from .const import DOMAIN, CONF_ACTIVE_FEATURES, COVER_FUNCTIONS, COVER_STATE_MAP/' custom_components/violet_pool_controller/cover.py

# Entferne doppelte COVER_STATE_MAP Definition falls vorhanden
sed -i '/^COVER_STATE_MAP = {$/,/^}$/d' custom_components/violet_pool_controller/cover.py

echo ""
echo "? Alle Fixes erfolgreich angewendet!"
echo ""
echo "?? Zusammenfassung der Änderungen:"
echo "  ? device.py vervollständigt"
echo "  ? 10 fehlende API-Methoden hinzugefügt"
echo "  ? Cover String-State Handling korrigiert"
echo ""
echo "?? Nächste Schritte:"
echo "  1. Home Assistant neu starten"
echo "  2. Integration neu laden"
echo "  3. Funktionalität testen"