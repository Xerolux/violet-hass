# =============================================================================
# Violet Pool Controller – Calibration Helper
# Copyright © 2026 Xerolux
# =============================================================================

"""Calibration management and monitoring for sensors."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

# Standard sensor calibration intervals (days)
CALIBRATION_INTERVALS = {
    "pH": 30,  # pH sensors: monthly
    "ORP": 30,  # ORP sensors: monthly
    "conductivity": 60,  # Conductivity: every 2 months
    "temperature": 90,  # Temperature: every 3 months
    "flow": 90,  # Flow rate: every 3 months
}

# Warning thresholds (days overdue)
CALIBRATION_WARNING_DAYS = 7  # Warning after 7 days overdue
CALIBRATION_CRITICAL_DAYS = 30  # Critical after 30 days overdue


class CalibrationStatus:
    """Tracks calibration status for a sensor."""

    def __init__(
        self,
        sensor_type: str,
        last_calibration: datetime | None = None,
        offset: float = 0.0,
        multiplier: float = 1.0,
    ):
        """
        Initialize calibration status.

        Args:
            sensor_type: Type of sensor (pH, ORP, conductivity, etc.)
            last_calibration: Last calibration date
            offset: Calibration offset value
            multiplier: Calibration multiplier value
        """
        self.sensor_type = sensor_type
        self.last_calibration = last_calibration
        self.offset = offset
        self.multiplier = multiplier

    @property
    def days_since_calibration(self) -> int | None:
        """Days since last calibration."""
        if not self.last_calibration:
            return None
        return (datetime.now() - self.last_calibration).days

    @property
    def is_expired(self) -> bool:
        """Check if calibration is expired."""
        days = self.days_since_calibration
        if days is None:
            return True
        interval = CALIBRATION_INTERVALS.get(self.sensor_type, 90)
        return days > interval

    @property
    def is_warning(self) -> bool:
        """Check if calibration is approaching expiration."""
        days = self.days_since_calibration
        if days is None:
            return True
        interval = CALIBRATION_INTERVALS.get(self.sensor_type, 90)
        days_left = interval - days
        return 0 < days_left <= CALIBRATION_WARNING_DAYS

    @property
    def status(self) -> str:
        """Get calibration status string."""
        if not self.last_calibration:
            return "Unknown"
        if self.is_expired:
            return "Expired"
        if self.is_warning:
            return "Warning"
        return "OK"

    @property
    def next_calibration_date(self) -> datetime | None:
        """Expected next calibration date."""
        if not self.last_calibration:
            return None
        interval = CALIBRATION_INTERVALS.get(self.sensor_type, 90)
        return self.last_calibration + timedelta(days=interval)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "sensor_type": self.sensor_type,
            "last_calibration": self.last_calibration.isoformat()
            if self.last_calibration
            else None,
            "days_since": self.days_since_calibration,
            "status": self.status,
            "is_expired": self.is_expired,
            "is_warning": self.is_warning,
            "offset": self.offset,
            "multiplier": self.multiplier,
            "next_calibration": self.next_calibration_date.isoformat()
            if self.next_calibration_date
            else None,
        }


def parse_calibration_data(raw_data: dict[str, Any]) -> dict[str, CalibrationStatus]:
    """
    Parse calibration data from controller response.

    Args:
        raw_data: Raw data from controller

    Returns:
        Dictionary of sensor -> CalibrationStatus
    """
    calibrations = {}

    # pH calibration
    if "PH_calibration_date" in raw_data:
        calibrations["pH"] = CalibrationStatus(
            sensor_type="pH",
            last_calibration=_parse_date(raw_data.get("PH_calibration_date")),
            offset=float(raw_data.get("PH_offset", 0.0)),
            multiplier=float(raw_data.get("PH_multiplier", 1.0)),
        )

    # ORP calibration
    if "ORP_calibration_date" in raw_data:
        calibrations["ORP"] = CalibrationStatus(
            sensor_type="ORP",
            last_calibration=_parse_date(raw_data.get("ORP_calibration_date")),
            offset=float(raw_data.get("ORP_offset", 0.0)),
            multiplier=float(raw_data.get("ORP_multiplier", 1.0)),
        )

    # Conductivity calibration
    if "COND_calibration_date" in raw_data:
        calibrations["conductivity"] = CalibrationStatus(
            sensor_type="conductivity",
            last_calibration=_parse_date(raw_data.get("COND_calibration_date")),
            offset=float(raw_data.get("COND_offset", 0.0)),
            multiplier=float(raw_data.get("COND_multiplier", 1.0)),
        )

    return calibrations


def _parse_date(date_str: str | None) -> datetime | None:
    """Parse date string from controller."""
    if not date_str:
        return None

    # Try common formats
    formats = [
        "%d.%m.%Y",  # DD.MM.YYYY
        "%Y-%m-%d",  # YYYY-MM-DD
        "%d/%m/%Y",  # DD/MM/YYYY
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    # If no format matches, return None
    return None
