"""API-Modul für die Kommunikation mit dem Violet Pool Controller."""
import logging
import asyncio
import aiohttp
from typing import Any, Dict, Optional, List, Union, Tuple

from .const import (
    API_READINGS,
    API_SET_FUNCTION_MANUALLY,
    API_SET_DOSING_PARAMETERS,
    API_SET_TARGET_VALUES,
    SWITCH_FUNCTIONS,
    COVER_FUNCTIONS,
    DOSING_FUNCTIONS,
)

_LOGGER = logging.getLogger(__name__)


class VioletPoolAPI:
    """Kapselt sämtliche Requests an den Violet Pool Controller."""

    def __init__(
        self,
        host: str,
        username: Optional[str],
        password: Optional[str],
        use_ssl: bool = True,
        timeout: int = 10,
    ):
        """Initialisiere das API-Objekt."""
        self.host = host
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.timeout = timeout

        # Die aiohttp.ClientSession wird extern (z.B. in __init__.py) gesetzt.
        self.session: Optional[aiohttp.ClientSession] = None

    async def get_readings(self, query: str = "ALL") -> Dict[str, Any]:
        """
        Liest aktuelle Werte vom Pool-Controller (GET).
        
        Args:
            query: Spezifische Abfrage für bestimmte Werte (z.B. 'pH_value,orp_value' 
                  oder Standardwert 'ALL' für alle Daten)
        
        Returns:
            Dictionary mit den abgefragten Werten
        """
        protocol = "https" if self.use_ssl else "http"
        url = f"{protocol}://{self.host}{API_READINGS}?{query}"
        _LOGGER.debug("GET readings from URL: %s", url)

        # Basic-Auth erzeugen, wenn Nutzer/Passwort existieren
        auth = (
            aiohttp.BasicAuth(self.username, self.password)
            if self.username and self.password
            else None
        )

        if not self.session:
            raise RuntimeError("Keine ClientSession gesetzt in VioletPoolAPI.")

        try:
            # Timeout via asyncio
            async with asyncio.timeout(self.timeout):
                async with self.session.get(url, auth=auth, ssl=self.use_ssl) as response:
                    response.raise_for_status()
                    return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("Fehler beim Abrufen der Pool-Daten: %s", err)
            raise ConnectionError(f"Fehler beim Abrufen der Pool-Daten: {err}") from err

    async def set_switch_state(
        self,
        key: str,
        action: str,
        duration: int = 0,
        last_value: int = 0
    ) -> str:
        """
        Steuert einen Switch (z.B. 'PUMP', 'LIGHT', 'ECO', 'DOS_1_CL', etc.).
        
        Args:
            key: Name des Switches, z.B. 'PUMP'
            action: Aktion, z.B. "ON", "OFF", "AUTO"
            duration: Optionaler Zeitwert, falls du am Gerät einen Timer setzen willst
            last_value: Optionaler Parameter (ggf. Wert, der vorher an war)
            
        Returns:
            Der Text der Antwort vom Gerät
        """
        if key not in SWITCH_FUNCTIONS and key not in DOSING_FUNCTIONS:
            _LOGGER.warning("Ungültiger Switch-Key: %s", key)
            return "ERROR: Ungültiger Switch-Key"
            
        protocol = "https" if self.use_ssl else "http"
        # URL zusammenbauen
        url = (
            f"{protocol}://{self.host}{API_SET_FUNCTION_MANUALLY}"
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

        if not self.session:
            raise RuntimeError("Keine ClientSession gesetzt in VioletPoolAPI.")

        auth = (
            aiohttp.BasicAuth(self.username, self.password)
            if self.username and self.password
            else None
        )

        try:
            async with asyncio.timeout(self.timeout):
                async with self.session.get(url, auth=auth, ssl=self.use_ssl) as response:
                    response.raise_for_status()
                    response_text = await response.text()
                    return response_text
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("Fehler beim Setzen des Switch-Status '%s': %s", action, err)
            raise ConnectionError(f"Fehler beim Setzen des Switch-Status '{action}': {err}") from err
    
    async def set_cover_state(self, action: str) -> str:
        """
        Steuert die Pool-Abdeckung.
        
        Args:
            action: "OPEN", "CLOSE", "STOP"
            
        Returns:
            Der Text der Antwort vom Gerät
        """
        # Mapping von Home Assistant-Aktionen zu Violet-Aktionen
        action_map = {
            "OPEN": "PUSH",  # Nur für DIRULE_x verwenden, wenn Cover über Schaltregel gesteuert wird
            "CLOSE": "PUSH", # Nur für DIRULE_x verwenden, wenn Cover über Schaltregel gesteuert wird 
            "STOP": "PUSH",  # Nur für DIRULE_x verwenden, wenn Cover über Schaltregel gesteuert wird
        }
        
        # Für direkte Steuerung über Standard-Cover
        cover_key = COVER_FUNCTIONS.get(action)
        if cover_key:
            return await self.set_switch_state(cover_key, "PUSH", 0, 0)
        else:
            _LOGGER.error("Ungültige Cover-Aktion: %s", action)
            return "ERROR: Ungültige Cover-Aktion"
    
    async def set_pv_surplus(self, state: bool, pump_speed: Optional[int] = None) -> str:
        """
        Aktiviert oder deaktiviert den Photovoltaik-Überschussmodus.
        
        Args:
            state: True für aktivieren, False für deaktivieren
            pump_speed: Optional - Drehzahlstufe der Pumpe (1-3)
            
        Returns:
            Der Text der Antwort vom Gerät
        """
        action = "ON" if state else "OFF"
        speed = pump_speed if pump_speed else 0
        
        return await self.set_switch_state("PVSURPLUS", action, speed, 0)
    
    async def set_dosing_parameters(
        self, 
        dosing_type: str, 
        parameter_name: str, 
        value: Union[str, int, float]
    ) -> str:
        """
        Setzt Dosierungsparameter wie Sollwerte.
        
        Args:
            dosing_type: z.B. "pH-", "pH+", "Chlor", "Flockmittel"
            parameter_name: Name des Parameters
            value: Neuer Wert
            
        Returns:
            Der Text der Antwort vom Gerät
        """
        protocol = "https" if self.use_ssl else "http"
        url = f"{protocol}://{self.host}{API_SET_DOSING_PARAMETERS}?{dosing_type},{parameter_name},{value}"
        
        _LOGGER.debug(
            "set_dosing_parameters -> Sende Kommando: type=%s, parameter=%s, value=%s, URL=%s",
            dosing_type,
            parameter_name,
            value,
            url,
        )
        
        auth = (
            aiohttp.BasicAuth(self.username, self.password)
            if self.username and self.password
            else None
        )
        
        if not self.session:
            raise RuntimeError("Keine ClientSession gesetzt in VioletPoolAPI.")
            
        try:
            async with asyncio.timeout(self.timeout):
                async with self.session.get(url, auth=auth, ssl=self.use_ssl) as response:
                    response.raise_for_status()
                    response_text = await response.text()
                    return response_text
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("Fehler beim Setzen der Dosierungsparameter: %s", err)
            raise ConnectionError(f"Fehler beim Setzen der Dosierungsparameter: {err}") from err
    
    async def manual_dosing(self, dosing_type: str, duration_seconds: int) -> str:
        """
        Löst eine manuelle Dosierung aus.
        
        Args:
            dosing_type: Dosierungstyp (pH-, pH+, Chlor, Flockmittel)
            duration_seconds: Dauer in Sekunden
            
        Returns:
            Der Text der Antwort vom Gerät
        """
        dosing_key = DOSING_FUNCTIONS.get(dosing_type)
        if not dosing_key:
            _LOGGER.error("Ungültiger Dosierungstyp: %s", dosing_type)
            return "ERROR: Ungültiger Dosierungstyp"
            
        return await self.set_switch_state(dosing_key, "MAN", duration_seconds, 0)
        
    async def set_target_value(
        self,
        target_type: str,
        value: Union[float, int]
    ) -> str:
        """
        Setzt einen Sollwert wie z.B. pH-Sollwert oder Redox.
        
        Args:
            target_type: Typ des Sollwerts ("pH", "ORP", "MinChlorine", etc.)
            value: Neuer Wert
            
        Returns:
            Der Text der Antwort vom Gerät
        """
        protocol = "https" if self.use_ssl else "http"
        url = f"{protocol}://{self.host}{API_SET_TARGET_VALUES}?{target_type},{value}"
        
        _LOGGER.debug(
            "set_target_value -> Sende Kommando: type=%s, value=%s, URL=%s",
            target_type,
            value,
            url,
        )
        
        auth = (
            aiohttp.BasicAuth(self.username, self.password)
            if self.username and self.password
            else None
        )
        
        if not self.session:
            raise RuntimeError("Keine ClientSession gesetzt in VioletPoolAPI.")
            
        try:
            async with asyncio.timeout(self.timeout):
                async with self.session.get(url, auth=auth, ssl=self.use_ssl) as response:
                    response.raise_for_status()
                    response_text = await response.text()
                    return response_text
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("Fehler beim Setzen des Sollwerts: %s", err)
            raise ConnectionError(f"Fehler beim Setzen des Sollwerts: {err}") from err
    
    async def set_ph_target(self, value: float) -> str:
        """
        Setzt den pH-Sollwert.
        
        Args:
            value: Neuer pH-Sollwert
            
        Returns:
            Der Text der Antwort vom Gerät
        """
        return await self.set_target_value("pH", value)
    
    async def set_orp_target(self, value: int) -> str:
        """
        Setzt den Redox-Sollwert (ORP).
        
        Args:
            value: Neuer Redox-Sollwert in mV
            
        Returns:
            Der Text der Antwort vom Gerät
        """
        return await self.set_target_value("ORP", value)
    
    async def set_min_chlorine_level(self, value: float) -> str:
        """
        Setzt den minimalen Chlorgehalt.
        
        Args:
            value: Neuer minimaler Chlorgehalt in mg/l
            
        Returns:
            Der Text der Antwort vom Gerät
        """
        return await self.set_target_value("MinChlorine", value)
    
    async def set_max_chlorine_level_day(self, value: float) -> str:
        """
        Setzt den maximalen Chlorgehalt tagsüber.
        
        Args:
            value: Neuer maximaler Chlorgehalt tagsüber in mg/l
            
        Returns:
            Der Text der Antwort vom Gerät
        """
        return await self.set_target_value("MaxChlorineDay", value)
    
    async def set_max_chlorine_level_night(self, value: float) -> str:
        """
        Setzt den maximalen Chlorgehalt nachts.
        
        Args:
            value: Neuer maximaler Chlorgehalt nachts in mg/l
            
        Returns:
            Der Text der Antwort vom Gerät
        """
        return await self.set_target_value("MaxChlorineNight", value)
    
    async def set_maintenance_mode(self, enabled: bool) -> str:
        """
        Aktiviert oder deaktiviert den Wartungsmodus.
        
        Args:
            enabled: True für aktivieren, False für deaktivieren
            
        Returns:
            Der Text der Antwort vom Gerät
        """
        action = "ON" if enabled else "OFF"
        return await self.set_switch_state("MAINTENANCE", action)
    
    async def start_water_analysis(self) -> str:
        """
        Startet eine Wasseranalyse.
        
        Returns:
            Der Text der Antwort vom Gerät
        """
        protocol = "https" if self.use_ssl else "http"
        url = f"{protocol}://{self.host}/startWaterAnalysis"
        
        auth = (
            aiohttp.BasicAuth(self.username, self.password)
            if self.username and self.password
            else None
        )
        
        if not self.session:
            raise RuntimeError("Keine ClientSession gesetzt in VioletPoolAPI.")
            
        try:
            async with asyncio.timeout(self.timeout):
                async with self.session.get(url, auth=auth, ssl=self.use_ssl) as response:
                    response.raise_for_status()
                    response_text = await response.text()
                    return response_text
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("Fehler beim Starten der Wasseranalyse: %s", err)
            raise ConnectionError(f"Fehler beim Starten der Wasseranalyse: {err}") from err
    
    async def get_dosing_stats(self) -> Dict[str, Any]:
        """
        Gibt Statistiken zur Dosierung zurück.
        
        Returns:
            Dictionary mit Dosierungsstatistiken
        """
        protocol = "https" if self.use_ssl else "http"
        url = f"{protocol}://{self.host}/getDosingStats"
        
        auth = (
            aiohttp.BasicAuth(self.username, self.password)
            if self.username and self.password
            else None
        )
        
        if not self.session:
            raise RuntimeError("Keine ClientSession gesetzt in VioletPoolAPI.")
            
        try:
            async with asyncio.timeout(self.timeout):
                async with self.session.get(url, auth=auth, ssl=self.use_ssl) as response:
                    response.raise_for_status()
                    return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("Fehler beim Abrufen der Dosierungsstatistiken: %s", err)
            raise ConnectionError(f"Fehler beim Abrufen der Dosierungsstatistiken: {err}") from err
