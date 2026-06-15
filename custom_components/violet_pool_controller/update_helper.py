# =============================================================================
# Violet Pool Controller – Firmware Update Helper
# Copyright © 2026 Xerolux
# =============================================================================

"""Firmware update checking helpers for Violet Pool Controller."""

from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


class FirmwareUpdateInfo:
    """Tracks available firmware updates."""

    def __init__(
        self,
        installed_version: str,
        available_version: str | None = None,
        carrier_version: str | None = None,
        release_notes: str | None = None,
    ):
        self.installed_version = installed_version
        self.available_version = available_version
        self.carrier_version = carrier_version
        self.release_notes = release_notes

    @property
    def update_available(self) -> bool:
        """Return True when a newer version is available."""
        if not self.available_version:
            return False
        return self._compare_versions(self.installed_version, self.available_version) < 0

    @property
    def update_description(self) -> str:
        """Human-readable update status line."""
        if not self.update_available:
            return f"System is up to date (v{self.installed_version})"
        return (
            f"Update available: v{self.available_version}"
            f" (installed: v{self.installed_version})"
        )

    @staticmethod
    def _compare_versions(current: str, available: str) -> int:
        """Return -1/0/1 for current < / == / > available."""
        try:
            cp = [int(x) for x in current.split(".")]
            ap = [int(x) for x in available.split(".")]
            n = max(len(cp), len(ap))
            cp += [0] * (n - len(cp))
            ap += [0] * (n - len(ap))
            for c, a in zip(cp, ap):
                if c < a:
                    return -1
                if c > a:
                    return 1
            return 0
        except (ValueError, AttributeError):
            return 0


def parse_firmware_info(raw_data: dict[str, Any]) -> FirmwareUpdateInfo:
    """Parse firmware info from getReadings data.

    The controller exposes two relevant keys in the getReadings response:
      SYSTEM_swversion       – currently installed version (e.g. "1.2.0")
      SYSTEM_availableversion – version available for download (empty when
                                up-to-date or when the controller has not yet
                                contacted the update server)
    """
    installed = str(raw_data.get("SYSTEM_swversion", "") or "").strip() or "0.0.0"

    available_raw = str(raw_data.get("SYSTEM_availableversion", "") or "").strip()
    available: str | None = available_raw if available_raw and available_raw != installed else None

    carrier = str(raw_data.get("SYSTEM_carrierboard_swversion", "") or "").strip() or None

    return FirmwareUpdateInfo(
        installed_version=installed,
        available_version=available,
        carrier_version=carrier,
    )
