"""Live check: pool health against a real controller.

Read-only.  Verifies that a controller without every optional module (this one
has no EXT2) reports a healthy pool: never-installed modules are informational,
not errors.

Usage:
    set VIOLET_HOST / VIOLET_USER / VIOLET_PASS, then:
    pytest tests/test_live_pool_health.py -s
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.common import MockConfigEntry
from violet_poolcontroller_api.api import VioletPoolAPI

from custom_components.violet_pool_controller.const import (
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_USE_SSL,
    DOMAIN,
)
from custom_components.violet_pool_controller.device import (
    VioletPoolControllerDevice,
    VioletPoolDataUpdateCoordinator,
)
from custom_components.violet_pool_controller.sensor_modules.specialized import (
    VioletHealthSensor,
)

HOST = os.environ.get("VIOLET_HOST", "")
USER = os.environ.get("VIOLET_USER", "")
PASS = os.environ.get("VIOLET_PASS", "")

pytestmark = pytest.mark.skipif(
    not HOST or not USER or not PASS,
    reason="set VIOLET_HOST/VIOLET_USER/VIOLET_PASS to run the live check",
)


async def test_pool_health_live(hass):
    """Never-installed modules must not flag the pool as unhealthy."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Live Check",
        data={
            CONF_API_URL: HOST,
            CONF_USE_SSL: False,
            CONF_DEVICE_ID: 1,
            CONF_DEVICE_NAME: "Violet Pool Controller",
            CONF_CONTROLLER_NAME: "Live Check",
        },
    )
    config_entry.add_to_hass(hass)

    api = VioletPoolAPI(
        host=HOST,
        session=async_get_clientsession(hass),
        username=USER,
        password=PASS,
    )
    with patch(
        "custom_components.violet_pool_controller.device.async_get_clientsession",
        return_value=MagicMock(),
    ):
        device = VioletPoolControllerDevice(hass=hass, config_entry=config_entry, api=api)
    coordinator = VioletPoolDataUpdateCoordinator(
        hass, device, "live-check", polling_interval=10
    )
    await coordinator.async_refresh()
    assert coordinator.last_update_success, "controller unreachable"

    entity = VioletHealthSensor(coordinator, config_entry)
    entity.async_write_ha_state = MagicMock()

    attributes = entity.extra_state_attributes
    print(f"\npool health: {entity.native_value}")
    print(f"errors:   {attributes['errors']}")
    print(f"warnings: {attributes['warnings']}")
    print(f"info:     {attributes['info']}")

    assert entity.native_value != "offline"
    # Whatever modules this controller has or lacks, none of them may be
    # reported as "missing" - that wording was the false positive.
    assert not [e for e in attributes["errors"] if e.endswith("missing")]
    assert "Extension Module 2 missing" not in attributes["errors"]
    # Real problems (if any exist on the test controller) still surface.
    print(f"HW flags: EXT1={coordinator.data.get('HW_EXTENSION_MODULE_1')} "
          f"EXT2={coordinator.data.get('HW_EXTENSION_MODULE_2')} "
          f"DMX={coordinator.data.get('HW_DMX_MODULE')}")
