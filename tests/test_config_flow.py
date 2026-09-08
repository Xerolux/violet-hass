"""Tests for Violet Pool Controller config flow."""

from unittest.mock import AsyncMock, MagicMock, patch

from pytest_homeassistant_custom_component.common import MockConfigEntry
from violet_poolcontroller_api import VioletAuthError, VioletPoolAPIError

from custom_components.violet_pool_controller.const import (
    CONF_API_URL,
    CONF_CONTROLLER_NAME,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_PASSWORD,
    CONF_POOL_SIZE,
    CONF_POOL_TYPE,
    CONF_RETRY_ATTEMPTS,
    CONF_TIMEOUT_DURATION,
    CONF_USE_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
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
        from custom_components.violet_pool_controller.config_flow import (
            ConfigFlow as VioletDeviceConfigFlow,
        )

        flow = VioletDeviceConfigFlow()
        flow.hass = hass
        flow.handler = DOMAIN  # Set handler (domain) so _async_current_entries works

        # Sollte NICHT als Duplikat erkannt werden
        is_duplicate = flow._is_duplicate_entry("192.168.178.55", 80, device_id=2)
        assert not is_duplicate, (
            "Controller mit gleicher IP aber unterschiedlicher Device-ID sollte erlaubt sein"
        )

        # Sollte als Duplikat erkannt werden (gleiche IP + Device-ID)
        is_duplicate = flow._is_duplicate_entry("192.168.178.55", 80, device_id=1)
        assert is_duplicate, (
            "Controller mit gleicher IP UND Device-ID sollte als Duplikat erkannt werden"
        )

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

        from custom_components.violet_pool_controller.config_flow import (
            ConfigFlow as VioletDeviceConfigFlow,
        )

        flow = VioletDeviceConfigFlow()
        flow.hass = hass
        flow.handler = DOMAIN

        # Sollte NICHT als Duplikat erkannt werden (unterschiedliche IP)
        is_duplicate = flow._is_duplicate_entry("192.168.178.56", 80, device_id=1)
        assert not is_duplicate, "Controller mit unterschiedlicher IP sollte erlaubt sein"

    async def test_duplicate_check_empty_entries(self, hass):
        """Test dass Duplicate-Check mit leeren Entries funktioniert."""
        # Keine Entries hinzufügen

        from custom_components.violet_pool_controller.config_flow import (
            ConfigFlow as VioletDeviceConfigFlow,
        )

        flow = VioletDeviceConfigFlow()
        flow.hass = hass
        flow.handler = DOMAIN

        # Sollte nie als Duplikat erkannt werden wenn keine Entries existieren
        is_duplicate = flow._is_duplicate_entry("192.168.178.55", 80, device_id=1)
        assert not is_duplicate, "Bei leeren Entries sollte nichts als Duplikat erkannt werden"

    async def test_controller_name_in_entry_title(self, hass):
        """Test dass Controller-Name im Entry-Title verwendet wird."""
        from custom_components.violet_pool_controller.config_flow import (
            ConfigFlow as VioletDeviceConfigFlow,
        )

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
        from custom_components.violet_pool_controller.config_flow import (
            ConfigFlow as VioletDeviceConfigFlow,
        )
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

    async def test_zeroconf_uses_same_unique_id_format(self, hass):
        """Test dass Zeroconf denselben unique_id-Builder wie der manuelle Flow nutzt."""
        from custom_components.violet_pool_controller.config_flow import (
            ConfigFlow as VioletDeviceConfigFlow,
        )

        flow = VioletDeviceConfigFlow()
        flow.hass = hass
        flow.handler = DOMAIN
        # The flow manager normally supplies a mutable context; the discovery
        # step writes the title placeholders into it.
        flow.context = {}
        flow.async_set_unique_id = AsyncMock()
        flow._abort_if_unique_id_configured = MagicMock()
        flow.async_step_zeroconf_confirm = AsyncMock(
            return_value={"type": "form", "step_id": "zeroconf_confirm"}
        )

        discovery_info = MagicMock()
        discovery_info.ip_address = "192.168.178.55"
        discovery_info.name = "violet-controller.local."
        discovery_info.port = 80

        result = await flow.async_step_zeroconf(discovery_info)

        flow.async_set_unique_id.assert_awaited_once_with("192.168.178.55-1")
        assert result["step_id"] == "zeroconf_confirm"

    def test_is_ip_literal_helper(self):
        """IP helper must distinguish literals from hostnames."""
        from custom_components.violet_pool_controller.config_flow import (
            ConfigFlow as VioletDeviceConfigFlow,
        )

        assert VioletDeviceConfigFlow._is_ip_literal("192.168.178.55")
        assert VioletDeviceConfigFlow._is_ip_literal("2001:db8::1")
        assert not VioletDeviceConfigFlow._is_ip_literal("pool-controller")
        assert not VioletDeviceConfigFlow._is_ip_literal("pool.local")

    async def test_get_grouped_sensors_honors_verify_ssl_false(self, hass):
        """Sensor auto-detection must not force verify_ssl=True.

        Regression test: get_grouped_sensors() used to hardcode
        verify_ssl=True, so a controller configured with a self-signed
        certificate (verify_ssl=False) would pass the connection test step
        but then fail SSL verification during sensor auto-detection.
        """
        from custom_components.violet_pool_controller.config_flow_utils.sensor_helper import (
            get_grouped_sensors,
        )

        mock_api_instance = MagicMock()
        mock_api_instance.get_readings = AsyncMock(return_value={"PUMP": 1})
        mock_api_instance.dosing_standalone = False
        mock_api_class = MagicMock(return_value=mock_api_instance)

        config_data = {
            CONF_API_URL: "192.168.178.55",
            CONF_VERIFY_SSL: False,
        }

        with patch(
            "custom_components.violet_pool_controller.config_flow_utils.sensor_helper.VioletPoolAPI",
            mock_api_class,
        ):
            await get_grouped_sensors(hass, config_data)

        assert mock_api_class.call_args.kwargs["verify_ssl"] is False


class TestZeroconfCredentialEntry:
    """Zeroconf discovery must collect credentials before an entry is created.

    Regression tests: the zeroconf confirm step used to be a bare form without
    any fields, so entries were created with empty username/password, and a
    controller that required authentication left the user stuck in a
    "cannot_connect" loop with no way to enter credentials.
    """

    def _make_flow(self, hass):
        """Create a config flow primed with zeroconf discovery data."""
        from custom_components.violet_pool_controller.config_flow import (
            ConfigFlow as VioletDeviceConfigFlow,
        )

        flow = VioletDeviceConfigFlow()
        flow.hass = hass
        flow.handler = DOMAIN
        flow._title_placeholders = {"name": "violet", "host": "192.168.178.55"}
        flow._config_data = {
            CONF_API_URL: "192.168.178.55",
            CONF_USERNAME: "",
            CONF_PASSWORD: "",
        }
        return flow

    @staticmethod
    def _schema_keys(result):
        """Extract plain key names from a voluptuous form schema."""
        return {getattr(key, "schema", key) for key in result["data_schema"].schema}

    async def test_zeroconf_confirm_shows_credential_fields(self, hass):
        """Der Bestätigungsschritt muss Felder für Benutzername und Passwort zeigen."""
        flow = self._make_flow(hass)

        result = await flow.async_step_zeroconf_confirm(None)

        assert result["type"] == "form"
        assert result["step_id"] == "zeroconf_confirm"
        keys = self._schema_keys(result)
        assert CONF_USERNAME in keys, "zeroconf_confirm muss ein Benutzername-Feld haben"
        assert CONF_PASSWORD in keys, "zeroconf_confirm muss ein Passwort-Feld haben"

    async def test_pool_setup_schema_accepts_known_values(self, hass):
        """Pool-Typ und Desinfektion müssen weiterhin die gespeicherten Werte akzeptieren."""
        flow = self._make_flow(hass)

        schema = flow._get_pool_setup_schema()
        validated = schema(
            {
                "pool_size": 50,
                "pool_type": "outdoor",
                "disinfection_method": "chlorine",
            }
        )

        assert validated["pool_type"] == "outdoor"
        assert validated["disinfection_method"] == "chlorine"

    async def test_zeroconf_confirm_stores_credentials_and_proceeds(self, hass):
        """Eingegebene Zugangsdaten müssen im Config-Entry landen."""
        flow = self._make_flow(hass)
        flow._test_connection = AsyncMock(return_value=True)

        result = await flow.async_step_zeroconf_confirm(
            {CONF_USERNAME: "admin", CONF_PASSWORD: "secret"}
        )

        assert result["type"] == "form"
        assert result["step_id"] == "pool_setup"
        assert flow._config_data[CONF_USERNAME] == "admin"
        assert flow._config_data[CONF_PASSWORD] == "secret"

    async def test_zeroconf_confirm_keeps_empty_credentials_without_auth(self, hass):
        """Controller ohne Anmeldung: leere Felder müssen weiterhin durchreichen."""
        flow = self._make_flow(hass)
        flow._test_connection = AsyncMock(return_value=True)

        result = await flow.async_step_zeroconf_confirm({})

        assert result["step_id"] == "pool_setup"
        assert flow._config_data[CONF_USERNAME] == ""

    async def test_zeroconf_confirm_auth_error_keeps_username(self, hass):
        """Falsche Zugangsdaten: Formular mit invalid_auth, Benutzername bleibt stehen."""
        flow = self._make_flow(hass)
        flow._test_connection = AsyncMock(return_value=False)
        flow._last_connection_error = "invalid_auth"

        result = await flow.async_step_zeroconf_confirm(
            {CONF_USERNAME: "admin", CONF_PASSWORD: "wrong"}
        )

        assert result["type"] == "form"
        assert result["step_id"] == "zeroconf_confirm"
        assert result["errors"]["base"] == "invalid_auth"
        assert CONF_USERNAME in self._schema_keys(result)

    async def test_zeroconf_confirm_connect_error_uses_cannot_connect(self, hass):
        """Nicht erreichbarer Controller: cannot_connect statt invalid_auth."""
        flow = self._make_flow(hass)
        flow._test_connection = AsyncMock(return_value=False)
        flow._last_connection_error = "cannot_connect"

        result = await flow.async_step_zeroconf_confirm(
            {CONF_USERNAME: "admin", CONF_PASSWORD: "secret"}
        )

        assert result["type"] == "form"
        assert result["errors"]["base"] == "cannot_connect"

    async def test_test_connection_classifies_auth_error(self, hass):
        """_test_connection muss Auth-Fehler von Verbindungsfehlern unterscheiden."""
        flow = self._make_flow(hass)
        flow._config_data = {
            CONF_API_URL: "192.168.178.55",
            CONF_USERNAME: "admin",
            CONF_PASSWORD: "wrong",
            CONF_USE_SSL: False,
            CONF_VERIFY_SSL: False,
            CONF_TIMEOUT_DURATION: 5,
            CONF_RETRY_ATTEMPTS: 1,
        }

        with patch(
            "custom_components.violet_pool_controller.config_flow.VioletPoolAPI"
        ) as api_class:
            api_class.return_value.get_readings = AsyncMock(
                side_effect=VioletAuthError("401")
            )
            ok = await flow._test_connection()

        assert ok is False
        assert flow._last_connection_error == "invalid_auth"

    async def test_test_connection_classifies_api_error(self, hass):
        """Allgemeine API-Fehler müssen auf cannot_connect mappen."""
        flow = self._make_flow(hass)
        flow._config_data = {
            CONF_API_URL: "192.168.178.55",
            CONF_USERNAME: "admin",
            CONF_PASSWORD: "secret",
            CONF_USE_SSL: False,
            CONF_VERIFY_SSL: False,
            CONF_TIMEOUT_DURATION: 5,
            CONF_RETRY_ATTEMPTS: 1,
        }

        with patch(
            "custom_components.violet_pool_controller.config_flow.VioletPoolAPI"
        ) as api_class:
            api_class.return_value.get_readings = AsyncMock(
                side_effect=VioletPoolAPIError("unreachable")
            )
            ok = await flow._test_connection()

        assert ok is False
        assert flow._last_connection_error == "cannot_connect"


class TestSensorAutoDetection:
    """Auto-detection must reach the controller and never produce an empty entry."""

    @staticmethod
    def _flow(hass):
        from custom_components.violet_pool_controller.config_flow import ConfigFlow

        flow = ConfigFlow()
        flow.hass = hass
        flow.handler = DOMAIN
        return flow

    async def test_get_grouped_sensors_uses_the_configured_port(self, hass):
        """The port must be part of the host, as in the connection test.

        Regression: get_grouped_sensors() built the API client from the bare
        host, so a controller on a non-default port was contacted on port 80.
        Discovery failed, the exception was swallowed and the entry ended up
        without a single entity.
        """
        from custom_components.violet_pool_controller.config_flow_utils.sensor_helper import (
            get_grouped_sensors,
        )
        from custom_components.violet_pool_controller.const import CONF_PORT

        api = MagicMock()
        api.get_readings = AsyncMock(return_value={"PUMP": 1})
        api.dosing_standalone = False
        api_class = MagicMock(return_value=api)

        with patch(
            "custom_components.violet_pool_controller.config_flow_utils.sensor_helper.VioletPoolAPI",
            api_class,
        ):
            await get_grouped_sensors(
                hass, {CONF_API_URL: "192.168.178.55", CONF_PORT: 8080}
            )

        assert api_class.call_args.kwargs["host"] == "192.168.178.55:8080"

    async def test_get_grouped_sensors_accepts_a_short_controller_password(self, hass):
        """A short password is the controller's business, not the flow's.

        Regression: get_grouped_sensors() ran a credential-strength check the
        connection test does not, so "1234" passed the test and then silently
        produced an entry without entities.
        """
        from custom_components.violet_pool_controller.config_flow_utils.sensor_helper import (
            get_grouped_sensors,
        )

        api = MagicMock()
        api.get_readings = AsyncMock(return_value={"PUMP": 1, "SOLAR": 0})
        api.dosing_standalone = False

        with patch(
            "custom_components.violet_pool_controller.config_flow_utils.sensor_helper.VioletPoolAPI",
            MagicMock(return_value=api),
        ):
            grouped = await get_grouped_sensors(
                hass,
                {
                    CONF_API_URL: "192.168.178.55",
                    CONF_USERNAME: "admin",
                    CONF_PASSWORD: "1234",
                },
            )

        assert grouped, "a short controller password must not empty the detection"

    async def test_no_detected_keys_selects_everything(self, hass):
        """An empty detection stores None ("all"), never [] ("nothing")."""
        from custom_components.violet_pool_controller.const import CONF_SELECTED_SENSORS

        flow = self._flow(hass)
        flow._config_data = {
            CONF_API_URL: "192.168.178.55",
            CONF_CONTROLLER_NAME: "Test Pool",
        }

        with patch.object(flow, "_get_grouped_sensors", AsyncMock(return_value={})):
            result = await flow._auto_configure_entities()

        assert result["data"][CONF_SELECTED_SENSORS] is None

    async def test_detected_keys_are_stored(self, hass):
        """The normal case still stores the detected datapoints."""
        from custom_components.violet_pool_controller.const import CONF_SELECTED_SENSORS

        flow = self._flow(hass)
        flow._config_data = {
            CONF_API_URL: "192.168.178.55",
            CONF_CONTROLLER_NAME: "Test Pool",
        }

        with patch.object(
            flow,
            "_get_grouped_sensors",
            AsyncMock(return_value={"PUMP": ["PUMP"], "SOLAR": ["SOLAR"]}),
        ):
            result = await flow._auto_configure_entities()

        assert result["data"][CONF_SELECTED_SENSORS] == ["PUMP", "SOLAR"]


class TestFeatureAutoDetection:
    """Feature detection must use the same key -> feature map as the platforms."""

    @staticmethod
    def _flow(hass):
        from custom_components.violet_pool_controller.config_flow import ConfigFlow

        flow = ConfigFlow()
        flow.hass = hass
        flow.handler = DOMAIN
        return flow

    async def test_dmx_and_eco_keys_enable_their_features(self, hass):
        """Regression: the hand-written marker table knew neither feature.

        ``dmx_scenes`` and ``eco_mode`` are part of AVAILABLE_FEATURES and
        feature_keys.py routes DMX_*/ECO* keys to them, so a fresh setup used
        to hide the DMX and ECO entities.
        """
        flow = self._flow(hass)

        active = flow._detect_active_features({"DMX_SCENE1", "ECO_MODE_ACTIVE"})

        assert "dmx_scenes" in active
        assert "eco_mode" in active

    async def test_known_features_are_still_detected(self, hass):
        """The features the old table covered must keep working."""
        flow = self._flow(hass)

        active = flow._detect_active_features({"PUMP", "HEATER", "SOLAR", "COVER_STATE"})

        assert "filter_control" in active
        assert "heating" in active
        assert "solar" in active
        assert "cover_control" in active

    async def test_no_keys_falls_back_to_the_defaults(self, hass):
        """Without any controller data the default feature set is kept."""
        from custom_components.violet_pool_controller.const import AVAILABLE_FEATURES

        flow = self._flow(hass)

        active = flow._detect_active_features(set())

        assert active == [str(f["id"]) for f in AVAILABLE_FEATURES if f["default"]]


class TestOptionsFlowStoresOnlyOptions:
    """The options flow must never copy the connection settings into the options.

    Regression: every step saved ``{**data, **options, **changed}``, so the
    password ended up in ``entry.options`` and the options-first lookup then
    shadowed every later reconfigure of the connection.
    """

    @staticmethod
    async def _save(hass, entry, step, user_input):
        from custom_components.violet_pool_controller.config_flow_support import (
            OptionsFlowHandler,
        )

        handler = OptionsFlowHandler()
        handler.hass = hass
        # For an options flow the handler *is* the config entry id.
        handler.handler = entry.entry_id
        return await getattr(handler, step)(user_input)

    def _entry(self, hass):
        entry = MockConfigEntry(
            domain=DOMAIN,
            title="Test Pool",
            data={
                CONF_API_URL: "192.168.178.55",
                CONF_USERNAME: "admin",
                CONF_PASSWORD: "s3cret",
                CONF_USE_SSL: False,
                CONF_DEVICE_ID: 1,
                CONF_CONTROLLER_NAME: "Test Pool",
                CONF_TIMEOUT_DURATION: 10,
                CONF_RETRY_ATTEMPTS: 3,
            },
            options={},
        )
        entry.add_to_hass(hass)
        return entry

    async def test_settings_save_keeps_credentials_out_of_the_options(self, hass):
        """Saving the general settings stores those settings and nothing else."""
        entry = self._entry(hass)

        result = await self._save(
            hass, entry, "async_step_settings", {"polling_interval": 30}
        )

        assert CONF_PASSWORD not in result["data"]
        assert CONF_USERNAME not in result["data"]
        assert CONF_API_URL not in result["data"]
        assert result["data"]["polling_interval"] == 30

    async def test_feature_save_keeps_credentials_out_of_the_options(self, hass):
        """The feature step saves the feature list only."""
        from custom_components.violet_pool_controller.const import CONF_ACTIVE_FEATURES

        entry = self._entry(hass)

        result = await self._save(
            hass,
            entry,
            "async_step_features",
            {CONF_ACTIVE_FEATURES: ["heating", "solar"]},
        )

        assert CONF_PASSWORD not in result["data"]
        assert result["data"][CONF_ACTIVE_FEATURES] == ["heating", "solar"]

    async def test_existing_options_survive_a_save(self, hass):
        """Options set by an earlier step are not dropped by the next one."""
        entry = self._entry(hass)
        hass.config_entries.async_update_entry(entry, options={"invert_cover": True})

        result = await self._save(
            hass, entry, "async_step_settings", {"polling_interval": 30}
        )

        assert result["data"]["invert_cover"] is True
        assert result["data"]["polling_interval"] == 30


class TestZeroconfDiscoveryCard:
    """The discovery card is rendered from the flow context."""

    async def test_title_placeholders_reach_the_context(self, hass):
        """Regression: only the attribute was set, so the card showed no host.

        Home Assistant reads ``context["title_placeholders"]`` when it renders
        the "discovered device" card; the private attribute is invisible to it.
        """
        from custom_components.violet_pool_controller.config_flow import ConfigFlow

        flow = ConfigFlow()
        flow.hass = hass
        flow.handler = DOMAIN
        flow.context = {}
        flow.async_set_unique_id = AsyncMock()
        flow._abort_if_unique_id_configured = MagicMock()
        flow.async_step_zeroconf_confirm = AsyncMock(return_value={"type": "form"})

        discovery_info = MagicMock()
        discovery_info.ip_address = "192.168.178.55"
        discovery_info.name = "violet-controller.local."
        discovery_info.port = 8080

        await flow.async_step_zeroconf(discovery_info)

        placeholders = flow.context["title_placeholders"]
        assert placeholders["name"] == "violet-controller.local."
        assert placeholders["host"] == "192.168.178.55:8080"
