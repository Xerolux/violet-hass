"""Tests for VioletControlServiceHandlers control service handlers."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.violet_pool_controller.service_control import (
    DOSING_INDEX_MAP,
    VioletControlServiceHandlers,
)


def make_service_call(data: dict) -> MagicMock:
    """Create a mock ServiceCall with given data."""
    call = MagicMock()
    call.data = data
    return call


def make_coordinator(
    api_return: dict | None = None,
    device_name: str = "Test Pool",
) -> MagicMock:
    """Create a mock coordinator with a device and API."""
    coordinator = MagicMock()
    coordinator.device = MagicMock()
    coordinator.device.device_name = device_name
    success = api_return or {"success": True}
    coordinator.device.api = MagicMock()
    coordinator.device.api.set_switch_state = AsyncMock(return_value=success)
    coordinator.device.api.manual_dosing = AsyncMock(return_value=success)
    coordinator.device.api.set_dosage_enabled = AsyncMock(return_value=success)
    coordinator.device._api = MagicMock()
    coordinator.async_request_refresh = AsyncMock()
    return coordinator


class TestHandleControlPump:
    """Test the handle_control_pump service handler."""

    @pytest.fixture
    def handlers(self):
        """Create handlers with a mock manager."""
        h = VioletControlServiceHandlers()
        h.manager = MagicMock()
        h.hass = MagicMock()
        return h

    async def test_speed_control(self, handlers):
        """Speed control action calls set_switch_state with speed."""
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        await handlers.handle_control_pump(
            make_service_call({"action": "speed_control", "speed": 3, "duration": 0})
        )

        coord.device.api.set_switch_state.assert_awaited_once()
        kwargs = coord.device.api.set_switch_state.call_args[1]
        assert kwargs["key"] == "PUMP"
        assert kwargs["last_value"] == 3
        coord.async_request_refresh.assert_awaited_once()

    async def test_force_off(self, handlers):
        """Force off action sends PUMP OFF with safe duration."""
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        await handlers.handle_control_pump(
            make_service_call({"action": "force_off", "duration": 0})
        )

        kwargs = coord.device.api.set_switch_state.call_args[1]
        assert kwargs["action"] == "OFF"
        # When duration is 0/falsy, safe_duration of 600 is used
        assert kwargs["duration"] == 600

    async def test_eco_mode(self, handlers):
        """Eco mode sets speed to 1."""
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        await handlers.handle_control_pump(
            make_service_call({"action": "eco_mode", "duration": 300})
        )

        kwargs = coord.device.api.set_switch_state.call_args[1]
        assert kwargs["last_value"] == 1

    async def test_boost_mode(self, handlers):
        """Boost mode sets speed to 3."""
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        await handlers.handle_control_pump(
            make_service_call({"action": "boost_mode", "duration": 300})
        )

        kwargs = coord.device.api.set_switch_state.call_args[1]
        assert kwargs["last_value"] == 3

    async def test_auto_mode(self, handlers):
        """Auto mode sends AUTO action."""
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        await handlers.handle_control_pump(
            make_service_call({"action": "auto"})
        )

        kwargs = coord.device.api.set_switch_state.call_args[1]
        assert kwargs["action"] == "AUTO"

    async def test_multiple_coordinators(self, handlers):
        """Action is applied to all coordinators."""
        coord1 = make_coordinator(device_name="Pool 1")
        coord2 = make_coordinator(device_name="Pool 2")
        handlers.manager.get_coordinators_for_call = AsyncMock(
            return_value=[coord1, coord2]
        )

        await handlers.handle_control_pump(
            make_service_call({"action": "auto"})
        )

        coord1.device.api.set_switch_state.assert_awaited_once()
        coord2.device.api.set_switch_state.assert_awaited_once()

    async def test_api_error_raises_ha_error(self, handlers):
        """VioletPoolAPIError is wrapped in HomeAssistantError."""
        from homeassistant.exceptions import HomeAssistantError
        from violet_poolcontroller_api.api import VioletPoolAPIError

        coord = make_coordinator()
        coord.device.api.set_switch_state = AsyncMock(
            side_effect=VioletPoolAPIError("API down")
        )
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        with pytest.raises(HomeAssistantError, match="Pump control failed"):
            await handlers.handle_control_pump(
                make_service_call({"action": "auto"})
            )


class TestHandleSmartDosing:
    """Test the handle_smart_dosing service handler."""

    @pytest.fixture
    def handlers(self):
        h = VioletControlServiceHandlers()
        h.manager = MagicMock()
        h.hass = MagicMock()
        h.manager.check_safety_lock = MagicMock(return_value=False)
        return h

    async def test_dosing_ph_minus(self, handlers):
        """pH- manual dosing calls manual_dosing API."""
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        await handlers.handle_smart_dosing(
            make_service_call({
                "dosing_type": "pH-",
                "action": "manual_dose",
                "duration": 30,
            })
        )

        coord.device.api.manual_dosing.assert_awaited_once()
        coord.async_request_refresh.assert_awaited_once()

    async def test_dosing_auto(self, handlers):
        """Auto dosing calls set_dosage_enabled."""
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        await handlers.handle_smart_dosing(
            make_service_call({
                "dosing_type": "Chlorine",
                "action": "auto",
                "duration": 30,
            })
        )

        coord.device.api.set_dosage_enabled.assert_awaited_once()

    async def test_dosing_stop(self, handlers):
        """Stop dosing calls set_switch_state with OFF."""
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        await handlers.handle_smart_dosing(
            make_service_call({
                "dosing_type": "Chlorine",
                "action": "stop",
                "duration": 30,
            })
        )

        coord.device.api.set_switch_state.assert_awaited_once()
        kwargs = coord.device.api.set_switch_state.call_args[1]
        assert kwargs["action"] == "OFF"

    async def test_safety_lock_blocks(self, handlers):
        """Safety lock prevents dosing."""
        from homeassistant.exceptions import HomeAssistantError

        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])
        handlers.manager.check_safety_lock = MagicMock(return_value=True)
        handlers.manager.get_remaining_lock_time = MagicMock(return_value=120)

        with pytest.raises(HomeAssistantError, match="Safety interval"):
            await handlers.handle_smart_dosing(
                make_service_call({
                    "dosing_type": "Chlorine",
                    "action": "manual_dose",
                    "duration": 30,
                })
            )

    async def test_safety_override_bypasses_lock(self, handlers):
        """Safety override flag bypasses safety lock."""
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])
        handlers.manager.check_safety_lock = MagicMock(return_value=True)

        await handlers.handle_smart_dosing(
            make_service_call({
                "dosing_type": "Chlorine",
                "action": "manual_dose",
                "duration": 30,
                "safety_override": True,
            })
        )

        coord.device.api.manual_dosing.assert_awaited_once()

    async def test_unknown_dosing_type_raises(self, handlers):
        """Unknown dosing type raises HomeAssistantError."""
        from homeassistant.exceptions import HomeAssistantError

        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        with pytest.raises(HomeAssistantError, match="Unknown dosing type"):
            await handlers.handle_smart_dosing(
                make_service_call({
                    "dosing_type": "invalid",
                    "action": "on",
                    "duration": 30,
                })
            )


class TestHandleControlExtensionRelay:
    """Test extension relay control handler."""

    @pytest.fixture
    def handlers(self):
        h = VioletControlServiceHandlers()
        h.manager = MagicMock()
        h.hass = MagicMock()
        return h

    async def test_relay_on(self, handlers):
        """Turning relay on sends state 4 (manual on)."""
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        with patch(
            "custom_components.violet_pool_controller.service_control.VioletControlClient"
        ) as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.set_function_manually = AsyncMock(return_value=True)

            await handlers.handle_control_extension_relay(
                make_service_call({
                    "relay_id": 1,
                    "action": "on",
                    "duration": 0,
                })
            )

            mock_client.set_function_manually.assert_awaited_once()
            args = mock_client.set_function_manually.call_args[0]
            assert args[0] == "EXT1_1"
            assert args[1] == "4"

    async def test_relay_off(self, handlers):
        """Turning relay off sends state 6 (manual off)."""
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        with patch(
            "custom_components.violet_pool_controller.service_control.VioletControlClient"
        ) as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.set_function_manually = AsyncMock(return_value=True)

            await handlers.handle_control_extension_relay(
                make_service_call({
                    "relay_id": 3,
                    "action": "off",
                    "duration": 0,
                })
            )

            args = mock_client.set_function_manually.call_args[0]
            assert args[0] == "EXT3_1"
            assert args[1] == "6"

    async def test_relay_invalid_id_high(self, handlers):
        """Relay ID > 8 raises HomeAssistantError."""
        from homeassistant.exceptions import HomeAssistantError

        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        with pytest.raises(HomeAssistantError, match="1-8"):
            await handlers.handle_control_extension_relay(
                make_service_call({"relay_id": 9, "action": "on"})
            )

    async def test_relay_invalid_id_low(self, handlers):
        """Relay ID < 1 raises HomeAssistantError."""
        from homeassistant.exceptions import HomeAssistantError

        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        with pytest.raises(HomeAssistantError, match="1-8"):
            await handlers.handle_control_extension_relay(
                make_service_call({"relay_id": 0, "action": "on"})
            )

    async def test_relay_explicit_state(self, handlers):
        """Explicit state value is passed through."""
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        with patch(
            "custom_components.violet_pool_controller.service_control.VioletControlClient"
        ) as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.set_function_manually = AsyncMock(return_value=True)

            await handlers.handle_control_extension_relay(
                make_service_call({
                    "relay_id": 2,
                    "state": 1,
                    "duration": 0,
                })
            )

            args = mock_client.set_function_manually.call_args[0]
            assert args[0] == "EXT2_1"
            assert args[1] == "1"


class TestHandleControlPumpHttp:
    """Test HTTP-based pump control handler."""

    @pytest.fixture
    def handlers(self):
        h = VioletControlServiceHandlers()
        h.manager = MagicMock()
        h.hass = MagicMock()
        h.hass.async_create_task = MagicMock()
        return h

    async def test_pump_on(self, handlers):
        """Pump on via HTTP sends PUMP ON command."""
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        with patch(
            "custom_components.violet_pool_controller.service_control.VioletControlClient"
        ) as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.set_pump_speed = AsyncMock(return_value=True)

            await handlers.handle_control_pump_http(
                make_service_call({"action": "on", "speed": 2})
            )

            mock_client.set_pump_speed.assert_awaited_once_with(2)

    async def test_pump_off(self, handlers):
        """Pump off via HTTP sends PUMP OFF command."""
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        with patch(
            "custom_components.violet_pool_controller.service_control.VioletControlClient"
        ) as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.set_pump_off = AsyncMock(return_value=True)

            await handlers.handle_control_pump_http(
                make_service_call({"action": "off"})
            )

            mock_client.set_pump_off.assert_awaited_once()


class TestHandleManualDosingHttp:
    """Test HTTP-based manual dosing handler."""

    @pytest.fixture
    def handlers(self):
        h = VioletControlServiceHandlers()
        h.manager = MagicMock()
        h.hass = MagicMock()
        return h

    async def test_dosing_chlorine(self, handlers):
        """Chlorine dosing uses index 0."""
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        with patch(
            "custom_components.violet_pool_controller.service_control.VioletControlClient"
        ) as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.trigger_manual_dosing = AsyncMock(return_value=True)

            await handlers.handle_manual_dosing_http(
                make_service_call({
                    "dosing_system": "chlorine",
                    "runtime_seconds": 30,
                })
            )

            mock_client.trigger_manual_dosing.assert_awaited_once()
            args = mock_client.trigger_manual_dosing.call_args[0]
            assert args[0] == DOSING_INDEX_MAP["chlorine"]

    async def test_dosing_unknown_system(self, handlers):
        """Unknown dosing system raises HomeAssistantError."""
        from homeassistant.exceptions import HomeAssistantError

        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        with pytest.raises(HomeAssistantError, match="Unknown dosing system"):
            await handlers.handle_manual_dosing_http(
                make_service_call({
                    "dosing_system": "invalid",
                    "runtime_seconds": 30,
                })
            )


class TestDosingIndexMap:
    """Test dosing index mapping constants."""

    def test_chlorine_is_index_0(self):
        assert DOSING_INDEX_MAP["chlorine"] == 0

    def test_electrolysis_is_index_1(self):
        assert DOSING_INDEX_MAP["electrolysis"] == 1

    def test_ph_minus_is_index_3(self):
        assert DOSING_INDEX_MAP["ph_minus"] == 3

    def test_ph_plus_is_index_4(self):
        assert DOSING_INDEX_MAP["ph_plus"] == 4

    def test_flocculant_is_index_5(self):
        assert DOSING_INDEX_MAP["flocculant"] == 5

    def test_h2o2_shares_index_0(self):
        """H2O2 shares the Chlorine physical output (index 0)."""
        assert DOSING_INDEX_MAP["h2o2"] == 0


class TestHandleControlHeaterHttp:
    """Test HTTP-based heater control handler."""

    @pytest.fixture
    def handlers(self):
        h = VioletControlServiceHandlers()
        h.manager = MagicMock()
        h.hass = MagicMock()
        return h

    async def test_heater_on(self, handlers):
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])
        with patch(
            "custom_components.violet_pool_controller.service_control.VioletControlClient"
        ) as cls:
            cls.return_value.set_heater_on = AsyncMock(return_value=True)
            cls.return_value.set_config = AsyncMock(return_value=True)
            await handlers.handle_control_heater_http(
                make_service_call({"action": "on", "target_temperature": 28.0})
            )
            cls.return_value.set_heater_on.assert_awaited_once()
            cls.return_value.set_config.assert_awaited_once()

    async def test_heater_off(self, handlers):
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])
        with patch(
            "custom_components.violet_pool_controller.service_control.VioletControlClient"
        ) as cls:
            cls.return_value.set_heater_off = AsyncMock(return_value=True)
            await handlers.handle_control_heater_http(
                make_service_call({"action": "off"})
            )
            cls.return_value.set_heater_off.assert_awaited_once()


class TestHandleControlSolarHttp:
    """Test HTTP-based solar control handler."""

    @pytest.fixture
    def handlers(self):
        h = VioletControlServiceHandlers()
        h.manager = MagicMock()
        h.hass = MagicMock()
        return h

    async def test_solar_on(self, handlers):
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])
        with patch(
            "custom_components.violet_pool_controller.service_control.VioletControlClient"
        ) as cls:
            cls.return_value.set_solar_on = AsyncMock(return_value=True)
            await handlers.handle_control_solar_http(
                make_service_call({"action": "on"})
            )
            cls.return_value.set_solar_on.assert_awaited_once()

    async def test_solar_off(self, handlers):
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])
        with patch(
            "custom_components.violet_pool_controller.service_control.VioletControlClient"
        ) as cls:
            cls.return_value.set_solar_off = AsyncMock(return_value=True)
            await handlers.handle_control_solar_http(
                make_service_call({"action": "off"})
            )
            cls.return_value.set_solar_off.assert_awaited_once()


class TestHandleControlCoverHttp:
    """Test HTTP-based cover control handler."""

    @pytest.fixture
    def handlers(self):
        h = VioletControlServiceHandlers()
        h.manager = MagicMock()
        h.hass = MagicMock()
        return h

    @pytest.mark.parametrize(
        "action,method",
        [
            ("open", "set_cover_open"),
            ("close", "set_cover_close"),
            ("stop", "set_cover_stop"),
        ],
    )
    async def test_cover_actions(self, handlers, action, method):
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])
        with patch(
            "custom_components.violet_pool_controller.service_control.VioletControlClient"
        ) as cls:
            setattr(cls.return_value, method, AsyncMock(return_value=True))
            await handlers.handle_control_cover_http(
                make_service_call({"action": action})
            )
            getattr(cls.return_value, method).assert_awaited_once()


class TestHandleControlBackwashHttp:
    """Test HTTP-based backwash control handler."""

    @pytest.fixture
    def handlers(self):
        h = VioletControlServiceHandlers()
        h.manager = MagicMock()
        h.hass = MagicMock()
        h.hass.async_create_task = MagicMock()
        return h

    async def test_backwash_abort(self, handlers):
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])
        with patch(
            "custom_components.violet_pool_controller.service_control.VioletControlClient"
        ) as cls:
            cls.return_value.set_backwash_abort = AsyncMock(return_value=True)
            await handlers.handle_control_backwash_http(
                make_service_call({"action": "abort"})
            )
            cls.return_value.set_backwash_abort.assert_awaited_once()

    async def test_backwash_run_requires_duration(self, handlers):
        """Run action requires duration_seconds for safety."""
        from homeassistant.exceptions import HomeAssistantError

        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])
        with pytest.raises(HomeAssistantError, match="duration is required"):
            await handlers.handle_control_backwash_http(
                make_service_call({"action": "run"})
            )

    async def test_backwash_run_with_duration(self, handlers):
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])
        with patch(
            "custom_components.violet_pool_controller.service_control.VioletControlClient"
        ) as cls:
            cls.return_value.set_backwash_run = AsyncMock(return_value=True)
            cls.return_value.set_backwash_abort = AsyncMock(return_value=True)
            await handlers.handle_control_backwash_http(
                make_service_call({"action": "run", "duration_seconds": 120})
            )
            cls.return_value.set_backwash_run.assert_awaited_once()


class TestHandleControlRefillHttp:
    """Test HTTP-based refill control handler."""

    @pytest.fixture
    def handlers(self):
        h = VioletControlServiceHandlers()
        h.manager = MagicMock()
        h.hass = MagicMock()
        h.hass.async_create_task = MagicMock()
        return h

    async def test_refill_stop(self, handlers):
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])
        with patch(
            "custom_components.violet_pool_controller.service_control.VioletControlClient"
        ) as cls:
            cls.return_value.set_function_manually = AsyncMock(return_value=True)
            await handlers.handle_control_refill_http(
                make_service_call({"action": "stop"})
            )
            cls.return_value.set_function_manually.assert_awaited_once()

    async def test_refill_fill_requires_duration(self, handlers):
        """Fill action requires duration_seconds for safety."""
        from homeassistant.exceptions import HomeAssistantError

        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])
        with pytest.raises(HomeAssistantError, match="duration_seconds"):
            await handlers.handle_control_refill_http(
                make_service_call({"action": "fill"})
            )

    async def test_refill_fill_with_duration(self, handlers):
        coord = make_coordinator()
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])
        with patch(
            "custom_components.violet_pool_controller.service_control.VioletControlClient"
        ) as cls:
            cls.return_value.set_function_manually = AsyncMock(return_value=True)
            await handlers.handle_control_refill_http(
                make_service_call({"action": "fill", "duration_seconds": 60})
            )
            cls.return_value.set_function_manually.assert_awaited_once()


class TestHandleManagePvSurplus:
    """Test PV surplus management handler."""

    @pytest.fixture
    def handlers(self):
        h = VioletControlServiceHandlers()
        h.manager = MagicMock()
        h.hass = MagicMock()
        return h

    async def test_activate(self, handlers):
        coord = make_coordinator()
        coord.device.api.set_pv_surplus = AsyncMock(return_value={"success": True})
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])
        await handlers.handle_manage_pv_surplus(
            make_service_call({"mode": "activate", "pump_speed": 2})
        )
        coord.device.api.set_pv_surplus.assert_awaited_once()

    async def test_deactivate(self, handlers):
        coord = make_coordinator()
        coord.device.api.set_pv_surplus = AsyncMock(return_value={"success": True})
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])
        await handlers.handle_manage_pv_surplus(
            make_service_call({"mode": "deactivate"})
        )
        coord.device.api.set_pv_surplus.assert_awaited_once()

    async def test_invalid_pump_speed_clamped(self, handlers):
        """Pump speed outside 1-3 is clamped to valid range."""
        coord = make_coordinator()
        coord.device.api.set_pv_surplus = AsyncMock(return_value={"success": True})
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])
        await handlers.handle_manage_pv_surplus(
            make_service_call({"mode": "activate", "pump_speed": 99})
        )
        kwargs = coord.device.api.set_pv_surplus.call_args[1]
        assert kwargs["pump_speed"] == 3
