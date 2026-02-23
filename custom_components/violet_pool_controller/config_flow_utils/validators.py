"""Config Flow Validators."""

import ipaddress
import logging
import re
from typing import Any

_LOGGER = logging.getLogger(__name__)

# Pre-compiled numeric pattern for performance
NUMERIC_PATTERN = re.compile(r"^-?\d+$")


def validate_ip_address(ip: str) -> bool:
    """
    Validate IP address or hostname.

    Args:
        ip: The IP address or hostname to validate.

    Returns:
        True if valid, False otherwise.
    """
    if not ip:
        return False
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        # Allow hostnames (letters, numbers, dots, dashes)
        return bool(re.match(r"^[a-zA-Z0-9\-\.]+$", ip))


def get_sensor_label(key: str, all_sensors: dict[str, Any] | None = None) -> str:
    """
    Get the friendly name for a sensor key.

    Args:
        key: The sensor key.
        all_sensors: Optional dictionary of all sensors for friendly name lookup.

    Returns:
        The friendly name with key.
    """
    if all_sensors and key in all_sensors:
        return f"{all_sensors[key]['name']} ({key})"
    return key


def validate_credentials_strength(username: str | None, password: str | None) -> None:
    """
    Check credentials against basic security policies.

    Args:
        username: The username.
        password: The password.

    Note:
        This is a basic check. In production, implement proper password validation.
    """
    # It's okay to have no auth, but if username is present, password should be checked
    # For now, just a placeholder.
    pass
