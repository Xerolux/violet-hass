"""Tests for Violet Pool Controller config flow."""
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller.const import (
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_POOL_SIZE,
    CONF_POOL_TYPE,
    DOMAIN,
)


class TestConfigFlow:
    """Test Violet Pool Controller config flow."""

    async def test_duplicate_check_different_device_ids(self, hass):
        """Test dass mehrere Controller mit gleicher IP aber unterschiedlichen Device-IDs erlaubt sind."""
        # Setup: Erstelle ersten Controller
        entry1 = MockConfigEntry(
            domain=DOMAIN,
            title="Pool 1 • 50m³",
            data={
                CONF_API_URL: "192.168.178.55",
                CONF_DEVICE_ID: 1,
                CONF_CONTROLLER_NAME: "Pool 1",
                CONF_DEVICE_NAME: "Violet Pool Controller",
                CONF_POOL_SIZE: 50,
                CONF_POOL_TYPE: "outdoor",
            },
        )
        entry1.add_to_hass(hass)

        # Test: Zweiter Controller mit gleicher IP aber Device-ID 2
        from custom_components.violet_pool_controller.config_flow import ConfigFlow as VioletDeviceConfigFlow

        flow = VioletDeviceConfigFlow()
        flow.hass = hass
        flow.handler = DOMAIN # Set handler (domain) so _async_current_entries works

        # Sollte NICHT als Duplikat erkannt werden
        is_duplicate = flow._is_duplicate_entry("192.168.178.55", device_id=2)
        assert not is_duplicate, "Controller mit gleicher IP aber unterschiedlicher Device-ID sollte erlaubt sein"

        # Sollte als Duplikat erkannt werden (gleiche IP + Device-ID)
        is_duplicate = flow._is_duplicate_entry("192.168.178.55", device_id=1)
        assert is_duplicate, "Controller mit gleicher IP UND Device-ID sollte als Duplikat erkannt werden"


    async def test_duplicate_check_different_ips(self, hass):
        """Test dass Controller mit unterschiedlichen IPs immer erlaubt sind."""
        # Setup: Erstelle ersten Controller
        entry1 = MockConfigEntry(
            domain=DOMAIN,
            title="Pool 1",
            data={
                CONF_API_URL: "192.168.178.55",
                CONF_DEVICE_ID: 1,
                CONF_CONTROLLER_NAME: "Pool 1",
            },
        )
        entry1.add_to_hass(hass)

        from custom_components.violet_pool_controller.config_flow import ConfigFlow as VioletDeviceConfigFlow

        flow = VioletDeviceConfigFlow()
        flow.hass = hass
        flow.handler = DOMAIN

        # Sollte NICHT als Duplikat erkannt werden (unterschiedliche IP)
        is_duplicate = flow._is_duplicate_entry("192.168.178.56", device_id=1)
        assert not is_duplicate, "Controller mit unterschiedlicher IP sollte erlaubt sein"


    async def test_duplicate_check_empty_entries(self, hass):
        """Test dass Duplicate-Check mit leeren Entries funktioniert."""
        # Keine Entries hinzufügen

        from custom_components.violet_pool_controller.config_flow import ConfigFlow as VioletDeviceConfigFlow

        flow = VioletDeviceConfigFlow()
        flow.hass = hass
        flow.handler = DOMAIN

        # Sollte nie als Duplikat erkannt werden wenn keine Entries existieren
        is_duplicate = flow._is_duplicate_entry("192.168.178.55", device_id=1)
        assert not is_duplicate, "Bei leeren Entries sollte nichts als Duplikat erkannt werden"


    async def test_controller_name_in_entry_title(self, hass):
        """Test dass Controller-Name im Entry-Title verwendet wird."""
        from custom_components.violet_pool_controller.config_flow import ConfigFlow as VioletDeviceConfigFlow

        flow = VioletDeviceConfigFlow()
        flow.hass = hass
        flow._config_data = {
            CONF_CONTROLLER_NAME: "Außenpool",
            CONF_POOL_SIZE: 75,
        }

        title = flow._generate_entry_title()
        assert title == "Außenpool • 75m³", f"Expected 'Außenpool • 75m³' but got '{title}'"


    async def test_controller_name_fallback(self, hass):
        """Test dass Fallback auf Default-Name funktioniert."""
        from custom_components.violet_pool_controller.config_flow import ConfigFlow as VioletDeviceConfigFlow
        from custom_components.violet_pool_controller.const import DEFAULT_CONTROLLER_NAME

        flow = VioletDeviceConfigFlow()
        flow.hass = hass
        flow._config_data = {
            # CONF_CONTROLLER_NAME fehlt absichtlich
            CONF_POOL_SIZE: 50,
        }

        title = flow._generate_entry_title()
        expected = f"{DEFAULT_CONTROLLER_NAME} • 50m³"
        assert title == expected, f"Expected '{expected}' but got '{title}'"
