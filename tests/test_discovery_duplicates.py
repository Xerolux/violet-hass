"""A controller that is already set up must not be offered again.

Reported on the forum: even with the current version installed,
Home Assistant keeps discovering "new" Violet Pool Controllers and offering to
set them up again.

The config flow aborts a zeroconf discovery through
``_abort_if_unique_id_configured()`` and ``_host_already_configured()``.
These checks handle:
- missing or legacy unique_ids
- url schemes (http://, https://) and ports
- hostnames vs IP addresses
- ZeroconfServiceInfo objects with hostname, name, and ip_addresses
"""

from __future__ import annotations

import ipaddress
from unittest.mock import MagicMock

from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from custom_components.violet_pool_controller import _backfill_unique_id
from custom_components.violet_pool_controller.config_flow import ConfigFlow
from custom_components.violet_pool_controller.const import CONF_API_URL, CONF_DEVICE_ID


def _entry(data: dict, unique_id: str | None = None) -> MagicMock:
    """A config entry stub carrying just what the code under test reads."""
    entry = MagicMock()
    entry.data = data
    entry.unique_id = unique_id
    return entry


class TestBackfillUniqueId:
    """Entries without a unique id are what discovery could not match."""

    def test_an_entry_without_one_gets_it(self) -> None:
        hass = MagicMock()
        entry = _entry({CONF_API_URL: "192.168.1.50", CONF_DEVICE_ID: 1})

        _backfill_unique_id(hass, entry)

        hass.config_entries.async_update_entry.assert_called_once_with(
            entry, unique_id="192.168.1.50-1"
        )

    def test_an_entry_with_url_gets_normalized_id(self) -> None:
        hass = MagicMock()
        entry = _entry({CONF_API_URL: "http://192.168.1.50:80", CONF_DEVICE_ID: 1})

        _backfill_unique_id(hass, entry)

        hass.config_entries.async_update_entry.assert_called_once_with(
            entry, unique_id="192.168.1.50-1"
        )

    def test_an_entry_that_has_one_is_left_alone(self) -> None:
        hass = MagicMock()
        entry = _entry({CONF_API_URL: "192.168.1.50"}, unique_id="192.168.1.50-1")

        _backfill_unique_id(hass, entry)

        hass.config_entries.async_update_entry.assert_not_called()

    def test_the_device_id_is_part_of_it(self) -> None:
        """Two controllers on one host differ only by device id."""
        hass = MagicMock()

        _backfill_unique_id(hass, _entry({CONF_API_URL: "192.168.1.50", CONF_DEVICE_ID: 2}))

        hass.config_entries.async_update_entry.assert_called_once()
        assert hass.config_entries.async_update_entry.call_args.kwargs["unique_id"] == (
            "192.168.1.50-2"
        )

    def test_the_legacy_host_key_is_understood(self) -> None:
        """Entries predating the current key store the address under `base_ip`."""
        hass = MagicMock()

        _backfill_unique_id(hass, _entry({"base_ip": "10.0.0.5"}))

        assert hass.config_entries.async_update_entry.call_args.kwargs[
            "unique_id"
        ] == "10.0.0.5-1"

    def test_an_entry_naming_no_host_is_skipped(self) -> None:
        """Nothing to build an id from - and it must not raise."""
        hass = MagicMock()

        _backfill_unique_id(hass, _entry({CONF_DEVICE_ID: 1}))

        hass.config_entries.async_update_entry.assert_not_called()

    def test_a_broken_device_id_falls_back_to_one(self) -> None:
        hass = MagicMock()

        _backfill_unique_id(hass, _entry({CONF_API_URL: "192.168.1.50", CONF_DEVICE_ID: "x"}))

        assert hass.config_entries.async_update_entry.call_args.kwargs["unique_id"] == (
            "192.168.1.50-1"
        )


class TestHostAlreadyConfigured:
    """The second guard: match on the host, whatever the unique id says."""

    def _flow(self, entries: list) -> ConfigFlow:
        flow = ConfigFlow()
        flow._async_current_entries = lambda: entries  # type: ignore[method-assign]
        return flow

    def test_a_configured_host_is_recognised(self) -> None:
        flow = self._flow([_entry({CONF_API_URL: "192.168.1.50"})])

        assert flow._host_already_configured("192.168.1.50")

    def test_recognised_with_http_prefix(self) -> None:
        flow = self._flow([_entry({CONF_API_URL: "http://192.168.1.50:80/"})])

        assert flow._host_already_configured("192.168.1.50")

    def test_recognised_even_without_a_unique_id(self) -> None:
        """This is the case the unique id check cannot see."""
        flow = self._flow([_entry({CONF_API_URL: "192.168.1.50"}, unique_id=None)])

        assert flow._host_already_configured("192.168.1.50")

    def test_recognised_through_the_legacy_key(self) -> None:
        flow = self._flow([_entry({"base_ip": "192.168.1.50"})])

        assert flow._host_already_configured("192.168.1.50")

    def test_surrounding_whitespace_does_not_hide_it(self) -> None:
        flow = self._flow([_entry({CONF_API_URL: " 192.168.1.50 "})])

        assert flow._host_already_configured("192.168.1.50")

    def test_hostname_matching(self) -> None:
        flow = self._flow([_entry({CONF_API_URL: "violet.local"})])

        assert flow._host_already_configured("violet.local")
        assert flow._host_already_configured("violet")

    def test_zeroconf_service_info_matching_by_ip(self) -> None:
        flow = self._flow([_entry({CONF_API_URL: "192.168.1.50"})])

        info = ZeroconfServiceInfo(
            ip_address=ipaddress.ip_address("192.168.1.50"),
            ip_addresses=[ipaddress.ip_address("192.168.1.50")],
            port=80,
            hostname="violet.local.",
            name="violet ._http._tcp.local.",
            type="_http._tcp.local.",
            properties={},
        )
        assert flow._host_already_configured(info)

    def test_zeroconf_service_info_matching_by_hostname(self) -> None:
        flow = self._flow([_entry({CONF_API_URL: "violet.local"})])

        info = ZeroconfServiceInfo(
            ip_address=ipaddress.ip_address("192.168.1.99"),  # DHCP IP changed
            ip_addresses=[ipaddress.ip_address("192.168.1.99")],
            port=80,
            hostname="violet.local.",
            name="violet ._http._tcp.local.",
            type="_http._tcp.local.",
            properties={},
        )
        assert flow._host_already_configured(info)

    def test_zeroconf_service_info_matching_by_service_name(self) -> None:
        flow = self._flow([_entry({CONF_API_URL: "violet"})])

        info = ZeroconfServiceInfo(
            ip_address=ipaddress.ip_address("192.168.1.99"),
            ip_addresses=[ipaddress.ip_address("192.168.1.99")],
            port=80,
            hostname="poolcontroller.local.",
            name="violet ._http._tcp.local.",
            type="_http._tcp.local.",
            properties={},
        )
        assert flow._host_already_configured(info)

    def test_a_different_host_is_still_offered(self) -> None:
        """A genuinely new controller must still be discoverable."""
        flow = self._flow([_entry({CONF_API_URL: "192.168.1.50"})])

        assert not flow._host_already_configured("192.168.1.51")

    def test_no_entries_at_all(self) -> None:
        assert not self._flow([])._host_already_configured("192.168.1.50")
