# =============================================================================
# Violet Pool Controller – Firmware Update Helper
# Copyright © 2026 Xerolux
# =============================================================================

"""Firmware update checking helpers for Violet Pool Controller."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from awesomeversion import AwesomeVersion, AwesomeVersionException

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
        return f"Update available: v{self.available_version} (installed: v{self.installed_version})"

    @staticmethod
    def _compare_versions(current: str, available: str) -> int:
        """Return -1/0/1 for current < / == / > available.

        Comparison goes through ``AwesomeVersion`` (shipped with Home
        Assistant) so pre-release and suffixed firmware versions such as
        ``1.2.0-beta`` are ordered instead of collapsing to "equal", which used
        to hide every update involving them.
        """
        if current == available:
            return 0

        try:
            left = AwesomeVersion(current)
            right = AwesomeVersion(available)
            if left < right:
                return -1
            if left > right:
                return 1
            return 0
        except (AwesomeVersionException, AttributeError, TypeError, ValueError):
            # Two strings that differ but cannot be ordered: the controller
            # only advertises an available version when it has one, so report
            # the update rather than swallowing it.
            _LOGGER.debug(
                "Could not compare firmware versions %r and %r; assuming an update",
                current,
                available,
            )
            return -1


def parse_firmware_info(raw_data: Mapping[str, Any]) -> FirmwareUpdateInfo:
    """Parse firmware info from getReadings data.

    The controller exposes firmware version information under two possible sets
    of keys depending on firmware generation:

    Newer firmware:
      SYSTEM_swversion        – currently installed version (e.g. "1.2.0")
      SYSTEM_availableversion – version available for download (empty when
                                up-to-date or when the controller hasn't yet
                                contacted the update server)

    Older / current spec firmware:
      SW_VERSION              – currently installed version
      SW_UPDATE_AVAILABLE     – version available for download
      SW_VERSION_CARRIER      – carrier board firmware version
    """
    installed = (
        str(raw_data.get("SYSTEM_swversion", "") or "").strip()
        or str(raw_data.get("SW_VERSION", "") or "").strip()
        or "0.0.0"
    )

    available_raw = (
        str(raw_data.get("SYSTEM_availableversion", "") or "").strip()
        or str(raw_data.get("SW_UPDATE_AVAILABLE", "") or "").strip()
    )
    available: str | None = available_raw if available_raw and available_raw != installed else None

    carrier = (
        str(raw_data.get("SYSTEM_carrierboard_swversion", "") or "").strip()
        or str(raw_data.get("SW_VERSION_CARRIER", "") or "").strip()
        or None
    )

    return FirmwareUpdateInfo(
        installed_version=installed,
        available_version=available,
        carrier_version=carrier,
    )
