"""Shared helpers for extracting and normalizing config entry values."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.config_entries import ConfigEntry

from .const import CONF_API_URL


def get_entry_value(entry: ConfigEntry, key: str, default: Any) -> Any:
    """Read option value first, then fallback to data and finally default."""
    return entry.options.get(key, entry.data.get(key, default))


def extract_api_host(entry_data: Mapping[str, Any]) -> str:
    """Extract and normalize API host from current and legacy keys."""
    host = entry_data.get(CONF_API_URL) or entry_data.get("host") or entry_data.get("base_ip")
    if not host:
        raise ValueError("No IP address found in config entry")
    if not isinstance(host, str):
        raise ValueError("API URL is not a string")
    return host.strip()


def normalize_host(host_or_url: str | None) -> str | None:
    """Normalize a host, URL, or hostname string to a canonical host token.

    Strips http(s):// schemes, paths, ports, trailing dots, and surrounding whitespace.
    Converts to lowercase.
    """
    if not host_or_url or not isinstance(host_or_url, str):
        return None
    cleaned = host_or_url.strip().lower()
    if not cleaned:
        return None

    # Remove protocol prefix
    if "://" in cleaned:
        cleaned = cleaned.split("://", 1)[1]

    # Remove path / query / fragment
    if "/" in cleaned:
        cleaned = cleaned.split("/", 1)[0]

    # Remove port if present (handle ipv6 [::1]:80 and ipv4/host 1.2.3.4:80)
    if cleaned.startswith("[") and "]" in cleaned:
        cleaned = cleaned[1:].split("]", 1)[0]
    elif ":" in cleaned and cleaned.count(":") == 1:
        cleaned = cleaned.split(":", 1)[0]

    # Remove trailing dot from FQDN (e.g. violet.local. -> violet.local)
    cleaned = cleaned.rstrip(".")
    return cleaned or None


def with_non_default_port(host: str, port: int) -> str:
    """Append port to host for non-default HTTP/HTTPS ports."""
    if port in (80, 443):
        return host
    return f"{host}:{port}"

