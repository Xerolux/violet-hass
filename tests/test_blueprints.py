"""Validate the shipped blueprints against Home Assistant's own schema.

Blueprints are plain YAML that nothing in the build ever loaded, so a typo only
surfaced when a user tried to import one. These tests parse every blueprint the
way Home Assistant does, and additionally substitute example inputs into the
heat-pump blueprint so its triggers, conditions and actions are validated as a
real automation would be.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from homeassistant.components.automation.config import AUTOMATION_BLUEPRINT_SCHEMA
from homeassistant.components.blueprint import models
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.util.yaml import loader

BLUEPRINT_DIR = Path(__file__).parent.parent / "blueprints" / "automation"
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
    "release_temperature": 40,
    "enable_switch": "input_boolean.pool_control",
    "notification_entity": "notify.mobile_app_phone",
}


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
