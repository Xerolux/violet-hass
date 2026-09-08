"""Parity between services.yaml, the registered services and their schemas.

A service that is registered but missing from ``services.yaml`` shows up in
Developer Tools without a description or a single field; a service described in
``services.yaml`` that nobody registers is a dead entry in the UI.  A schema
that demands a target while the YAML offers no way to pick one makes the
service impossible to call from the UI at all.  All three used to be true for
this integration, so they are asserted here.
"""

from __future__ import annotations

import json
from pathlib import Path

import homeassistant.helpers.config_validation as cv
import pytest
import voluptuous as vol
import yaml

from custom_components.violet_pool_controller.service_schemas import get_service_schemas

COMPONENT_DIR = Path(__file__).parent.parent / "custom_components" / "violet_pool_controller"
SERVICES_YAML = COMPONENT_DIR / "services.yaml"
STRINGS_JSON = COMPONENT_DIR / "strings.json"
SERVICES_PY = COMPONENT_DIR / "services.py"

# Keys a ``target:`` block supplies instead of a ``fields:`` entry - the five
# entity-service fields plus the frontend's own ``metadata`` bucket.
TARGET_KEYS = frozenset(
    {str(key) for key in cv.ENTITY_SERVICE_FIELDS} | {"metadata"}
)
# The two of those a service may also expose as an ordinary field.
PICKER_KEYS = frozenset({"device_id", "entity_id"})


def _load_yaml() -> dict[str, dict]:
    """Return the parsed services.yaml."""
    return yaml.safe_load(SERVICES_YAML.read_text(encoding="utf-8"))


def _load_strings_services() -> dict[str, dict]:
    """Return the ``services`` block of strings.json."""
    return json.loads(STRINGS_JSON.read_text(encoding="utf-8"))["services"]


def _registered_service_names() -> set[str]:
    """Return every service name ``async_register_services`` registers.

    The registration table and the individual ``async_register`` calls both
    name the service as a plain string literal, so the names are read from the
    module's own registration data rather than from a running Home Assistant.
    """
    from custom_components.violet_pool_controller import services as services_module

    return set(services_module.SERVICE_HANDLER_NAMES)


def _schema_keys(schema: object) -> set[str]:
    """Collect every literal string key a Voluptuous schema accepts."""
    keys: set[str] = set()
    if isinstance(schema, vol.Schema):
        return _schema_keys(schema.schema)
    if isinstance(schema, vol.All):
        for validator in schema.validators:
            keys |= _schema_keys(validator)
        return keys
    if isinstance(schema, dict):
        for key in schema:
            marker = key.schema if isinstance(key, vol.Marker) else key
            if isinstance(marker, str):
                keys.add(marker)
        return keys
    return keys


YAML_SERVICES = _load_yaml()
SCHEMAS = get_service_schemas()
REGISTERED = _registered_service_names()


def test_registered_services_match_yaml() -> None:
    """Every registered service is described in services.yaml and vice versa."""
    assert set(YAML_SERVICES) == REGISTERED


def test_registered_services_match_strings_json() -> None:
    """Every registered service has a name/description in strings.json."""
    assert set(_load_strings_services()) == REGISTERED


@pytest.mark.parametrize("service_name", sorted(REGISTERED))
def test_service_offers_a_way_to_pick_a_target(service_name: str) -> None:
    """A schema that requires a target must give the UI a way to supply one."""
    schema = SCHEMAS.get(service_name)
    if schema is None:
        pytest.skip(f"{service_name} has no schema")
    keys = _schema_keys(schema)
    if not keys & TARGET_KEYS:
        return

    entry = YAML_SERVICES[service_name]
    has_target = "target" in entry
    has_field = bool(PICKER_KEYS & set(entry.get("fields") or {}))
    assert has_target or has_field, (
        f"{service_name} requires a device_id/entity_id but services.yaml offers "
        "neither a target: block nor a device_id/entity_id field, so a UI call "
        "can never satisfy the schema"
    )


@pytest.mark.parametrize("service_name", sorted(YAML_SERVICES))
def test_target_block_is_hassfest_valid(service_name: str) -> None:
    """Hassfest rejects a filtered ``device:`` target on a service.

    "Services do not support device filters on target, use a device selector
    instead" - only an ``entity:`` filter or a bare ``device: {}`` passes.
    """
    target = YAML_SERVICES[service_name].get("target")
    if target is None:
        return
    for kind, selector in target.items():
        if kind == "device":
            assert not selector, (
                f"{service_name}: a device target may not carry a filter; "
                "use an entity: filter or a bare device: {}"
            )
        else:
            assert kind == "entity", f"{service_name}: unknown target kind {kind!r}"


@pytest.mark.parametrize("service_name", sorted(REGISTERED))
def test_yaml_fields_match_schema_keys(service_name: str) -> None:
    """The fields offered in the UI are exactly the keys the schema accepts."""
    schema = SCHEMAS.get(service_name)
    if schema is None:
        pytest.skip(f"{service_name} has no schema")
    entry = YAML_SERVICES[service_name]
    yaml_fields = set(entry.get("fields") or {}) - TARGET_KEYS
    assert yaml_fields == _schema_keys(schema) - TARGET_KEYS


@pytest.mark.parametrize("service_name", sorted(REGISTERED))
def test_strings_fields_match_yaml_fields(service_name: str) -> None:
    """Every YAML field has a translated name, and no stale ones remain."""
    entry = YAML_SERVICES[service_name]
    strings_entry = _load_strings_services()[service_name]
    assert set(strings_entry.get("fields") or {}) == set(entry.get("fields") or {})
