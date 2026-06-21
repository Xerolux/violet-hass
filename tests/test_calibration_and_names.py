"""Tests for calibration helper and entity name resolution."""
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from custom_components.violet_pool_controller.calibration_helper import (
    CALIBRATION_CRITICAL_DAYS,
    CALIBRATION_INTERVALS,
    CalibrationStatus,
    parse_calibration_data,
)
from custom_components.violet_pool_controller.entity_names import (
    EntityNameResolver,
    apply_hardware_names,
)


class TestCalibrationStatus:
    """Test CalibrationStatus class."""

    def test_no_calibration_unknown(self):
        """No calibration date returns Unknown status."""
        status = CalibrationStatus("pH")
        assert status.status == "Unknown"
        assert status.is_expired is True
        assert status.is_warning is False
        assert status.days_since_calibration is None
        assert status.next_calibration_date is None

    def test_recent_calibration_ok(self):
        """Recent calibration returns OK status."""
        recent = datetime.now() - timedelta(days=5)
        status = CalibrationStatus("pH", last_calibration=recent)
        assert status.status == "OK"
        assert status.is_expired is False
        assert status.is_warning is False
        assert status.days_since_calibration == 5

    def test_expired_calibration(self):
        """Past interval returns Expired status."""
        old = datetime.now() - timedelta(days=45)
        status = CalibrationStatus("pH", last_calibration=old)
        assert status.status == "Expired"
        assert status.is_expired is True
        assert status.is_warning is False

    def test_warning_calibration(self):
        """Within warning window returns Warning status."""
        ph_interval = CALIBRATION_INTERVALS["pH"]  # 30 days
        warning_date = datetime.now() - timedelta(days=ph_interval - 3)
        status = CalibrationStatus("pH", last_calibration=warning_date)
        assert status.status == "Warning"
        assert status.is_expired is False
        assert status.is_warning is True

    def test_next_calibration_date(self):
        """Next calibration date is calculated correctly."""
        cal_date = datetime.now() - timedelta(days=10)
        status = CalibrationStatus("ORP", last_calibration=cal_date)
        expected = cal_date + timedelta(days=CALIBRATION_INTERVALS["ORP"])
        assert status.next_calibration_date is not None
        diff = abs((status.next_calibration_date - expected).total_seconds())
        assert diff < 60  # Within a minute

    def test_to_dict(self):
        """to_dict returns all fields."""
        cal_date = datetime.now() - timedelta(days=10)
        status = CalibrationStatus(
            "pH", last_calibration=cal_date, offset=0.5, multiplier=1.1
        )
        d = status.to_dict()
        assert d["sensor_type"] == "pH"
        assert d["days_since"] == 10
        assert d["status"] == "OK"
        assert d["is_expired"] is False
        assert d["offset"] == 0.5
        assert d["multiplier"] == 1.1
        assert d["last_calibration"] is not None

    def test_to_dict_no_calibration(self):
        """to_dict with no calibration."""
        status = CalibrationStatus("pH")
        d = status.to_dict()
        assert d["last_calibration"] is None
        assert d["next_calibration"] is None
        assert d["status"] == "Unknown"

    def test_unknown_sensor_type_uses_default_interval(self):
        """Unknown sensor type uses default 90-day interval."""
        recent = datetime.now() - timedelta(days=50)
        status = CalibrationStatus("unknown_sensor", last_calibration=recent)
        assert status.is_expired is False
        assert status.days_since_calibration == 50

    def test_critical_threshold(self):
        """Calibration critical days after interval."""
        ph_interval = CALIBRATION_INTERVALS["pH"]
        critical_date = datetime.now() - timedelta(
            days=ph_interval + CALIBRATION_CRITICAL_DAYS + 1
        )
        status = CalibrationStatus("pH", last_calibration=critical_date)
        assert status.is_expired is True


class TestParseCalibrationData:
    """Test parse_calibration_data function."""

    def test_parse_ph(self):
        """Parse pH calibration data."""
        data = {
            "PH_calibration_date": "15.06.2026",
            "PH_offset": 0.3,
            "PH_multiplier": 1.05,
        }
        calibrations = parse_calibration_data(data)
        assert "pH" in calibrations
        assert calibrations["pH"].offset == 0.3
        assert calibrations["pH"].multiplier == 1.05

    def test_parse_orp(self):
        """Parse ORP calibration data."""
        data = {
            "ORP_calibration_date": "2026-06-15",
            "ORP_offset": -2.0,
            "ORP_multiplier": 0.98,
        }
        calibrations = parse_calibration_data(data)
        assert "ORP" in calibrations
        assert calibrations["ORP"].offset == -2.0

    def test_parse_conductivity(self):
        """Parse conductivity calibration data."""
        data = {
            "COND_calibration_date": "15/06/2026",
            "COND_offset": 1.0,
            "COND_multiplier": 1.0,
        }
        calibrations = parse_calibration_data(data)
        assert "conductivity" in calibrations

    def test_parse_empty(self):
        """Empty data returns empty dict."""
        calibrations = parse_calibration_data({})
        assert calibrations == {}

    def test_parse_invalid_date(self):
        """Invalid date string returns None for last_calibration."""
        data = {"PH_calibration_date": "not-a-date"}
        calibrations = parse_calibration_data(data)
        assert "pH" in calibrations
        assert calibrations["pH"].last_calibration is None
        assert calibrations["pH"].status == "Unknown"

    def test_parse_missing_date(self):
        """Missing date key skips that sensor."""
        data = {"PH_offset": 0.3}
        calibrations = parse_calibration_data(data)
        assert "pH" not in calibrations


class TestEntityNameResolver:
    """Test EntityNameResolver class."""

    def test_no_config_returns_default(self):
        """No hardware config returns default name."""
        resolver = EntityNameResolver(None)
        name = resolver.resolve_entity_name("switch", "PUMP", "Default Pump")
        assert name == "Default Pump"

    def test_empty_config_returns_default(self):
        """Empty hardware config returns default name."""
        resolver = EntityNameResolver({})
        name = resolver.resolve_entity_name("switch", "PUMP", "Default Pump")
        assert name == "Default Pump"

    def test_extension_relay_name(self):
        """Extension relay name is resolved from config."""
        hw_config = {
            "extension_relays": {
                "EXT1_1": {"name": "Pool Light Relay"},
            }
        }
        resolver = EntityNameResolver(hw_config)
        name = resolver.resolve_entity_name("switch", "EXT1_1", "Default Relay")
        assert name == "Pool Light Relay"

    def test_extension_relay_not_in_config(self):
        """Extension relay not in config returns default."""
        resolver = EntityNameResolver({"extension_relays": {}})
        name = resolver.resolve_entity_name("switch", "EXT2_1", "Default Relay")
        assert name == "Default Relay"

    def test_dmx_scene_name(self):
        """DMX scene name is resolved from config."""
        hw_config = {
            "dmx_scenes": {
                "LIGHT_SCENE_1": {"name": "Party Mode"},
            }
        }
        resolver = EntityNameResolver(hw_config)
        name = resolver.resolve_entity_name("light", "LIGHT_SCENE_1", "Scene 1")
        assert name == "Party Mode"

    def test_dosing_name(self):
        """Dosing system name is resolved from config."""
        hw_config = {
            "dosing_systems": {
                "CL": {"name": "Chlorine Pump"},
            }
        }
        resolver = EntityNameResolver(hw_config)
        name = resolver.resolve_entity_name("switch", "DOS_1_CL", "Chlorine")
        assert name == "Chlorine Pump"

    def test_output_name(self):
        """Main output name is resolved from config."""
        hw_config = {
            "outputs": {
                "PUMP": {"name": "Main Circulation Pump"},
            }
        }
        resolver = EntityNameResolver(hw_config)
        name = resolver.resolve_entity_name("switch", "PUMP", "Pump")
        assert name == "Main Circulation Pump"

    def test_digital_input_name(self):
        """Digital input name is resolved via parser."""
        parser = MagicMock()
        parser.get_di_friendly_name = MagicMock(return_value="Filter Status")
        hw_config = {"digital_inputs": {"parser": parser}}
        resolver = EntityNameResolver(hw_config)
        name = resolver.resolve_entity_name("binary_sensor", "INPUT3", "DI3")
        assert name == "Filter Status"
        parser.get_di_friendly_name.assert_called_once_with(3)

    def test_unknown_key_returns_default(self):
        """Unknown key returns default name."""
        resolver = EntityNameResolver({"outputs": {}})
        name = resolver.resolve_entity_name("switch", "UNKNOWN_KEY", "Default")
        assert name == "Default"

    def test_get_resolver_from_coordinator(self):
        """get_resolver creates resolver from coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.hardware_config = {"outputs": {"PUMP": {"name": "Test"}}}
        resolver = EntityNameResolver(None).get_resolver(coordinator)
        assert resolver.hw_config is not None
        name = resolver.resolve_entity_name("switch", "PUMP", "Default")
        assert name == "Test"

    def test_get_resolver_no_device(self):
        """get_resolver handles coordinator without device."""
        coordinator = MagicMock()
        coordinator.device = None
        resolver = EntityNameResolver(None).get_resolver(coordinator)
        assert resolver.hw_config is None


class TestApplyHardwareNames:
    """Test apply_hardware_names function."""

    def test_applies_resolved_names(self):
        """Resolved names are applied to configs."""
        resolver = EntityNameResolver({
            "outputs": {"PUMP": {"name": "Custom Pump"}}
        })
        configs = [
            {"key": "PUMP", "name": "Default Pump"},
            {"key": "HEATER", "name": "Default Heater"},
        ]
        updated = apply_hardware_names(configs, resolver, "switch")
        assert updated[0]["name"] == "Custom Pump"
        assert updated[1]["name"] == "Default Heater"

    def test_preserves_other_fields(self):
        """Other fields in configs are preserved."""
        resolver = EntityNameResolver({})
        configs = [{"key": "PUMP", "name": "Pump", "icon": "mdi:pump"}]
        updated = apply_hardware_names(configs, resolver, "switch")
        assert updated[0]["icon"] == "mdi:pump"

    def test_empty_configs(self):
        """Empty config list returns empty."""
        resolver = EntityNameResolver({})
        assert apply_hardware_names([], resolver) == []

    def test_missing_key_uses_name_as_default(self):
        """Config without key uses name as default."""
        resolver = EntityNameResolver({})
        configs = [{"name": "Some Name"}]
        updated = apply_hardware_names(configs, resolver)
        assert updated[0]["name"] == "Some Name"
