# =============================================================================
# Violet Pool Controller – Firmware Update Helper
# Copyright © 2026 Xerolux
# =============================================================================

"""Firmware update checking and installation for Violet Pool Controller."""

from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)

KNOWN_LATEST_FIRMWARE_VERSION = "1.2.0"


class FirmwareUpdateInfo:
    """Tracks available firmware updates."""

    def __init__(
        self,
        installed_version: str,
        available_version: str | None = None,
        carrier_version: str | None = None,
        release_notes: str | None = None,
        installed_date: str | None = None,
    ):
        """
        Initialize firmware update info.

        Args:
            installed_version: Currently installed version (e.g., "1.1.9")
            available_version: Available version for update (e.g., "1.2.0")
            carrier_version: Carrier firmware version
            release_notes: Release notes/changelog
            installed_date: Installation date of current version
        """
        self.installed_version = installed_version
        self.available_version = available_version
        self.carrier_version = carrier_version
        self.release_notes = release_notes
        self.installed_date = installed_date

    @property
    def update_available(self) -> bool:
        """Check if update is available."""
        if not self.available_version:
            return False
        return self._compare_versions(self.installed_version, self.available_version) < 0

    @property
    def update_description(self) -> str:
        """Get human-readable update description."""
        if not self.update_available:
            return f"System is up to date (v{self.installed_version})"
        return f"Update available: v{self.available_version} (Installed: v{self.installed_version})"

    @property
    def release_notes_html(self) -> str:
        """Format release notes for HA."""
        if not self.release_notes:
            return "No release notes available"
        # Format markdown-like text from controller
        lines = []
        for line in self.release_notes.split("\n"):
            line = line.strip()
            if line.startswith("•"):
                # Bullet point
                lines.append(f"• {line[1:].strip()}")
            elif line.startswith("FIXES:"):
                lines.append("**FIXES:**")
            elif line.startswith("FEATURES:"):
                lines.append("**FEATURES:**")
            elif line:
                lines.append(line)
        return "\n".join(lines)

    @staticmethod
    def _compare_versions(current: str, available: str) -> int:
        """
        Compare semantic versions.

        Returns:
            -1 if current < available
            0 if current == available
            1 if current > available
        """
        try:
            current_parts = [int(x) for x in current.split(".")]
            available_parts = [int(x) for x in available.split(".")]

            # Pad with zeros if lengths differ
            max_len = max(len(current_parts), len(available_parts))
            current_parts += [0] * (max_len - len(current_parts))
            available_parts += [0] * (max_len - len(available_parts))

            for c, a in zip(current_parts, available_parts):
                if c < a:
                    return -1
                elif c > a:
                    return 1
            return 0
        except (ValueError, AttributeError):
            return 0


def parse_firmware_info(raw_data: dict[str, Any]) -> FirmwareUpdateInfo:
    """
    Parse firmware update info from controller response.

    Args:
        raw_data: Raw data from controller

    Returns:
        FirmwareUpdateInfo instance
    """
    installed = raw_data.get("SW_VERSION", "1.0.0")
    available = (
        raw_data.get("SW_UPDATE_AVAILABLE")
        or raw_data.get("SYSTEM_UPDATE_AVAILABLE_VERSION")
        or raw_data.get("SW_LATEST_VERSION")
        or raw_data.get("LATEST_SW_VERSION")
    )
    if isinstance(available, bool):
        available = KNOWN_LATEST_FIRMWARE_VERSION if available else None
    if not available and FirmwareUpdateInfo._compare_versions(
        str(installed), KNOWN_LATEST_FIRMWARE_VERSION
    ) < 0:
        available = KNOWN_LATEST_FIRMWARE_VERSION
    carrier = raw_data.get("SW_VERSION_CARRIER")
    release_notes = raw_data.get("SW_RELEASE_NOTES")
    installed_date = raw_data.get("SW_INSTALL_DATE")

    return FirmwareUpdateInfo(
        installed_version=installed,
        available_version=available,
        carrier_version=carrier,
        release_notes=release_notes,
        installed_date=installed_date,
    )
