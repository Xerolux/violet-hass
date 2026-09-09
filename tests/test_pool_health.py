"""Tests for the pool health aggregation.

Regression target: hardware-module presence flags (``HW_*``) can only be
False when a module was never installed - module detection latches once a
module has been seen.  A not-installed optional module (e.g. no EXT2, or a
standalone dosing unit without a base module) is a valid configuration and
must not surface as a pool-health ERROR.
"""

from unittest.mock import MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller.const import (
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_USE_SSL,
    DOMAIN,
)
from custom_components.violet_pool_controller.device import VioletPoolControllerDevice
from custom_components.violet_pool_controller.sensor_modules.specialized import (
    VioletHealthSensor,
)


@pytest.fixture
def config_entry():
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Test Pool",
        data={
            CONF_API_URL: "192.168.178.55",
            CONF_USE_SSL: False,
            CONF_DEVICE_ID: 1,
            CONF_DEVICE_NAME: "Test Pool Controller",
            CONF_CONTROLLER_NAME: "Test Pool",
        },
    )


@pytest.fixture
def device(hass, config_entry):
    """Return a device wired to a mock API."""
    with patch(
        "custom_components.violet_pool_controller.device.async_get_clientsession",
        return_value=MagicMock(),
    ):
        return VioletPoolControllerDevice(
            hass=hass,
            config_entry=config_entry,
            api=MagicMock(),
        )


def _make_health_sensor(device, config_entry, data):
    """Build a VioletHealthSensor with a mocked coordinator."""
    coordinator = MagicMock()
    coordinator.device = device
    coordinator.data = data
    coordinator.last_update_success = True
    entity = VioletHealthSensor(coordinator, config_entry)
    entity.async_write_ha_state = MagicMock()
    return entity


ALL_MODULES_PRESENT = {
    "HW_BASE_MODULE": True,
    "HW_DOSING_MODULE": True,
    "HW_EXTENSION_MODULE_1": True,
    "HW_EXTENSION_MODULE_2": True,
    "HW_DMX_MODULE": True,
    "HW_DIRULE_MODULE": True,
}


async def test_absent_extension_module_is_not_an_error(hass, device, config_entry):
    """A never-installed EXT2 must not flag the pool as unhealthy."""
    data = dict(ALL_MODULES_PRESENT, HW_EXTENSION_MODULE_2=False)
    entity = _make_health_sensor(device, config_entry, data)

    assert entity.native_value == "ok"
    attributes = entity.extra_state_attributes
    assert "Extension Module 2 missing" not in attributes["errors"]
    assert attributes["error_count"] == 0


async def test_standalone_base_module_absent_is_not_an_error(hass, device, config_entry):
    """Standalone dosing systems report no base module by design."""
    data = dict(ALL_MODULES_PRESENT, HW_BASE_MODULE=False)
    entity = _make_health_sensor(device, config_entry, data)

    assert entity.native_value == "ok"
    assert entity.extra_state_attributes["error_count"] == 0


async def test_absent_module_is_reported_as_info(hass, device, config_entry):
    """The absent module stays visible as informational, not as an error."""
    data = dict(ALL_MODULES_PRESENT, HW_DMX_MODULE=False)
    entity = _make_health_sensor(device, config_entry, data)

    attributes = entity.extra_state_attributes
    assert "DMX Module not installed" in attributes["info"]
    assert entity.native_value == "ok"


async def test_all_modules_present_is_healthy(hass, device, config_entry):
    """A fully equipped controller reports ok with empty problem lists."""
    entity = _make_health_sensor(device, config_entry, dict(ALL_MODULES_PRESENT))

    assert entity.native_value == "ok"
    attributes = entity.extra_state_attributes
    assert attributes["errors"] == []
    assert attributes["warnings"] == []


async def test_problem_flag_still_raises_error(hass, device, config_entry):
    """Binary problem sensors keep flagging the pool as unhealthy."""
    data = dict(ALL_MODULES_PRESENT, CIRCULATION_STATE=1)
    entity = _make_health_sensor(device, config_entry, data)

    assert entity.native_value == "error"
    assert "Circulation Issue" in entity.extra_state_attributes["errors"]
