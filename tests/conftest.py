# violet-poolController-api - API für Violet Pool Controller
# Copyright (C) 2024-2026  Xerolux
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Pytest configuration and fixtures."""

from __future__ import annotations

from inspect import signature

import aiohttp.client_reqrep


# Monkey-patch aiohttp.ClientResponse to handle missing stream_writer parameter
# This is needed for compatibility with aioresponses 0.7.8 and aiohttp 3.13+
_original_client_response_init = aiohttp.client_reqrep.ClientResponse.__init__


def _patched_client_response_init(self: aiohttp.client_reqrep.ClientResponse, *args, **kwargs) -> None:
    """Patched ClientResponse.__init__ that adds stream_writer if missing."""
    sig = signature(_original_client_response_init)
    if "stream_writer" in sig.parameters and "stream_writer" not in kwargs:
        kwargs["stream_writer"] = None
    _original_client_response_init(self, *args, **kwargs)


aiohttp.client_reqrep.ClientResponse.__init__ = _patched_client_response_init
