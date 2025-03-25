"""API-Modul für die Kommunikation mit dem Violet Pool Controller."""
import logging
import asyncio
import aiohttp
from typing import Any, Dict, Optional, List, Union

from .const import (
    API_READINGS, 
    API_SET_FUNCTION_MANUALLY,
    DEFAULT_TIMEOUT_DURATION,
    DEFAULT_RETRY_ATTEMPTS
)

_LOGGER = logging.getLogger(__name__)


class VioletPoolAPI:
    """Kapselt sämtliche Requests an den Violet Pool Controller."""

    def __init__(
        self,
        host: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_ssl: bool = True,
        timeout: int = DEFAULT_TIMEOUT_DURATION,
        retries: int = DEFAULT_RETRY_ATTEMPTS,
    ):
        """Initialisiere das API-Objekt."""
        self.host = host
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.retries = retries

        # Die aiohttp.ClientSession wird extern (z.B. in __init__.py) gesetzt.
        self.session: Optional[aiohttp.ClientSession] = None
        self.protocol = "https" if self.use_ssl else "http"

    async def get_readings(self, params: Optional[str] = "ALL") -> Dict[str, Any]:
        """
        Liest aktuelle Werte vom Pool-Controller (GET).
        Beispiel: Temperatur, Pumpenstatus usw.
        
        :param params: Optional - Spezifische Parameter, die gelesen werden sollen (Default: "ALL")
        """
        url = f"{self.protocol}://{self.host}{API_READINGS}?{params}"
        _LOGGER.debug("GET readings from URL: %s", url)

        # Basic-Auth erzeugen, wenn Nutzer/Passwort existieren
        auth = (
            aiohttp.BasicAuth(self.username, self.password)
            if self.username and self.password
            else None
        )

        if not self.session:
            raise RuntimeError("Keine ClientSession gesetzt in VioletPoolAPI.")

        for attempt in range(self.retries):
            try:
                # Timeout via asyncio
                async with asyncio.timeout(self.timeout):
                    async with self.session.get(url, auth=auth, ssl=self.use_ssl) as response:
                        response.raise_for_status()
                        return await response.json()
            except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                _LOGGER.error("Fehler beim Abrufen der Pool-Daten (Versuch %d/%d): %s", 
                              attempt + 1, self.retries, err)
                if attempt + 1 == self.retries:
                    raise ConnectionError(f"Fehler beim Abrufen der Pool-Daten: {err}") from err
                # Exponentielles Backoff
                await asyncio.sleep(2 ** attempt)

        raise ConnectionError("Fehler beim Abrufen der Pool-Daten nach allen Versuchen.")

    async def set_switch_state(
        self,
        key: str,
        action: str,
        duration: int = 0,
        last_value: int = 0
    ) -> str:
        """
        Steuert einen Switch (z.B. 'PUMP', 'LIGHT', 'ECO', 'DOS_1_CL', etc.).
        
        :param key: Name des Switches, z.B. 'PUMP'
        :param action: Aktion, z.B. "ON", "OFF", "AUTO"
        :param duration: Optionaler Zeitwert, falls du am Gerät einen Timer setzen willst
        :param last_value: Optionaler Parameter (ggf. Wert, der vorher an war)
        :return: Der Text der Antwort vom Gerät (oder wirf Exception bei Fehler)
        """
        url = (
            f"{self.protocol}://{self.host}{API_SET_FUNCTION_MANUALLY}"
            f"?{key},{action},{duration},{last_value}"
        )
        _LOGGER.debug(
            "set_switch_state -> Sende Kommando: key=%s, action=%s, duration=%d, last_value=%d, URL=%s",
            key,
            action,
            duration,
            last_value,
            url,
        )

        return await self._send_command(url)

    async def set_cover_state(self, action: str) -> str:
        """
        Steuert die Pool-Abdeckung.
        
        :param action: "OPEN", "CLOSE" oder "STOP"
        :return: Die Antwort vom Gerät
        """
        command_map = {
            "OPEN": "AUF",
            "CLOSE": "ZU",
            "STOP": "STOP"
        }
        
        command = command_map.get(action.upper(), "STOP")
        
        # Für die Poolabdeckung werden spezielle Kommandos verwendet
        if command == "AUF":
            return await self.set_switch_state("DIRULE_10", "PUSH", 0, 0)
        elif command == "ZU":
            return await self.set_switch_state("DIRULE_12", "PUSH", 0, 0)
        else: # STOP
            return await self.set_switch_state("DIRULE_11", "PUSH", 0, 0)

    async def set_pump_state(self, pump_on: bool, speed: int = 0, duration: int = 0) -> str:
        """
        Schaltet die Pumpe ein oder aus.
        
        :param pump_on: True für Ein, False für Aus
        :param speed: Geschwindigkeit 1-3 bei regelbarer Pumpe, 0 für Standard
        :param duration: Optional - Dauer in Sekunden, 0 für permanent
        :return: Die Antwort vom Gerät
        """
        action = "ON" if pump_on else "OFF"
        return await self.set_switch_state("PUMP", action, duration, speed)

    async def set_pump_auto(self) -> str:
        """
        Setzt die Pumpe auf Automatik-Modus.
        
        :return: Die Antwort vom Gerät
        """
        return await self.set_switch_state("PUMP", "AUTO", 0, 0)

    async def set_heating_state(self, heating_on: bool, duration: int = 0) -> str:
        """
        Schaltet die Heizung ein oder aus.
        
        :param heating_on: True für Ein, False für Aus
        :param duration: Optional - Dauer in Sekunden, 0 für permanent
        :return: Die Antwort vom Gerät
        """
        action = "ON" if heating_on else "OFF"
        return await self.set_switch_state("HEATER", "AUTO" if not heating_on else action, duration, 0)

    async def set_solar_state(self, solar_on: bool, duration: int = 0) -> str:
        """
        Schaltet den Solarabsorber ein oder aus.
        
        :param solar_on: True für Ein, False für Aus
        :param duration: Optional - Dauer in Sekunden, 0 für permanent
        :return: Die Antwort vom Gerät
        """
        action = "ON" if solar_on else "OFF"
        return await self.set_switch_state("SOLAR", "AUTO" if not solar_on else action, duration, 0)

    async def set_light_state(self, light_on: bool) -> str:
        """
        Schaltet die Beleuchtung ein oder aus.
        
        :param light_on: True für Ein, False für Aus
        :return: Die Antwort vom Gerät
        """
        action = "ON" if light_on else "OFF"
        return await self.set_switch_state("LIGHT", action, 0, 0)

    async def set_light_color(self) -> str:
        """
        Wechselt die Farbe der Beleuchtung.
        
        :return: Die Antwort vom Gerät
        """
        return await self.set_switch_state("LIGHT", "COLOR", 0, 0)

    async def set_dmx_scene(self, scene_number: int, scene_on: bool) -> str:
        """
        Schaltet eine DMX-Lichtszene ein oder aus.
        
        :param scene_number: Nummer der Szene (1-12)
        :param scene_on: True für Ein, False für Aus
        :return: Die Antwort vom Gerät
        """
        if not 1 <= scene_number <= 12:
            raise ValueError("DMX Szenen-Nummer muss zwischen 1 und 12 liegen.")
            
        action = "ON" if scene_on else "OFF"
        return await self.set_switch_state(f"DMX_SCENE{scene_number}", action, 0, 0)
        
    async def set_backwash_state(self, backwash_on: bool) -> str:
        """
        Startet oder stoppt die Rückspülung manuell.
        
        :param backwash_on: True für Start, False für Stop
        :return: Die Antwort vom Gerät
        """
        action = "ON" if backwash_on else "OFF"
        return await self.set_switch_state("BACKWASH", action, 0, 0)

    async def set_pv_surplus(self, enable: bool, speed: int = 0) -> str:
        """
        Aktiviert oder deaktiviert den PV-Überschussmodus.
        
        :param enable: True zum Aktivieren, False zum Deaktivieren
        :param speed: Geschwindigkeit für die Pumpe (1-3)
        :return: Die Antwort vom Gerät
        """
        action = "ON" if enable else "OFF"
        return await self.set_switch_state("PVSURPLUS", action, speed, 0)

    async def manual_dosing(self, dosing_type: str, duration_seconds: int) -> str:
        """
        Startet eine manuelle Dosierung.
        
        :param dosing_type: Typ der Dosierung ('DOS_1_CL', 'DOS_4_PHM', 'DOS_5_PHP', 'DOS_6_FLOC')
        :param duration_seconds: Dauer der Dosierung in Sekunden
        :return: Die Antwort vom Gerät
        """
        valid_types = ['DOS_1_CL', 'DOS_4_PHM', 'DOS_5_PHP', 'DOS_6_FLOC', 'DOS_2_ELO']
        if dosing_type not in valid_types:
            raise ValueError(f"Ungültiger Dosierungstyp. Muss einer von {valid_types} sein")
            
        return await self.set_switch_state(dosing_type, "ON", duration_seconds, 0)
        
    async def reset_canister(self, dosing_type: str, volume_ml: int) -> str:
        """
        Setzt den Kanisterinhalt zurück.
        
        :param dosing_type: Typ der Dosierung ('DOS_1_CL', 'DOS_4_PHM', 'DOS_5_PHP', 'DOS_6_FLOC')
        :param volume_ml: Neues Volumen in ml
        :return: Die Antwort vom Gerät
        """
        # Für den Gebindewechsel würden wir einen anderen API-Endpunkt verwenden müssen
        # Da dieser in der API nicht direkt dokumentiert ist, kann dies später ergänzt werden
        _LOGGER.error("Die Reset-Kanister-Funktion ist noch nicht implementiert")
        return "NOT_IMPLEMENTED"

    async def set_rule_state(self, rule_number: int, action: str) -> str:
        """
        Schaltet eine Regel ein, aus oder sperrt/entsperrt sie.
        
        :param rule_number: Nummer der Regel (1-7)
        :param action: "PUSH" (auslösen), "LOCK" (sperren) oder "UNLOCK" (entsperren)
        :return: Die Antwort vom Gerät
        """
        if not 1 <= rule_number <= 7:
            raise ValueError("Regelnummer muss zwischen 1 und 7 liegen.")
        
        valid_actions = ["PUSH", "LOCK", "UNLOCK"]
        if action not in valid_actions:
            raise ValueError(f"Ungültige Aktion. Muss eine von {valid_actions} sein")
            
        return await self.set_switch_state(f"DIRULE_{rule_number}", action, 0, 0)

    async def _send_command(self, url: str) -> str:
        """
        Sendet einen Befehl an den Pool-Controller und verarbeitet die Antwort.
        
        :param url: Die zu verwendende URL inkl. der Parameter
        :return: Der Text der Antwort vom Gerät
        """
        if not self.session:
            raise RuntimeError("Keine ClientSession gesetzt in VioletPoolAPI.")

        auth = (
            aiohttp.BasicAuth(self.username, self.password)
            if self.username and self.password
            else None
        )

        for attempt in range(self.retries):
            try:
                async with asyncio.timeout(self.timeout):
                    async with self.session.get(url, auth=auth, ssl=self.use_ssl) as response:
                        response.raise_for_status()
                        response_text = await response.text()
                        _LOGGER.debug("Antwort vom Gerät: %s", response_text)
                        return response_text
            except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                _LOGGER.error("Fehler beim Senden des Befehls (Versuch %d/%d): %s", 
                             attempt + 1, self.retries, err)
                if attempt + 1 == self.retries:
                    raise ConnectionError(f"Fehler beim Senden des Befehls: {err}") from err
                # Exponentielles Backoff
                await asyncio.sleep(2 ** attempt)

        raise ConnectionError("Fehler beim Senden des Befehls nach allen Versuchen.")
