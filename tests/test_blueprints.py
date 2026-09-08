"""Validate the shipped blueprints against Home Assistant's own schema.

Blueprints are plain YAML that nothing in the build ever loaded, so a typo only
surfaced when a user tried to import one. These tests parse every blueprint the
way Home Assistant does, and additionally substitute example inputs into the
heat-pump blueprint so its triggers, conditions and actions are validated as a
real automation would be.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from homeassistant.components.automation.config import AUTOMATION_BLUEPRINT_SCHEMA
from homeassistant.components.blueprint import models
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.util.yaml import loader

from custom_components.violet_pool_controller.climate import (
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
)

REPO = Path(__file__).parent.parent
BLUEPRINT_DIR = REPO / "blueprints" / "automation"
HEAT_PUMP_BLUEPRINT = BLUEPRINT_DIR / "pool_heatpump_cooling.yaml"

# Inputs for the heat-pump blueprint, as a user would fill them in.
HEAT_PUMP_INPUTS = {
    "pool_temperature_sensor": "sensor.violet_pool_temperature",
    "heat_pump": "climate.heat_pump",
    "target_temperature_helper": "input_number.pool_target",
    "hysteresis": 0.5,
    "cooling_enabled": True,
    "idle_mode": "auto",
    "violet_heater": "climate.violet_heater",
    "release_temperature": 35,
    "enable_switch": "input_boolean.pool_control",
    "notification_entity": "notify.mobile_app_phone",
}


def _minimum_home_assistant_version() -> str:
    """Return the Home Assistant floor the integration declares."""
    return json.loads((REPO / "hacs.json").read_text(encoding="utf-8"))["homeassistant"]


def blueprint_paths() -> list[Path]:
    """Return every shipped automation blueprint."""
    return sorted(BLUEPRINT_DIR.glob("*.yaml"))


def load_blueprint(path: Path) -> models.Blueprint:
    """Parse a blueprint the way Home Assistant does."""
    return models.Blueprint(
        loader.load_yaml(str(path)),
        expected_domain="automation",
        path=str(path),
        schema=AUTOMATION_BLUEPRINT_SCHEMA,
    )


def test_blueprints_exist() -> None:
    """Guard against the directory being renamed or emptied."""
    assert blueprint_paths(), f"No blueprints found in {BLUEPRINT_DIR}"


@pytest.mark.parametrize("path", blueprint_paths(), ids=lambda path: path.name)
def test_blueprint_matches_home_assistant_schema(path: Path) -> None:
    """Every blueprint must be importable by Home Assistant."""
    blueprint = load_blueprint(path)

    assert blueprint.domain == "automation"
    assert blueprint.metadata["input"], f"{path.name} declares no inputs"
    assert blueprint.metadata.get("source_url", "").endswith(path.name), (
        f"{path.name} points its source_url at a different file"
    )


@pytest.mark.parametrize("path", blueprint_paths(), ids=lambda path: path.name)
def test_blueprint_requires_the_supported_home_assistant(path: Path) -> None:
    """A blueprint must not import into a Home Assistant the integration needs.

    These blueprints declared ``min_version: "2024.6.0"`` while the integration
    requires 2026.8.0 (see hacs.json), so Home Assistant happily imported an
    automation for entities that could never exist on that install.
    """
    required = _minimum_home_assistant_version()
    declared = load_blueprint(path).metadata.get("homeassistant", {}).get("min_version")

    assert declared == required, (
        f"{path.name} declares min_version {declared!r}; the integration "
        f"requires {required!r} (hacs.json)."
    )


@pytest.mark.parametrize("path", blueprint_paths(), ids=lambda path: path.name)
def test_blueprint_does_not_link_an_unpublished_file(path: Path) -> None:
    """``blueprints/README.md`` is gitignored, so the link 404s on GitHub."""
    text = path.read_text(encoding="utf-8")

    assert "blueprints/README.md" not in text, (
        f"{path.name} sends users to blueprints/README.md, which is not "
        "published. Spell the helper setup out, or link the wiki."
    )


class TestHeatPumpBlueprint:
    """The heat-pump blueprint is validated as a fully substituted automation."""

    @pytest.fixture
    def substituted(self, hass: HomeAssistant) -> dict:
        """Return the automation config with the example inputs filled in."""
        blueprint = load_blueprint(HEAT_PUMP_BLUEPRINT)
        inputs = models.BlueprintInputs(
            blueprint,
            {"use_blueprint": {"path": str(HEAT_PUMP_BLUEPRINT), "input": HEAT_PUMP_INPUTS}},
        )
        return inputs.async_substitute()

    def test_all_inputs_are_consumed(self, substituted) -> None:
        """An unused input means a placeholder never made it into the config."""
        assert "!input" not in str(substituted)

    def test_triggers_are_valid(self, substituted) -> None:
        """Triggers must pass Home Assistant's trigger schema."""
        cv.TRIGGER_SCHEMA(substituted["triggers"])

    def test_conditions_are_valid(self, substituted) -> None:
        """Conditions must pass Home Assistant's condition schema."""
        for condition in substituted["conditions"]:
            cv.CONDITION_SCHEMA(condition)

    def test_actions_are_valid(self, substituted) -> None:
        """Actions must pass Home Assistant's script schema."""
        cv.SCRIPT_SCHEMA(substituted["actions"])


    def test_the_release_temperature_stays_inside_the_heater_range(self) -> None:
        """A release temperature the heater rejects would do nothing.

        ``VioletClimateEntity`` drops a setpoint outside its range with a log
        warning instead of raising, so a default above the maximum would leave
        the "hold the valve open" step silently ineffective on every run
        (the default used to be 40 °C against a heater that accepts 20-35 °C).
        """
        blueprint = load_blueprint(HEAT_PUMP_BLUEPRINT)
        release = blueprint.metadata["input"]["release_temperature"]
        bounds = release["selector"]["number"]

        assert DEFAULT_MIN_TEMP <= release["default"] <= DEFAULT_MAX_TEMP
        assert bounds["min"] >= DEFAULT_MIN_TEMP
        assert bounds["max"] <= DEFAULT_MAX_TEMP

    def test_the_helper_setup_is_spelled_out(self) -> None:
        """A blueprint cannot create the helper, so it must say how to.

        The forum report that prompted this: helper created, blueprint
        imported, automation on the dashboard - and then the question where the
        target temperature is actually set.
        """
        description = load_blueprint(HEAT_PUMP_BLUEPRINT).metadata["description"]

        assert "Create helper" in description
        assert "ON THE DASHBOARD" in description

    def test_optional_inputs_may_be_omitted(self, hass: HomeAssistant) -> None:
        """The blueprint must also work without the optional entities."""
        blueprint = load_blueprint(HEAT_PUMP_BLUEPRINT)
        required_only = {
            key: value
            for key, value in HEAT_PUMP_INPUTS.items()
            if key not in ("violet_heater", "enable_switch", "notification_entity")
        }
        config = models.BlueprintInputs(
            blueprint,
            {"use_blueprint": {"path": str(HEAT_PUMP_BLUEPRINT), "input": required_only}},
        ).async_substitute()

        cv.SCRIPT_SCHEMA(config["actions"])
