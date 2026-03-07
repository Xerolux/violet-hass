"""Tests for Cover platform."""
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.violet_pool_controller import (
    async_setup_entry,
)
from custom_components.violet_pool_controller.const import (
    CONF_ACTIVE_FEATURES,
    CONF_API_URL,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_USE_SSL,
    DOMAIN,
)
from custom_components.violet_pool_controller.cover import (
    VioletCover,
    COVER_STATE_MAP,
)


@pytest.fixture
def mock_coordinator():
    """Mock coordinator."""
    class MockCoordinator:
        def __init__(self):
            self.data = {
                "COVER_STATE": "OPEN",
                "LAST_MOVING_DIRECTION": "OPEN",
            }
            self.device = MockDevice()

        async def async_request_refresh(self):
            """Mock refresh."""

    return MockCoordinator()


class MockDevice:
    """Mock device."""
    def __init__(self):
        self.device_name = "Test Pool"
        self.available = True
        self.api = MockAPI()
        self.device_info = {
            "identifiers": {("violet_pool_controller", "192.168.1.100_1")},
            "name": "Test Pool",
            "manufacturer": "PoolDigital GmbH & Co. KG",
            "model": "Violet Pool Controller",
            "sw_version": "1.0.0",
        }


class MockAPI:
    """Mock API."""
    async def set_switch_state(self, key, action):
        """Mock set_switch_state."""
        return {"success": True}


@pytest.fixture
def config_entry():
    """Mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_URL: "192.168.1.100",
            CONF_USE_SSL: False,
            CONF_DEVICE_ID: 1,
            CONF_DEVICE_NAME: "Test Pool",
        },
        options={
            CONF_ACTIVE_FEATURES: ["cover_control"],
        }
    )


class TestVioletCover:
    """Test VioletCover entity."""

    @pytest.mark.asyncio
    async def test_cover_initialization(self, mock_coordinator, config_entry):
        """Test cover initialization."""
        cover = VioletCover(mock_coordinator, config_entry)

        assert cover.name == "Pool Cover"
        assert cover.unique_id is not None
        assert cover.device_class == "shutter"
        assert cover.should_poll is False  # Coordinator-based entity; HA handles scheduling

    @pytest.mark.asyncio
    async def test_cover_is_open(self, mock_coordinator, config_entry):
        """Test cover is_open property."""
        mock_coordinator.data["COVER_STATE"] = "OPEN"
        cover = VioletCover(mock_coordinator, config_entry)

        assert cover.is_open is True
        assert cover.is_closed is False

    @pytest.mark.asyncio
    async def test_cover_is_closed(self, mock_coordinator, config_entry):
        """Test cover is_closed property."""
        mock_coordinator.data["COVER_STATE"] = "CLOSED"
        cover = VioletCover(mock_coordinator, config_entry)

        assert cover.is_closed is True
        assert cover.is_open is False

    @pytest.mark.asyncio
    async def test_cover_is_opening(self, mock_coordinator, config_entry):
        """Test cover is_opening property."""
        mock_coordinator.data["COVER_STATE"] = "OPENING"
        cover = VioletCover(mock_coordinator, config_entry)

        assert cover.is_opening is True

    @pytest.mark.asyncio
    async def test_cover_is_closing(self, mock_coordinator, config_entry):
        """Test cover is_closing property."""
        mock_coordinator.data["COVER_STATE"] = "CLOSING"
        cover = VioletCover(mock_coordinator, config_entry)

        assert cover.is_closing is True

    @pytest.mark.asyncio
    async def test_cover_open_command(self, mock_coordinator, config_entry):
        """Test cover open command."""
        cover = VioletCover(mock_coordinator, config_entry)

        await cover.async_open_cover()

        # Verify command was sent (this would make an API call in real usage)
        assert cover._last_action == "OPEN"

    @pytest.mark.asyncio
    async def test_cover_close_command(self, mock_coordinator, config_entry):
        """Test cover close command."""
        cover = VioletCover(mock_coordinator, config_entry)

        await cover.async_close_cover()

        assert cover._last_action == "CLOSE"

    @pytest.mark.asyncio
    async def test_cover_stop_command(self, mock_coordinator, config_entry):
        """Test cover stop command."""
        cover = VioletCover(mock_coordinator, config_entry)

        await cover.async_stop_cover()

        assert cover._last_action == "STOP"

    @pytest.mark.asyncio
    async def test_cover_state_map(self):
        """Test COVER_STATE_MAP mappings."""
        assert COVER_STATE_MAP.get("0") == "open"
        assert COVER_STATE_MAP.get("2") == "closed"
        assert COVER_STATE_MAP.get("1") == "opening"
        assert COVER_STATE_MAP.get("3") == "closing"

    @pytest.mark.asyncio
    async def test_cover_none_data(self, mock_coordinator, config_entry):
        """Test cover with None coordinator data."""
        mock_coordinator.data = None
        cover = VioletCover(mock_coordinator, config_entry)

        # Should return False, not crash
        assert cover.is_open is False
        assert cover.is_closed is False
