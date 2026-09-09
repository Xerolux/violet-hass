"""Tests for VioletControlServiceHandlers control service handlers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from violet_poolcontroller_api.api import VioletPoolAPI

from custom_components.violet_pool_controller.runtime_data import VioletRuntimeData
from custom_components.violet_pool_controller.safety_guard import SafetyGuard
from custom_components.violet_pool_controller.service_control import (
    VioletControlServiceHandlers,
)
from custom_components.violet_pool_controller.service_helpers import DOSING_INDEX_MAP

ENTRY_ID = "test_entry"


def make_service_call(data: dict) -> MagicMock:
    """Create a mock ServiceCall with given data."""
    call = MagicMock()
    call.data = data
    return call


def make_coordinator(
    api_return: dict | None = None,
    device_name: str = "Test Pool",
    entry_id: str = ENTRY_ID,
) -> MagicMock:
    """Create a mock coordinator with a device and API.

    The API mock is built with ``spec=VioletPoolAPI`` on purpose: a stop target
    naming a method the real API does not have must fail the test rather than
    be silently accepted, which is how the refill auto-stop stayed broken.
    """
    coordinator = MagicMock()
    coordinator.device = MagicMock()
    coordinator.device.device_name = device_name
    success = api_return or {"success": True}
    coordinator.device.api = MagicMock(spec=VioletPoolAPI)
    coordinator.device.api.set_switch_state = AsyncMock(return_value=success)
    coordinator.device.api.manual_dosing = AsyncMock(return_value=success)
    coordinator.device.api.set_dosage_enabled = AsyncMock(return_value=success)
    coordinator.async_request_refresh = AsyncMock()
    coordinator.config_entry = MagicMock()
    coordinator.config_entry.entry_id = entry_id
    return coordinator


class _FakePersistence:
    """In-memory persistence backend for SafetyGuard tests."""

    def __init__(self) -> None:
        self._data: dict = {}

    async def async_load(self) -> dict:
        return self._data

    async def async_save(self, data: dict) -> None:
        self._data = data


@pytest.fixture(autouse=True)
def expected_lingering_tasks():
    """Allow lingering tasks from SafetyGuard background timers."""
    return True


def make_manager_with_safety(coordinator: MagicMock | None = None) -> MagicMock:
    """Create a mock manager with a real SafetyGuard wired to *coordinator*.

    The guard resolves the controller through the config entry that started
    the operation, so the mock hass has to answer ``async_get_entry`` with an
    entry carrying that coordinator's runtime data.
    """
    manager = MagicMock()
    hass = MagicMock()
    hass.data = {}

    def mock_create_bg_task(coro, name=None):
        coro.close()
        return MagicMock()

    hass.async_create_background_task = mock_create_bg_task

    if coordinator is not None:
        entry = MagicMock()
        entry.entry_id = coordinator.config_entry.entry_id
        entry.runtime_data = VioletRuntimeData(coordinator=coordinator)
        hass.config_entries.async_get_entry.side_effect = (
            lambda entry_id: entry if entry_id == entry.entry_id else None
        )
        hass.config_entries.async_entries.return_value = [entry]
    else:
        hass.config_entries.async_get_entry.return_value = None
        hass.config_entries.async_entries.return_value = []

    manager.hass = hass
    guard = SafetyGuard(hass, _FakePersistence())
    manager.safety_guard = guard
    manager.set_safety_lock = guard.set_lock
    return manager


def close_background_coroutine(coroutine, _name):
    """Close a mocked background coroutine without executing its delay."""
    coroutine.close()


class TestHandleControlPump:
    """Test the handle_control_pump service handler."""

    @pytest.fixture
    def handlers(self):
        coordinator = make_coordinator()
        h = VioletControlServiceHandlers()
        h.manager = make_manager_with_safety(coordinator)
        h.hass = h.manager.hass
        h.manager.get_coordinators_for_call = AsyncMock(return_value=[coordinator])
        # The guard resolves the controller through this entry, so tests must
        # act on the same coordinator the manager was wired to.
        h.test_coordinator = coordinator
        return h

    async def test_speed_control(self, handlers):
        """Speed control action calls set_switch_state with speed."""
        coord = handlers.test_coordinator

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
        coord = handlers.test_coordinator

        await handlers.handle_control_pump(
            make_service_call({"action": "force_off", "duration": 0})
        )

        kwargs = coord.device.api.set_switch_state.call_args[1]
        assert kwargs["action"] == "OFF"
        # When duration is 0/falsy, safe_duration of 600 is used
        assert kwargs["duration"] == 600

    async def test_eco_mode(self, handlers):
        """Eco mode sets speed to 1."""
        coord = handlers.test_coordinator

        await handlers.handle_control_pump(
            make_service_call({"action": "eco_mode", "duration": 300})
        )

        kwargs = coord.device.api.set_switch_state.call_args[1]
        assert kwargs["last_value"] == 1

    async def test_boost_mode(self, handlers):
        """Boost mode sets speed to 3."""
        coord = handlers.test_coordinator

        await handlers.handle_control_pump(
            make_service_call({"action": "boost_mode", "duration": 300})
        )

        kwargs = coord.device.api.set_switch_state.call_args[1]
        assert kwargs["last_value"] == 3

    async def test_auto_mode(self, handlers):
        """Auto mode sends AUTO action."""
        coord = handlers.test_coordinator

        await handlers.handle_control_pump(make_service_call({"action": "auto"}))

        kwargs = coord.device.api.set_switch_state.call_args[1]
        assert kwargs["action"] == "AUTO"

    async def test_multiple_coordinators(self, handlers):
        """Action is applied to all coordinators."""
        coord1 = make_coordinator(device_name="Pool 1")
        coord2 = make_coordinator(device_name="Pool 2")
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord1, coord2])

        await handlers.handle_control_pump(make_service_call({"action": "auto"}))

        coord1.device.api.set_switch_state.assert_awaited_once()
        coord2.device.api.set_switch_state.assert_awaited_once()

    async def test_api_error_raises_ha_error(self, handlers):
        """VioletPoolAPIError is wrapped in HomeAssistantError."""
        from homeassistant.exceptions import HomeAssistantError
        from violet_poolcontroller_api.api import VioletPoolAPIError

        coord = make_coordinator()
        coord.device.api.set_switch_state = AsyncMock(side_effect=VioletPoolAPIError("API down"))
        handlers.manager.get_coordinators_for_call = AsyncMock(return_value=[coord])

        with pytest.raises(HomeAssistantError, match="Pump control failed"):
            await handlers.handle_control_pump(make_service_call({"action": "auto"}))


class TestHandleSmartDosing:
    """Test the handle_smart_dosing service handler."""

    @pytest.fixture
    def handlers(self):
        coordinator = make_coordinator()
        h = VioletControlServiceHandlers()
        h.manager = make_manager_with_safety(coordinator)
        h.hass = h.manager.hass
        h.manager.get_coordinators_for_call = AsyncMock(return_value=[coordinator])
        # The guard resolves the controller through this entry, so tests must
        # act on the same coordinator the manager was wired to.
        h.test_coordinator = coordinator
        return h

    async def test_dosing_ph_minus(self, handlers):
        """pH- manual dosing calls manual_dosing API."""
        coord = handlers.test_coordinator

        await handlers.handle_smart_dosing(
            make_service_call(
                {
                    "dosing_type": "pH-",
                    "action": "manual_dose",
                    "duration": 30,
                }
            )
        )

        coord.device.api.manual_dosing.assert_awaited_once()
        coord.async_request_refresh.assert_awaited_once()

    async def test_dosing_auto(self, handlers):
        """Auto dosing calls set_dosage_enabled."""
        coord = handlers.test_coordinator

        await handlers.handle_smart_dosing(
            make_service_call(
                {
                    "dosing_type": "Chlorine",
                    "action": "auto",
                    "duration": 30,
                }
            )
        )

        coord.device.api.set_dosage_enabled.assert_awaited_once()

    async def test_dosing_stop(self, handlers):
        """Stop dosing calls set_switch_state with OFF."""
        coord = handlers.test_coordinator

        await handlers.handle_smart_dosing(
            make_service_call(
                {
                    "dosing_type": "Chlorine",
                    "action": "stop",
                    "duration": 30,
                }
            )
        )

        coord.device.api.set_switch_state.assert_awaited_once()
        kwargs = coord.device.api.set_switch_state.call_args[1]
        assert kwargs["action"] == "OFF"

    async def test_safety_lock_blocks(self, handlers):
        """Safety lock prevents dosing."""
        from homeassistant.exceptions import HomeAssistantError

        # Arm a real cooldown lock on the SafetyGuard.
        handlers.manager.safety_guard.set_lock(ENTRY_ID, "DOS_1_CL", 120)

        with pytest.raises(HomeAssistantError, match="Safety interval"):
            await handlers.handle_smart_dosing(
                make_service_call(
                    {
                        "dosing_type": "Chlorine",
                        "action": "manual_dose",
                        "duration": 30,
                    }
                )
            )

    async def test_safety_override_bypasses_lock(self, handlers):
        """Safety override flag bypasses safety lock."""
        coord = handlers.test_coordinator
        # Arm a lock, but safety_override=True should bypass it.
        handlers.manager.safety_guard.set_lock(ENTRY_ID, "DOS_1_CL", 120)

        await handlers.handle_smart_dosing(
            make_service_call(
                {
                    "dosing_type": "Chlorine",
                    "action": "manual_dose",
                    "duration": 30,
                    "safety_override": True,
                }
            )
        )

        coord.device.api.manual_dosing.assert_awaited_once()

    async def test_unknown_dosing_type_raises(self, handlers):
        """Unknown dosing type raises HomeAssistantError."""
        from homeassistant.exceptions import HomeAssistantError


        with pytest.raises(HomeAssistantError, match="Unknown dosing type"):
            await handlers.handle_smart_dosing(
                make_service_call(
                    {
                        "dosing_type": "invalid",
                        "action": "on",
                        "duration": 30,
                    }
                )
            )


class TestHandleControlExtensionRelay:
    """Test extension relay control handler.

    Until 2.7.0 this handler built the key as ``EXT<relay_id>_1``, so relay 3
    became ``EXT3_1`` - a key the controller does not have; it only has
    ``EXT1_1..EXT1_8`` and ``EXT2_1..EXT2_8``. It also sent the read state
    codes ``"4"``, ``"6"`` and ``"0"`` where the command grammar expects
    ``ON``/``OFF``/``AUTO``. Both are asserted here.
    """

    @pytest.fixture
    def handlers(self):
        coordinator = make_coordinator()
        h = VioletControlServiceHandlers()
        h.manager = make_manager_with_safety(coordinator)
        h.hass = h.manager.hass
        h.manager.get_coordinators_for_call = AsyncMock(return_value=[coordinator])
        h.test_coordinator = coordinator
        return h

    @pytest.mark.parametrize(
        ("action", "expected"),
        [("on", "ON"), ("off", "OFF"), ("auto", "AUTO")],
    )
    async def test_relay_action_is_a_command_not_a_state_code(
        self, handlers, action, expected
    ):
        coord = handlers.test_coordinator

        await handlers.handle_control_extension_relay(
            make_service_call({"bank": 1, "relay": 1, "action": action, "duration": 0})
        )

        coord.device.api.set_switch_state.assert_awaited_once_with(
            "EXT1_1", expected, duration=None
        )

    async def test_relay_addresses_the_second_bank(self, handlers):
        """Relay 5 of bank 2 is EXT2_5, not EXT5_1."""
        coord = handlers.test_coordinator

        await handlers.handle_control_extension_relay(
            make_service_call({"bank": 2, "relay": 5, "action": "on", "duration": 0})
        )

        coord.device.api.set_switch_state.assert_awaited_once_with(
            "EXT2_5", "ON", duration=None
        )

    async def test_relay_duration_is_forwarded(self, handlers):
        coord = handlers.test_coordinator

        await handlers.handle_control_extension_relay(
            make_service_call({"bank": 1, "relay": 4, "action": "on", "duration": 120})
        )

        coord.device.api.set_switch_state.assert_awaited_once_with(
            "EXT1_4", "ON", duration=120
        )

    async def test_relay_unknown_action_is_a_validation_error(self, handlers):
        """Range checks are the schema's job; an unknown action is still ours."""
        from homeassistant.exceptions import ServiceValidationError

        coord = handlers.test_coordinator

        with pytest.raises(ServiceValidationError):
            await handlers.handle_control_extension_relay(
                make_service_call({"bank": 1, "relay": 1, "action": "toggle"})
            )

        coord.device.api.set_switch_state.assert_not_awaited()


class TestHandleControlPumpHttp:
    """Test HTTP-based pump control handler."""

    @pytest.fixture
    def handlers(self):
        coordinator = make_coordinator()
        h = VioletControlServiceHandlers()
        h.manager = make_manager_with_safety(coordinator)
        h.hass = h.manager.hass
        h.manager.get_coordinators_for_call = AsyncMock(return_value=[coordinator])
        # The guard resolves the controller through this entry, so tests must
        # act on the same coordinator the manager was wired to.
        h.test_coordinator = coordinator
        return h

    async def test_pump_on(self, handlers):
        """Pump on via HTTP sends PUMP ON command."""

        with patch(
            "custom_components.violet_pool_controller.service_mixins.pump.VioletControlClient"
        ) as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.set_pump_speed = AsyncMock(return_value=True)

            await handlers.handle_control_pump_http(make_service_call({"action": "on", "speed": 2}))

            mock_client.set_pump_speed.assert_awaited_once_with(2)

    async def test_pump_off(self, handlers):
        """Pump off via HTTP sends PUMP OFF command."""

        with patch(
            "custom_components.violet_pool_controller.service_mixins.pump.VioletControlClient"
        ) as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.set_pump_off = AsyncMock(return_value=True)

            await handlers.handle_control_pump_http(make_service_call({"action": "off"}))

            mock_client.set_pump_off.assert_awaited_once()


class TestHandleManualDosingHttp:
    """Test HTTP-based manual dosing handler."""

    @pytest.fixture
    def handlers(self):
        coordinator = make_coordinator()
        h = VioletControlServiceHandlers()
        h.manager = make_manager_with_safety(coordinator)
        h.hass = h.manager.hass
        h.manager.get_coordinators_for_call = AsyncMock(return_value=[coordinator])
        # The guard resolves the controller through this entry, so tests must
        # act on the same coordinator the manager was wired to.
        h.test_coordinator = coordinator
        return h

    async def test_dosing_chlorine(self, handlers):
        """Chlorine dosing uses index 0."""

        with patch(
            "custom_components.violet_pool_controller.service_mixins.dosing.VioletControlClient"
        ) as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.trigger_manual_dosing = AsyncMock(return_value=True)

            await handlers.handle_manual_dosing_http(
                make_service_call(
                    {
                        "dosing_system": "chlorine",
                        "runtime_seconds": 30,
                    }
                )
            )

            mock_client.trigger_manual_dosing.assert_awaited_once()
            args = mock_client.trigger_manual_dosing.call_args[0]
            assert args[0] == DOSING_INDEX_MAP["chlorine"]

    async def test_dosing_unknown_system(self, handlers):
        """Unknown dosing system raises HomeAssistantError."""
        from homeassistant.exceptions import HomeAssistantError


        with pytest.raises(HomeAssistantError, match="Unknown dosing system"):
            await handlers.handle_manual_dosing_http(
                make_service_call(
                    {
                        "dosing_system": "invalid",
                        "runtime_seconds": 30,
                    }
                )
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
        coordinator = make_coordinator()
        h = VioletControlServiceHandlers()
        h.manager = make_manager_with_safety(coordinator)
        h.hass = h.manager.hass
        h.manager.get_coordinators_for_call = AsyncMock(return_value=[coordinator])
        # The guard resolves the controller through this entry, so tests must
        # act on the same coordinator the manager was wired to.
        h.test_coordinator = coordinator
        return h

    async def test_heater_on(self, handlers):
        with patch(
            "custom_components.violet_pool_controller.service_mixins.climate.VioletControlClient"
        ) as cls:
            cls.return_value.set_heater_on = AsyncMock(return_value=True)
            cls.return_value.set_config = AsyncMock(return_value=True)
            await handlers.handle_control_heater_http(
                make_service_call({"action": "on", "target_temperature": 28.0})
            )
            cls.return_value.set_heater_on.assert_awaited_once()
            cls.return_value.set_config.assert_awaited_once()

    async def test_heater_off(self, handlers):
        with patch(
            "custom_components.violet_pool_controller.service_mixins.climate.VioletControlClient"
        ) as cls:
            cls.return_value.set_heater_off = AsyncMock(return_value=True)
            await handlers.handle_control_heater_http(make_service_call({"action": "off"}))
            cls.return_value.set_heater_off.assert_awaited_once()


class TestHandleControlSolarHttp:
    """Test HTTP-based solar control handler."""

    @pytest.fixture
    def handlers(self):
        coordinator = make_coordinator()
        h = VioletControlServiceHandlers()
        h.manager = make_manager_with_safety(coordinator)
        h.hass = h.manager.hass
        h.manager.get_coordinators_for_call = AsyncMock(return_value=[coordinator])
        # The guard resolves the controller through this entry, so tests must
        # act on the same coordinator the manager was wired to.
        h.test_coordinator = coordinator
        return h

    async def test_solar_on(self, handlers):
        with patch(
            "custom_components.violet_pool_controller.service_mixins.climate.VioletControlClient"
        ) as cls:
            cls.return_value.set_solar_on = AsyncMock(return_value=True)
            await handlers.handle_control_solar_http(make_service_call({"action": "on"}))
            cls.return_value.set_solar_on.assert_awaited_once()

    async def test_solar_off(self, handlers):
        with patch(
            "custom_components.violet_pool_controller.service_mixins.climate.VioletControlClient"
        ) as cls:
            cls.return_value.set_solar_off = AsyncMock(return_value=True)
            await handlers.handle_control_solar_http(make_service_call({"action": "off"}))
            cls.return_value.set_solar_off.assert_awaited_once()


class TestHandleControlCoverHttp:
    """Test HTTP-based cover control handler."""

    @pytest.fixture
    def handlers(self):
        coordinator = make_coordinator()
        h = VioletControlServiceHandlers()
        h.manager = make_manager_with_safety(coordinator)
        h.hass = h.manager.hass
        h.manager.get_coordinators_for_call = AsyncMock(return_value=[coordinator])
        # The guard resolves the controller through this entry, so tests must
        # act on the same coordinator the manager was wired to.
        h.test_coordinator = coordinator
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
        with patch(
            "custom_components.violet_pool_controller.service_mixins.cover.VioletControlClient"
        ) as cls:
            setattr(cls.return_value, method, AsyncMock(return_value=True))
            await handlers.handle_control_cover_http(make_service_call({"action": action}))
            getattr(cls.return_value, method).assert_awaited_once()


class TestHandleControlBackwashHttp:
    """Test HTTP-based backwash control handler."""

    @pytest.fixture
    def handlers(self):
        coordinator = make_coordinator()
        h = VioletControlServiceHandlers()
        h.manager = make_manager_with_safety(coordinator)
        h.hass = h.manager.hass
        h.manager.get_coordinators_for_call = AsyncMock(return_value=[coordinator])
        # The guard resolves the controller through this entry, so tests must
        # act on the same coordinator the manager was wired to.
        h.test_coordinator = coordinator
        return h

    async def test_backwash_abort(self, handlers):
        coord = handlers.test_coordinator

        await handlers.handle_control_backwash_http(make_service_call({"action": "abort"}))

        coord.device.api.set_switch_state.assert_awaited_once_with("BACKWASH", "OFF")

    async def test_backwash_run_requires_duration(self, handlers):
        """Run action requires duration_seconds for safety."""
        from homeassistant.exceptions import HomeAssistantError

        with pytest.raises(HomeAssistantError, match="duration is required"):
            await handlers.handle_control_backwash_http(make_service_call({"action": "run"}))

    async def test_backwash_run_passes_the_duration_to_the_controller(self, handlers):
        """The controller has to carry the timeout, not only Home Assistant.

        The start command used to be sent without a duration, so the whole
        safety timeout depended on Home Assistant still being alive.
        """
        coord = handlers.test_coordinator

        await handlers.handle_control_backwash_http(
            make_service_call({"action": "run", "duration_seconds": 120})
        )

        coord.device.api.set_switch_state.assert_awaited_once_with(
            "BACKWASH", "ON", duration=120
        )


class TestHandleControlRefillHttp:
    """Test HTTP-based refill control handler."""

    @pytest.fixture
    def handlers(self):
        coordinator = make_coordinator()
        h = VioletControlServiceHandlers()
        h.manager = make_manager_with_safety(coordinator)
        h.hass = h.manager.hass
        h.manager.get_coordinators_for_call = AsyncMock(return_value=[coordinator])
        # The guard resolves the controller through this entry, so tests must
        # act on the same coordinator the manager was wired to.
        h.test_coordinator = coordinator
        return h

    async def test_refill_stop(self, handlers):
        coord = handlers.test_coordinator

        await handlers.handle_control_refill_http(make_service_call({"action": "stop"}))

        coord.device.api.set_switch_state.assert_awaited_once_with("REFILL", "OFF")

    async def test_refill_fill_requires_duration(self, handlers):
        """Fill action requires duration_seconds for safety."""
        from homeassistant.exceptions import HomeAssistantError

        with pytest.raises(HomeAssistantError, match="duration_seconds"):
            await handlers.handle_control_refill_http(make_service_call({"action": "fill"}))

    async def test_refill_fill_passes_the_duration_to_the_controller(self, handlers):
        """The valve must close on its own if Home Assistant dies mid-refill.

        The start command used to be sent without a duration, so the only
        thing that would ever have closed it was an HA-side timer whose stop
        command named a method the controller API does not have.
        """
        coord = handlers.test_coordinator

        await handlers.handle_control_refill_http(
            make_service_call({"action": "fill", "duration_seconds": 60})
        )

        coord.device.api.set_switch_state.assert_awaited_once_with("REFILL", "ON", duration=60)

    async def test_refill_arms_a_stop_the_api_can_actually_dispatch(self, handlers):
        """The persisted auto-stop must name a real method on the API."""
        await handlers.handle_control_refill_http(
            make_service_call({"action": "fill", "duration_seconds": 60})
        )

        stored = (await handlers.manager.safety_guard._persistence.async_load())["auto_stops"]
        target = stored[f"{ENTRY_ID}::REFILL"]["stop_target"]
        assert callable(getattr(handlers.test_coordinator.device.api, target["method"], None))


class TestHandleManagePvSurplus:
    """Test PV surplus management handler."""

    @pytest.fixture
    def handlers(self):
        coordinator = make_coordinator()
        h = VioletControlServiceHandlers()
        h.manager = make_manager_with_safety(coordinator)
        h.hass = h.manager.hass
        h.manager.get_coordinators_for_call = AsyncMock(return_value=[coordinator])
        # The guard resolves the controller through this entry, so tests must
        # act on the same coordinator the manager was wired to.
        h.test_coordinator = coordinator
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
        await handlers.handle_manage_pv_surplus(make_service_call({"mode": "deactivate"}))
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
