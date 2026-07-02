# violet-poolController-api - API für Violet Pool Controller
# Copyright (C) 2024-2026  Xerolux
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Input Sanitization Utilities für User-Inputs und API-Parameter."""

from __future__ import annotations

import logging
import math
import re
import unicodedata
from html import escape
from typing import Any

_LOGGER = logging.getLogger(__name__)

_MAX_DEVICE_KEY_LENGTH = 50
_MAX_API_PARAM_LENGTH = 100


class InputSanitizer:
    """Input Sanitization für Sicherheit und Datenintegrität.

    Schützt vor:
    - XSS (Cross-Site Scripting)
    - SQL Injection (nicht relevant bei HTTP API, aber defensiv)
    - Command Injection
    - Path Traversal
    - Unerwarteten Zeichen
    """

    # Erlaubte Zeichen-Patterns
    ALPHANUMERIC = re.compile(r"^[a-zA-Z0-9]+$")
    ALPHANUMERIC_UNDERSCORE = re.compile(r"^[a-zA-Z0-9_]+$")
    ALPHANUMERIC_DASH_UNDERSCORE = re.compile(r"^[a-zA-Z0-9_-]+$")
    NUMERIC = re.compile(r"^-?[0-9]+(\.[0-9]+)?$")
    INTEGER = re.compile(r"^-?[0-9]+$")
    FLOAT = re.compile(r"^-?[0-9]+\.[0-9]+$")

    # Gefährliche Patterns
    DANGEROUS_CHARS = re.compile(r'[<>&"\';\\]')
    PATH_TRAVERSAL = re.compile(r"\.\.|/|\\")
    COMMAND_INJECTION = re.compile(r"[;&|`$(){}[\]]")

    @staticmethod
    def sanitize_string(
        value: Any,  # noqa: ANN401
        max_length: int = 255,
        *,
        allow_special_chars: bool = False,
        escape_html: bool = True,
    ) -> str:
        """Sanitize einen String-Wert.

        Args:
            value: Zu sanitisierender Wert
            max_length: Maximale Länge
            allow_special_chars: Erlaube Sonderzeichen (sonst nur alphanumerisch)
            escape_html: HTML-Escape durchführen

        Returns:
            Sanitisierter String

        Raises:
            ValueError: Bei ungültigen Eingaben

        """
        if value is None:
            return ""

        # Konvertiere zu String
        str_value = str(value).strip()

        # Unicode-Normalisierung (NFKD für Defense-in-Depth)
        # Normalized Form Compatibility Decomposition
        str_value = unicodedata.normalize("NFKD", str_value)

        # Längen-Validierung
        if len(str_value) > max_length:
            _LOGGER.warning(
                "String zu lang (%d > %d), wird gekürzt: %s...",
                len(str_value),
                max_length,
                str_value[:50],
            )
            str_value = str_value[:max_length]

        if not allow_special_chars:
            original = str_value
            str_value = re.sub(r"[^a-zA-Z0-9 _-]", "", str_value)
            if str_value != original:
                _LOGGER.warning(
                    "Gefährliche Zeichen entfernt: '%s' → '%s'",
                    original,
                    str_value,
                )
        if escape_html:
            str_value = escape(str_value)

        return str_value

    @staticmethod
    def sanitize_numeric(value: Any) -> float:  # noqa: ANN401
        """Sanitize a numeric value.

        Args:
            value: Zu sanitisierender numerischer Wert

        Returns:
            Sanierte Fließkommazahl

        """
        try:
            if isinstance(value, (int, float)):
                if not math.isfinite(float(value)):
                    _LOGGER.warning("Unendlicher/NaN-Wert: %s", value)
                    return 0.0
                return float(value)

            str_value = str(value).strip()
            has_minus = str_value.startswith("-")
            cleaned = re.sub(r"[^0-9.]", "", str_value)
            if has_minus and cleaned:
                cleaned = "-" + cleaned

            if not cleaned:
                return 0.0

            return float(cleaned)
        except (ValueError, TypeError, OverflowError):
            _LOGGER.warning("Ungültiger numerischer Wert: %s", value)
            return 0.0

    @staticmethod
    def sanitize_integer(
        value: Any,  # noqa: ANN401
        min_value: int | None = None,
        max_value: int | None = None,
        default: int = 0,
    ) -> int:
        """Sanitize einen Integer-Wert.

        Args:
            value: Zu sanitisierender Wert
            min_value: Minimaler erlaubter Wert
            max_value: Maximaler erlaubter Wert
            default: Default-Wert bei Fehler

        Returns:
            Sanitisierter Integer

        """
        try:
            try:
                int_value = int(value)
            except (ValueError, TypeError, OverflowError):
                int_value = int(float(value))

            # Range-Validierung
            if min_value is not None and int_value < min_value:
                _LOGGER.warning(
                    "Integer-Wert %d < min %d, verwende min",
                    int_value,
                    min_value,
                )
                return min_value

            if max_value is not None and int_value > max_value:
                _LOGGER.warning(
                    "Integer-Wert %d > max %d, verwende max",
                    int_value,
                    max_value,
                )
                return max_value

        except (ValueError, TypeError) as err:
            _LOGGER.warning(
                "Ungültiger Integer-Wert '%s', verwende default %d: %s",
                value,
                default,
                err,
            )
            return default
        else:
            return int_value

    @staticmethod
    def sanitize_float(
        value: Any,  # noqa: ANN401
        min_value: float | None = None,
        max_value: float | None = None,
        precision: int = 2,
        default: float = 0.0,
    ) -> float:
        """Sanitize einen Float-Wert.

        Args:
            value: Zu sanitisierender Wert
            min_value: Minimaler erlaubter Wert
            max_value: Maximaler erlaubter Wert
            precision: Dezimalstellen-Präzision
            default: Default-Wert bei Fehler

        Returns:
            Sanitisierter Float

        """
        try:
            float_value = float(value)

            # Range-Validierung
            if min_value is not None and float_value < min_value:
                _LOGGER.warning(
                    "Float-Wert %.2f < min %.2f, verwende min",
                    float_value,
                    min_value,
                )
                return min_value

            if max_value is not None and float_value > max_value:
                _LOGGER.warning(
                    "Float-Wert %.2f > max %.2f, verwende max",
                    float_value,
                    max_value,
                )
                return max_value

            # Präzision
            return round(float_value, precision)

        except (ValueError, TypeError) as err:
            _LOGGER.warning(
                "Ungültiger Float-Wert '%s', verwende default %.2f: %s",
                value,
                default,
                err,
            )
            return default

    @staticmethod
    def sanitize_boolean(value: Any, *, default: bool = False) -> bool:  # noqa: ANN401
        """Sanitize einen Boolean-Wert.

        Args:
            value: Zu sanitisierender Wert
            default: Default-Wert bei Fehler

        Returns:
            Sanitisierter Boolean

        """
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            lower_value = value.lower().strip()
            if lower_value in {"true", "1", "yes", "on", "enabled"}:
                return True
            if lower_value in {"false", "0", "no", "off", "disabled"}:
                return False

        if isinstance(value, (int, float)):
            return bool(value)

        _LOGGER.warning(
            "Ungültiger Boolean-Wert '%s', verwende default %s",
            value,
            default,
        )
        return default

    @staticmethod
    def validate_device_key(key: str) -> str:
        """Validiere einen Device-Key (z.B. PUMP, HEATER, etc.).

        Args:
            key: Device-Key

        Returns:
            Validierter Key

        Raises:
            ValueError: Bei ungültigem Key

        """
        if not key:
            msg = "Device-Key darf nicht leer sein"
            raise ValueError(msg)

        # Nur Großbuchstaben, Zahlen und Underscore erlaubt
        # Wir erlauben auch Bindestriche und konvertieren sie zu Underscores
        key = key.upper().replace("-", "_")
        sanitized = re.sub(r"[^A-Z0-9_]", "", key)

        if sanitized != key:
            _LOGGER.warning(
                "Device-Key enthielt ungültige Zeichen: '%s' → '%s'",
                key,
                sanitized,
            )

        if len(sanitized) > _MAX_DEVICE_KEY_LENGTH:
            msg = f"Device-Key zu lang: {len(sanitized)} > {_MAX_DEVICE_KEY_LENGTH}"
            raise ValueError(msg)

        return sanitized

    @staticmethod
    def validate_api_parameter(param: str) -> str:
        """Validiere einen API-Parameter-Namen.

        Args:
            param: Parameter-Name

        Returns:
            Validierter Parameter

        Raises:
            ValueError: Bei ungültigem Parameter oder Path Traversal

        """
        if not param:
            msg = "API-Parameter darf nicht leer sein"
            raise ValueError(msg)

        # Prüfe auf Path Traversal VOR der Bereinigung
        if InputSanitizer.PATH_TRAVERSAL.search(param):
            msg = f"Path Traversal erkannt in Parameter: {param}"
            raise ValueError(msg)

        # Entferne gefährliche Zeichen
        sanitized = re.sub(r"[^a-zA-Z0-9_-]", "", param)

        if sanitized != param:
            _LOGGER.warning(
                "API-Parameter enthielt ungültige Zeichen: '%s' → '%s'",
                param,
                sanitized,
            )

        if len(sanitized) > _MAX_API_PARAM_LENGTH:
            msg = f"API-Parameter zu lang: {len(sanitized)} > {_MAX_API_PARAM_LENGTH}"
            raise ValueError(msg)

        return sanitized

    @staticmethod
    def validate_duration(duration: Any, min_sec: int = 0, max_sec: int = 86400) -> int:  # noqa: ANN401
        """Validiere eine Duration in Sekunden.

        Args:
            duration: Duration-Wert
            min_sec: Minimale Duration (Standard: 0)
            max_sec: Maximale Duration (Standard: 24h)

        Returns:
            Validierte Duration in Sekunden

        """
        duration_int = InputSanitizer.sanitize_integer(
            duration,
            min_value=min_sec,
            max_value=max_sec,
            default=0,
        )

        if duration_int < 0:
            _LOGGER.warning("Negative Duration %d, setze auf 0", duration_int)
            return 0

        return duration_int

    @staticmethod
    def validate_speed(
        speed: Any,
        min_speed: int = 1,
        max_speed: int = 4,
        default: int = 2,  # noqa: ANN401
    ) -> int:
        """Validiere einen Speed-Wert (z.B. Pumpengeschwindigkeit).

        Args:
            speed: Speed-Wert
            min_speed: Minimale Speed (Standard: 1)
            max_speed: Maximale Speed (Standard: 4)
            default: Default Speed (Standard: 2)

        Returns:
            Validierte Speed

        """
        return InputSanitizer.sanitize_integer(
            speed,
            min_value=min_speed,
            max_value=max_speed,
            default=default,
        )

    @staticmethod
    def validate_temperature(
        temp: Any,  # noqa: ANN401
        min_temp: float = -50.0,
        max_temp: float = 100.0,
    ) -> float:
        """Validiere einen Temperatur-Wert.

        Args:
            temp: Temperatur-Wert
            min_temp: Minimale Temperatur
            max_temp: Maximale Temperatur

        Returns:
            Validierte Temperatur

        """
        return InputSanitizer.sanitize_float(
            temp,
            min_value=min_temp,
            max_value=max_temp,
            precision=1,
            default=20.0,
        )

    @staticmethod
    def validate_ph_value(ph: Any) -> float:  # noqa: ANN401
        """Validiere einen pH-Wert.

        Args:
            ph: pH-Wert

        Returns:
            Validierter pH-Wert (6.0-9.0)

        """
        return InputSanitizer.sanitize_float(
            ph,
            min_value=6.0,
            max_value=9.0,
            precision=1,
            default=7.2,
        )

    @staticmethod
    def validate_orp_value(orp: Any) -> int:  # noqa: ANN401
        """Validiere einen ORP-Wert (Redoxpotential).

        Args:
            orp: ORP-Wert in mV

        Returns:
            Validierter ORP-Wert (500-900 mV)

        """
        return InputSanitizer.sanitize_integer(
            orp,
            min_value=500,
            max_value=900,
            default=700,
        )

    @staticmethod
    def validate_chlorine_level(chlorine: Any) -> float:  # noqa: ANN401
        """Validiere einen Chlor-Wert.

        Args:
            chlorine: Chlor-Wert in mg/l

        Returns:
            Validierter Chlor-Wert (0.0-5.0 mg/l)

        """
        return InputSanitizer.sanitize_float(
            chlorine,
            min_value=0.0,
            max_value=5.0,
            precision=1,
            default=0.6,
        )


# Singleton-Instanz für einfachen Zugriff
_sanitizer = InputSanitizer()


def sanitize_string(*args: Any, **kwargs: Any) -> str:  # noqa: ANN401
    """Shortcut für InputSanitizer.sanitize_string()."""
    return _sanitizer.sanitize_string(*args, **kwargs)


def sanitize_integer(*args: Any, **kwargs: Any) -> int:  # noqa: ANN401
    """Shortcut für InputSanitizer.sanitize_integer()."""
    return _sanitizer.sanitize_integer(*args, **kwargs)


def sanitize_float(*args: Any, **kwargs: Any) -> float:  # noqa: ANN401
    """Shortcut für InputSanitizer.sanitize_float()."""
    return _sanitizer.sanitize_float(*args, **kwargs)


def sanitize_boolean(*args: Any, **kwargs: Any) -> bool:  # noqa: ANN401
    """Shortcut für InputSanitizer.sanitize_boolean()."""
    return _sanitizer.sanitize_boolean(*args, **kwargs)


__all__ = [
    "InputSanitizer",
    "sanitize_boolean",
    "sanitize_float",
    "sanitize_integer",
    "sanitize_string",
]
