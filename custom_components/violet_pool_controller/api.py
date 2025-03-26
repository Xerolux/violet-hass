"""API-Modul für die Kommunikation mit dem Violet Pool Controller."""
import logging
import asyncio
import json
from typing import Any, Dict, Optional, List, Union, Tuple

import aiohttp
import async_timeout

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


class VioletPoolAPIError(Exception):
    """Basisklasse für API-Fehler des Violet Pool Controllers."""
    pass


class VioletPoolConnectionError(VioletPoolAPIError):
    """Fehler bei der Verbindung zum Violet Pool Controller."""
    pass


class VioletPoolCommandError(VioletPoolAPIError):
    """Fehler bei der Ausführung eines Befehls am Violet Pool Controller."""
    pass


class VioletPoolAPI:
    """Kapselt sämtliche Requests an den Violet Pool Controller."""

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_ssl: bool = True,
        timeout: int = 10,
    ):
        """Initialisiere das API-Objekt.
        
        Args:
            host: IP-Adresse oder Hostname des Controllers
            session: Aktive aiohttp.ClientSession
            username: Optionaler Benutzername
            password: Optionales Passwort
            use_ssl: True für HTTPS, False für HTTP
            timeout: Timeout in Sekunden
        """
        self.host = host
        self.session = session
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.protocol = "https" if self.use_ssl else "http"
        self.base_url = f"{self.protocol}://{self.host}"
        
        # Auth-Objekt erstellen, falls Credentials vorhanden
        self.auth = None
        if self.username and self.password:
            self.auth = aiohttp.BasicAuth(
                login=self.username, 
                password=self.password
            )

    async def api_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        raw_query: Optional[str] = None,
    ) -> Union[Dict[str, Any], str]:
        """Führt einen API-Request aus und gibt das Ergebnis zurück.
        
        Args:
            endpoint: API-Endpunkt (z.B. "/getReadings")
            method: HTTP-Methode (GET oder POST)
            params: Dictionary mit GET-Parametern
            data: Dictionary mit POST-Daten
            raw_query: Rohes Query-String (alternative zu params)
            
        Returns:
            Union[Dict[str, Any], str]: JSON-Antwort oder String
            
        Raises:
            VioletPoolConnectionError: Bei Verbindungsproblemen
            VioletPoolCommandError: Bei Fehlern bei der Befehlsausführung
        """
        url = f"{self.base_url}{endpoint}"
        
        # Raw Query anhängen, falls vorhanden
        if raw_query:
            url = f"{url}?{raw_query}"
            
        _LOGGER.debug(
            "%s request to %s (params=%s, data=%s)",
            method,
            url,
            params,
            data,
        )
            
        try:
            async with async_timeout.timeout(self.timeout):
                async with self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    auth=self.auth,
                    ssl=self.use_ssl
                ) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        error_msg = f"HTTP {response.status}: {error_text}"
                        _LOGGER.error("API-Fehler: %s", error_msg)
                        raise VioletPoolCommandError(error_msg)
                    
                    # Prüfe Content-Type
                    content_type = response.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        result = await response.json()
                        _LOGGER.debug("API-JSON-Antwort: %s", result)
                        return result
                    else:
                        text = await response.text()
                        _LOGGER.debug("API-Text-Antwort: %s", text)
                        return text
                    
        except asyncio.TimeoutError as err:
            error_msg = f"Timeout bei Verbindung zu {self.host}: {err}"
            _LOGGER.error(error_msg)
            raise VioletPoolConnectionError(error_msg) from err
            
        except aiohttp.ClientError as err:
            error_msg = f"Verbindungsfehler zu {self.host}: {err}"
            _LOGGER.error(error_msg)
            raise VioletPoolConnectionError(error_msg) from err
            
        except Exception as err:
            error_msg = f"Unerwarteter Fehler bei API-Anfrage: {err}"
            _LOGGER.exception(error_msg)
            raise VioletPoolAPIError(error_msg) from err

    async def get_readings(self, query: str = "ALL") -> Dict[str, Any]:
        """Liest aktuelle Werte vom Pool-Controller.
        
        Args:
            query: Spezifische Abfrage für bestimmte Werte (z.B. 'pH_value,orp_value' 
                  oder Standardwert 'ALL' für alle Daten)
        
        Returns:
            Dictionary mit den abgefragten Werten
            
        Raises:
            VioletPoolConnectionError: Bei Verbindungsproblemen
            VioletPoolCommandError: Bei Fehlern bei der Befehlsausführung
        """
        result = await self.api_request(
            endpoint=API_READINGS,
            params={"query": query} if query != "ALL" else None,
            raw_query=query if query != "ALL" else None,
        )
        
        if isinstance(result, str):
            # Versuche String als JSON zu parsen (manchmal liefert der Controller JSON mit falschem Content-Type)
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # Wenn es kein gültiges JSON ist, gib ein Dict mit dem Rohtext zurück
                return {"raw_response": result}
        
        return result

    async def set_switch_state(
        self,
        key: str,
        action: str,
        duration: int = 0,
        last_value: int = 0
    ) -> Dict[str, Any]:
        """Steuert einen Switch (z.B. 'PUMP', 'LIGHT', 'ECO', 'DOS_1_CL', etc.).
        
        Args:
            key: Name des Switches, z.B. 'PUMP'
            action: Aktion, z.B. "ON", "OFF", "AUTO"
            duration: Optionaler Zeitwert, falls du am Gerät einen Timer setzen willst
            last_value: Optionaler Parameter (ggf. Wert, der vorher an war)
            
        Returns:
            Dict mit der Antwort vom Gerät
            
        Raises:
            VioletPoolCommandError: Bei ungültigem Switch-Key oder Fehlern
        """
        if key not in SWITCH_FUNCTIONS and key not in DOSING_FUNCTIONS and key != "MAINTENANCE":
            error_msg = f"Ungültiger Switch-Key: {key}"
            _LOGGER.warning(error_msg)
            raise VioletPoolCommandError(error_msg)
            
        raw_query = f"{key},{action},{duration},{last_value}"
        
        _LOGGER.debug(
            "set_switch_state: key=%s, action=%s, duration=%d, last_value=%d",
            key,
            action,
            duration,
            last_value,
        )
        
        result = await self.api_request(
            endpoint=API_SET_FUNCTION_MANUALLY,
            raw_query=raw_query,
        )
        
        # Normalisiere das Ergebnis zu einem Dictionary
        if isinstance(result, str):
            return {"response": result, "success": "OK" in result or "SUCCESS" in result}
        return result

    async def set_cover_state(self, action: str) -> Dict[str, Any]:
        """Steuert die Pool-Abdeckung.
        
        Args:
            action: "OPEN", "CLOSE", "STOP"
            
        Returns:
            Dict mit der Antwort vom Gerät
            
        Raises:
            VioletPoolCommandError: Bei ungültiger Aktion
        """
        # Gültige Aktionen für die Abdeckung
        valid_actions = ["OPEN", "CLOSE", "STOP"]
        
        if action not in valid_actions:
            error_msg = f"Ungültige Cover-Aktion: {action}"
            _LOGGER.error(error_msg)
            raise VioletPoolCommandError(error_msg)
            
        # Für direkte Steuerung über Standard-Cover
        cover_key = COVER_FUNCTIONS.get(action)
        if cover_key:
            return await self.set_switch_state(cover_key, "PUSH", 0, 0)
            
        # Fallback für Systeme, die DIRULE_x verwenden
        # Hier könnten weitere Implementierungen je nach Systemtyp erfolgen
        error_msg = f"Cover-Aktion {action} nicht unterstützt von diesem System"
        _LOGGER.error(error_msg)
        raise VioletPoolCommandError(error_msg)
    
    async def set_pv_surplus(self, active: bool, pump_speed: Optional[int] = None) -> Dict[str, Any]:
        """Aktiviert oder deaktiviert den Photovoltaik-Überschussmodus.
        
        Args:
            active: True für aktivieren, False für deaktivieren
            pump_speed: Optional - Drehzahlstufe der Pumpe (1-3)
            
        Returns:
            Dict mit der Antwort vom Gerät
            
        Raises:
            VioletPoolCommandError: Bei Fehlern
        """
        action = "ON" if active else "OFF"
        
        # Validiere pump_speed
        if active and pump_speed is not None:
            if not 1 <= pump_speed <= 3:
                error_msg = f"Ungültige Pumpendrehzahl: {pump_speed}. Erlaubt sind 1-3."
                _LOGGER.warning(error_msg)
                pump_speed = max(1, min(3, pump_speed))  # Clamp to 1-3
        else:
            pump_speed = 0
                
        return await self.set_switch_state("PVSURPLUS", action, pump_speed, 0)
    
    async def set_dosing_parameters(
        self, 
        dosing_type: str, 
        parameter_name: str, 
        value: Union[str, int, float]
    ) -> Dict[str, Any]:
        """Setzt Dosierungsparameter wie Sollwerte.
        
        Args:
            dosing_type: z.B. "pH-", "pH+", "Chlor", "Flockmittel"
            parameter_name: Name des Parameters
            value: Neuer Wert
            
        Returns:
            Dict mit der Antwort vom Gerät
            
        Raises:
            VioletPoolConnectionError: Bei Verbindungsproblemen
            VioletPoolCommandError: Bei Fehlern bei der Befehlsausführung
        """
        raw_query = f"{dosing_type},{parameter_name},{value}"
        
        _LOGGER.debug(
            "set_dosing_parameters: type=%s, parameter=%s, value=%s",
            dosing_type,
            parameter_name,
            value,
        )
        
        result = await self.api_request(
            endpoint=API_SET_DOSING_PARAMETERS,
            raw_query=raw_query,
        )
        
        # Normalisiere das Ergebnis
        if isinstance(result, str):
            return {"response": result, "success": "OK" in result or "SUCCESS" in result}
        return result
    
    async def manual_dosing(self, dosing_type: str, duration_seconds: int) -> Dict[str, Any]:
        """Löst eine manuelle Dosierung aus.
        
        Args:
            dosing_type: Dosierungstyp (pH-, pH+, Chlor, Flockmittel)
            duration_seconds: Dauer in Sekunden
            
        Returns:
            Dict mit der Antwort vom Gerät
            
        Raises:
            VioletPoolCommandError: Bei ungültigem Dosierungstyp
        """
        # Validiere duration_seconds
        if duration_seconds <= 0 or duration_seconds > 3600:
            error_msg = f"Ungültige Dauer: {duration_seconds}. Erlaubt sind 1-3600 Sekunden."
            _LOGGER.warning(error_msg)
            duration_seconds = max(1, min(3600, duration_seconds))  # Clamp to 1-3600
            
        dosing_key = DOSING_FUNCTIONS.get(dosing_type)
        if not dosing_key:
            error_msg = f"Ungültiger Dosierungstyp: {dosing_type}"
            _LOGGER.error(error_msg)
            raise VioletPoolCommandError(error_msg)
            
        return await self.set_switch_state(dosing_key, "MAN", duration_seconds, 0)
        
    async def set_target_value(
        self,
        target_type: str,
        value: Union[float, int]
    ) -> Dict[str, Any]:
        """Setzt einen Sollwert wie z.B. pH-Sollwert oder Redox.
        
        Args:
            target_type: Typ des Sollwerts ("pH", "ORP", "MinChlorine", etc.)
            value: Neuer Wert
            
        Returns:
            Dict mit der Antwort vom Gerät
            
        Raises:
            VioletPoolConnectionError: Bei Verbindungsproblemen
            VioletPoolCommandError: Bei Fehlern bei der Befehlsausführung
        """
        # Wertebereich validieren
        if target_type == "pH" and (value < 6.8 or value > 7.8):
            _LOGGER.warning(
                "pH-Sollwert %f außerhalb des üblichen Bereichs (6.8-7.8). Fortfahren...",
                value
            )
            
        if target_type == "ORP" and (value < 600 or value > 800):
            _LOGGER.warning(
                "ORP-Sollwert %d außerhalb des üblichen Bereichs (600-800 mV). Fortfahren...",
                value
            )
            
        raw_query = f"{target_type},{value}"
        
        _LOGGER.debug(
            "set_target_value: type=%s, value=%s",
            target_type,
            value,
        )
        
        result = await self.api_request(
            endpoint=API_SET_TARGET_VALUES,
            raw_query=raw_query,
        )
        
        # Normalisiere das Ergebnis
        if isinstance(result, str):
            return {"response": result, "success": "OK" in result or "SUCCESS" in result}
        return result
    
    async def set_ph_target(self, value: float) -> Dict[str, Any]:
        """Setzt den pH-Sollwert.
        
        Args:
            value: Neuer pH-Sollwert
            
        Returns:
            Dict mit der Antwort vom Gerät
            
        Raises:
            VioletPoolConnectionError: Bei Verbindungsproblemen
            VioletPoolCommandError: Bei Fehlern bei der Befehlsausführung
        """
        # Validiere pH-Wert
        value = float(value)  # Sicherstellen, dass es ein Float ist
        
        # Normaler pH-Bereich ist 6.8 bis 7.8
        if value < 6.8 or value > 7.8:
            _LOGGER.warning(
                "pH-Sollwert %f außerhalb des üblichen Bereichs (6.8-7.8)",
                value
            )
            
        # Rundung auf 1 Dezimalstelle
        value = round(value, 1)
            
        return await self.set_target_value("pH", value)
    
    async def set_orp_target(self, value: int) -> Dict[str, Any]:
        """Setzt den Redox-Sollwert (ORP).
        
        Args:
            value: Neuer Redox-Sollwert in mV
            
        Returns:
            Dict mit der Antwort vom Gerät
            
        Raises:
            VioletPoolConnectionError: Bei Verbindungsproblemen
            VioletPoolCommandError: Bei Fehlern bei der Befehlsausführung
        """
        # Validiere Redox-Wert
        value = int(value)  # Sicherstellen, dass es ein Int ist
        
        # Normaler ORP-Bereich ist 600 bis 800 mV
        if value < 600 or value > 800:
            _LOGGER.warning(
                "ORP-Sollwert %d außerhalb des üblichen Bereichs (600-800 mV)",
                value
            )
            
        return await self.set_target_value("ORP", value)
    
    async def set_min_chlorine_level(self, value: float) -> Dict[str, Any]:
        """Setzt den minimalen Chlorgehalt.
        
        Args:
            value: Neuer minimaler Chlorgehalt in mg/l
            
        Returns:
            Dict mit der Antwort vom Gerät
            
        Raises:
            VioletPoolConnectionError: Bei Verbindungsproblemen
            VioletPoolCommandError: Bei Fehlern bei der Befehlsausführung
        """
        # Validiere Chlorwert
        value = float(value)
        
        # Normaler Chlorbereich ist ca. 0.3 bis 1.5 mg/l
        if value < 0.2 or value > 2.0:
            _LOGGER.warning(
                "Chlorgehalt %f außerhalb des üblichen Bereichs (0.2-2.0 mg/l)",
                value
            )
            
        # Rundung auf 1 Dezimalstelle
        value = round(value, 1)
            
        return await self.set_target_value("MinChlorine", value)
    
    async def set_max_chlorine_level_day(self, value: float) -> Dict[str, Any]:
        """Setzt den maximalen Chlorgehalt tagsüber.
        
        Args:
            value: Neuer maximaler Chlorgehalt tagsüber in mg/l
            
        Returns:
            Dict mit der Antwort vom Gerät
            
        Raises:
            VioletPoolConnectionError: Bei Verbindungsproblemen
            VioletPoolCommandError: Bei Fehlern bei der Befehlsausführung
        """
        # Validiere Chlorwert
        value = float(value)
        
        # Normaler Chlorbereich ist ca. 0.3 bis 1.5 mg/l
        if value < 0.5 or value > 3.0:
            _LOGGER.warning(
                "Chlorgehalt (Tag) %f außerhalb des üblichen Bereichs (0.5-3.0 mg/l)",
                value
            )
            
        # Rundung auf 1 Dezimalstelle
        value = round(value, 1)
            
        return await self.set_target_value("MaxChlorineDay", value)
    
    async def set_max_chlorine_level_night(self, value: float) -> Dict[str, Any]:
        """Setzt den maximalen Chlorgehalt nachts.
        
        Args:
            value: Neuer maximaler Chlorgehalt nachts in mg/l
            
        Returns:
            Dict mit der Antwort vom Gerät
            
        Raises:
            VioletPoolConnectionError: Bei Verbindungsproblemen
            VioletPoolCommandError: Bei Fehlern bei der Befehlsausführung
        """
        # Validiere Chlorwert
        value = float(value)
        
        # Normaler Chlorbereich ist ca. 0.3 bis 1.5 mg/l
        if value < 0.5 or value > 3.0:
            _LOGGER.warning(
                "Chlorgehalt (Nacht) %f außerhalb des üblichen Bereichs (0.5-3.0 mg/l)",
                value
            )
            
        # Rundung auf 1 Dezimalstelle
        value = round(value, 1)
            
        return await self.set_target_value("MaxChlorineNight", value)
    
    async def set_maintenance_mode(self, enabled: bool) -> Dict[str, Any]:
        """Aktiviert oder deaktiviert den Wartungsmodus.
        
        Args:
            enabled: True für aktivieren, False für deaktivieren
            
        Returns:
            Dict mit der Antwort vom Gerät
            
        Raises:
            VioletPoolConnectionError: Bei Verbindungsproblemen
            VioletPoolCommandError: Bei Fehlern bei der Befehlsausführung
        """
        action = "ON" if enabled else "OFF"
        return await self.set_switch_state("MAINTENANCE", action)
    
    async def start_water_analysis(self) -> Dict[str, Any]:
        """Startet eine Wasseranalyse.
        
        Returns:
            Dict mit der Antwort vom Gerät
            
        Raises:
            VioletPoolConnectionError: Bei Verbindungsproblemen
            VioletPoolCommandError: Bei Fehlern bei der Befehlsausführung
        """
        result = await self.api_request(endpoint="/startWaterAnalysis")
        
        # Normalisiere das Ergebnis
        if isinstance(result, str):
            return {"response": result, "success": "OK" in result or "SUCCESS" in result}
        return result
    
    async def get_dosing_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken zur Dosierung zurück.
        
        Returns:
            Dictionary mit Dosierungsstatistiken
            
        Raises:
            VioletPoolConnectionError: Bei Verbindungsproblemen
            VioletPoolCommandError: Bei Fehlern bei der Befehlsausführung
        """
        result = await self.api_request(endpoint="/getDosingStats")
        
        # Falls das Ergebnis ein String ist, versuche es als JSON zu parsen
        if isinstance(result, str):
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return {"raw_response": result}
                
        return result
        
    async def get_system_info(self) -> Dict[str, Any]:
        """Ruft Systeminformationen ab.
        
        Returns:
            Dictionary mit Systeminformationen
            
        Raises:
            VioletPoolConnectionError: Bei Verbindungsproblemen
            VioletPoolCommandError: Bei Fehlern bei der Befehlsausführung
        """
        result = await self.api_request(endpoint="/getSystemInfo")
        
        # Falls das Ergebnis ein String ist, versuche es als JSON zu parsen
        if isinstance(result, str):
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return {"raw_response": result}
                
        return result
