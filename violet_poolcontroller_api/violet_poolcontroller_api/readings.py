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

"""Typed, read-only view over a /getReadings API snapshot.

:class:`VioletReadings` wraps the raw ``dict[str, Any]`` returned by the
controller and exposes documented fields as typed, lazily-evaluated properties.
It implements the :class:`collections.abc.Mapping` protocol, so all existing
code that accesses ``coordinator.data.get("KEY")`` or ``"KEY" in
coordinator.data`` continues to work unchanged — the typed accessors are purely
additive.

Usage::

    readings = VioletReadings(raw_dict)

    # Backward-compatible dict-style access (works on Mapping)
    temp = readings.get("onewire1_value")

    # New typed accessors
    if readings.pump is not None and readings.pump.is_on:
        print("Pump is running")

    ph = readings.ph  # float | None, already cast from the raw string
    for idx, state in readings.onewire_states.items():
        if state is not None and state != OnewireState.OK:
            print(f"Sensor {idx} fault: {state}")
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from datetime import timedelta
from functools import cached_property
from types import MappingProxyType
from typing import Any

from .const_devices import (
    CoverState,
    DmxSceneState,
    OnewireState,
    OutputState,
    PvSurplusState,
    RuleState,
)
from .parsers import parse_runtime_string, parse_uptime_string

# ---------------------------------------------------------------------------
# Module-level helpers (not part of the public API)
# ---------------------------------------------------------------------------

_DOSING_KEYS = ("DOS_1_CL", "DOS_2_ELO", "DOS_4_PHM", "DOS_5_PHP", "DOS_6_FLOC")


def _opt_float(raw: Any) -> float | None:  # noqa: ANN401
    """Return ``float(raw)`` or ``None`` if the value is absent or non-numeric."""
    if raw is None:
        return None
    try:
        return float(raw)
    except (ValueError, TypeError):
        return None


def _parse_output_state(raw: Any) -> OutputState | None:  # noqa: ANN401
    """Convert a raw output state value to :class:`OutputState`.

    Handles:
    * Plain integers / integer strings: ``"4"`` → ``OutputState.MANUAL_ON``
    * Composite strings with pipe separator: ``"3|PUMP_ANTI_FREEZE"`` →
      ``OutputState.AUTO_PRIO_ON`` (numeric prefix is used)
    """
    if raw is None:
        return None
    try:
        numeric = str(raw).split("|")[0].strip()
        return OutputState(int(numeric))
    except (ValueError, KeyError):
        return None


def _parse_dmx_state(raw: Any) -> DmxSceneState | None:  # noqa: ANN401
    """Convert a raw DMX scene state to :class:`DmxSceneState`."""
    if raw is None:
        return None
    try:
        return DmxSceneState(int(raw))
    except (ValueError, KeyError):
        return None


def _parse_rule_state(raw: Any) -> RuleState | None:  # noqa: ANN401
    """Convert a raw digital rule state to :class:`RuleState`."""
    if raw is None:
        return None
    try:
        return RuleState(int(raw))
    except (ValueError, KeyError):
        return None


def _parse_cover_state(raw: Any) -> CoverState | None:  # noqa: ANN401
    """Convert a COVER_STATE string to :class:`CoverState`."""
    if raw is None:
        return None
    try:
        return CoverState(str(raw).strip().upper())
    except ValueError:
        return None


def _parse_onewire_state(raw: Any) -> OnewireState | None:  # noqa: ANN401
    """Convert a 1-wire sensor state string to :class:`OnewireState`."""
    if raw is None:
        return None
    try:
        return OnewireState(str(raw).strip())
    except ValueError:
        return None


def _parse_pv_surplus(raw: Any) -> PvSurplusState | None:  # noqa: ANN401
    """Convert a PVSURPLUS value to :class:`PvSurplusState`."""
    if raw is None:
        return None
    try:
        return PvSurplusState(int(raw))
    except (ValueError, KeyError):
        return None


# ---------------------------------------------------------------------------
# Public class
# ---------------------------------------------------------------------------


class VioletReadings(Mapping[str, Any]):
    """Typed, immutable view over a single /getReadings API snapshot.

    Implements :class:`~collections.abc.Mapping` so it is a drop-in
    replacement for the raw ``dict[str, Any]`` previously returned by
    :meth:`~violet_poolcontroller_api.api.VioletPoolAPI.get_readings`.

    Typed accessors use :func:`~functools.cached_property` so that repeated
    access within the same poll cycle is free.  The cache is invalidated
    automatically when a new :class:`VioletReadings` object is created for
    the next poll.

    Attributes:
        raw: :class:`~types.MappingProxyType` view of the underlying dict for
            read-only access to undocumented or firmware-specific keys that
            are not yet exposed as typed properties.
    """

    def __init__(self, raw: dict[str, Any]) -> None:
        """Wrap a raw /getReadings response.

        Args:
            raw: The ``dict`` returned by the controller (already flattened
                and sanitised by :meth:`VioletPoolAPI.get_readings`).
                A defensive copy is made to prevent external mutations from
                invalidating the :func:`cached_property` values.
        """
        self._raw: dict[str, Any] = dict(raw)

    # ------------------------------------------------------------------
    # Mapping protocol (required)
    # ------------------------------------------------------------------

    def __getitem__(self, key: str) -> Any:  # noqa: ANN401
        return self._raw[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._raw)

    def __len__(self) -> int:
        return len(self._raw)

    # ------------------------------------------------------------------
    # Raw access
    # ------------------------------------------------------------------

    @property
    def raw(self) -> MappingProxyType[str, Any]:
        """Read-only proxy of the underlying dict.

        Use this to access keys that are not yet exposed as typed properties
        (e.g. undocumented or firmware-specific fields).
        """
        return MappingProxyType(self._raw)

    # ------------------------------------------------------------------
    # System information
    # ------------------------------------------------------------------

    @cached_property
    def sw_version(self) -> str | None:
        """Software version string of the Violet application (e.g. ``"1.1.9"``)."""
        v = self._raw.get("SW_VERSION")
        return str(v).strip() if v is not None else None

    @cached_property
    def cpu_temp(self) -> float | None:
        """CPU temperature in °C (main board)."""
        return _opt_float(self._raw.get("CPU_TEMP"))

    @cached_property
    def cpu_temp_carrier(self) -> float | None:
        """CPU temperature in °C (carrier board)."""
        return _opt_float(self._raw.get("CPU_TEMP_CARRIER"))

    @cached_property
    def cpu_uptime(self) -> timedelta:
        """System uptime since last boot as a :class:`~datetime.timedelta`."""
        raw = self._raw.get("CPU_UPTIME", "")
        return parse_uptime_string(str(raw))

    @cached_property
    def memory_usage_mb(self) -> float | None:
        """Total system memory used in MB."""
        return _opt_float(self._raw.get("SYSTEM_MEMORY"))

    # ------------------------------------------------------------------
    # Water chemistry
    # ------------------------------------------------------------------

    @cached_property
    def ph(self) -> float | None:
        """Current pH reading (2 decimal places)."""
        return _opt_float(self._raw.get("pH_value"))

    @cached_property
    def ph_min(self) -> float | None:
        """Today's minimum pH reading (reset nightly at 00:00)."""
        return _opt_float(self._raw.get("pH_value_min"))

    @cached_property
    def ph_max(self) -> float | None:
        """Today's maximum pH reading (reset nightly at 00:00)."""
        return _opt_float(self._raw.get("pH_value_max"))

    @cached_property
    def orp(self) -> float | None:
        """Current ORP / redox potential in mV."""
        return _opt_float(self._raw.get("orp_value"))

    @cached_property
    def orp_min(self) -> float | None:
        """Today's minimum ORP reading in mV."""
        return _opt_float(self._raw.get("orp_value_min"))

    @cached_property
    def orp_max(self) -> float | None:
        """Today's maximum ORP reading in mV."""
        return _opt_float(self._raw.get("orp_value_max"))

    @cached_property
    def chlorine(self) -> float | None:
        """Current chlorine / potentiometric sensor reading in mg/L."""
        return _opt_float(self._raw.get("pot_value"))

    @cached_property
    def chlorine_min(self) -> float | None:
        """Today's minimum chlorine reading in mg/L."""
        return _opt_float(self._raw.get("pot_value_min"))

    @cached_property
    def chlorine_max(self) -> float | None:
        """Today's maximum chlorine reading in mg/L."""
        return _opt_float(self._raw.get("pot_value_max"))

    # ------------------------------------------------------------------
    # Main output states
    # ------------------------------------------------------------------

    @cached_property
    def pump(self) -> OutputState | None:
        """Current pump output state.

        Composite states such as ``"3|PUMP_ANTI_FREEZE"`` are reduced to
        their numeric prefix (``OutputState.AUTO_PRIO_ON`` in that case).
        """
        return _parse_output_state(self._raw.get("PUMP"))

    @cached_property
    def pump_runtime(self) -> timedelta:
        """Today's pump runtime as a :class:`~datetime.timedelta`."""
        return parse_runtime_string(str(self._raw.get("PUMP_RUNTIME", "")))

    @cached_property
    def solar(self) -> OutputState | None:
        """Current solar output state."""
        return _parse_output_state(self._raw.get("SOLAR"))

    @cached_property
    def solar_runtime(self) -> timedelta:
        """Today's solar runtime."""
        return parse_runtime_string(str(self._raw.get("SOLAR_RUNTIME", "")))

    @cached_property
    def heater(self) -> OutputState | None:
        """Current heater output state."""
        return _parse_output_state(self._raw.get("HEATER"))

    @cached_property
    def heater_runtime(self) -> timedelta:
        """Today's heater runtime."""
        return parse_runtime_string(str(self._raw.get("HEATER_RUNTIME", "")))

    @cached_property
    def light(self) -> OutputState | None:
        """Current pool light output state."""
        return _parse_output_state(self._raw.get("LIGHT"))

    @cached_property
    def eco(self) -> OutputState | None:
        """Current eco-mode output state."""
        return _parse_output_state(self._raw.get("ECO"))

    @cached_property
    def backwash(self) -> OutputState | None:
        """Current backwash output state."""
        return _parse_output_state(self._raw.get("BACKWASH"))

    @cached_property
    def backwashrinse(self) -> OutputState | None:
        """Current backwash-rinse output state."""
        return _parse_output_state(self._raw.get("BACKWASHRINSE"))

    @cached_property
    def refill(self) -> OutputState | None:
        """Current water-refill output state."""
        return _parse_output_state(self._raw.get("REFILL"))

    # ------------------------------------------------------------------
    # Special outputs
    # ------------------------------------------------------------------

    @cached_property
    def pv_surplus(self) -> PvSurplusState | None:
        """Current PV surplus state (distinct 0/1/2 scheme, not 0-6).

        ``None`` means the key was absent in the snapshot.
        """
        return _parse_pv_surplus(self._raw.get("PVSURPLUS"))

    @cached_property
    def cover(self) -> CoverState | None:
        """Current pool cover state.

        ``None`` when no cover is configured or the key is absent.
        """
        return _parse_cover_state(self._raw.get("COVER_STATE"))

    # ------------------------------------------------------------------
    # 1-wire temperature sensors (indices 1-12)
    # ------------------------------------------------------------------

    @cached_property
    def onewire_temperatures(self) -> dict[int, float | None]:
        """Current temperature readings for all 12 1-wire sensors.

        Keys are sensor indices 1–12.  A value of ``None`` means no sensor is
        configured for that slot or the reading is unavailable.
        """
        return {i: _opt_float(self._raw.get(f"onewire{i}_value")) for i in range(1, 13)}

    @cached_property
    def onewire_states(self) -> dict[int, OnewireState | None]:
        """Fault states for all 12 1-wire sensors.

        Keys are sensor indices 1–12.
        """
        return {i: _parse_onewire_state(self._raw.get(f"onewire{i}_state")) for i in range(1, 13)}

    # ------------------------------------------------------------------
    # Analog / impulse inputs
    # ------------------------------------------------------------------

    @cached_property
    def analog_inputs(self) -> dict[int, float | None]:
        """Current readings for analog inputs ADC1–ADC6 (or ADC5, firmware-dependent).

        Keys are input indices 1–6.
        """
        return {i: _opt_float(self._raw.get(f"ADC{i}_value")) for i in range(1, 7)}

    @cached_property
    def impulse_inputs(self) -> dict[int, float | None]:
        """Current readings for impulse inputs IMP1–IMP2."""
        return {i: _opt_float(self._raw.get(f"IMP{i}_value")) for i in range(1, 3)}

    @cached_property
    def digital_inputs(self) -> dict[int, bool]:
        """State of digital inputs INPUT1–INPUT12.

        ``True`` means the input is closed (logic 1), ``False`` means open (0).
        Absent inputs default to ``False``.
        """
        return {i: bool(int(self._raw.get(f"INPUT{i}", 0) or 0)) for i in range(1, 13)}

    # ------------------------------------------------------------------
    # Dosing channel output states
    # ------------------------------------------------------------------

    @cached_property
    def dosing_states(self) -> dict[str, OutputState | None]:
        """Output states for all dosing channels.

        Keys: ``"DOS_1_CL"``, ``"DOS_2_ELO"``, ``"DOS_4_PHM"``,
        ``"DOS_5_PHP"``, ``"DOS_6_FLOC"``.
        """
        return {key: _parse_output_state(self._raw.get(key)) for key in _DOSING_KEYS}

    @cached_property
    def dosing_daily_amounts_ml(self) -> dict[str, int | None]:
        """Today's dosing amounts in mL for each dosing channel."""
        return {
            key: (
                int(v)
                if (v := self._raw.get(f"{key}_DAILY_DOSING_AMOUNT_ML")) is not None
                else None
            )
            for key in _DOSING_KEYS
        }

    # ------------------------------------------------------------------
    # DMX light scenes (1-12)
    # ------------------------------------------------------------------

    @cached_property
    def dmx_scenes(self) -> dict[int, DmxSceneState | None]:
        """States for all 12 DMX light scenes.

        Keys are scene indices 1–12.
        """
        return {i: _parse_dmx_state(self._raw.get(f"DMX_SCENE{i}")) for i in range(1, 13)}

    # ------------------------------------------------------------------
    # Extension relay banks (EXT1 and EXT2, 8 relays each)
    # ------------------------------------------------------------------

    @cached_property
    def extension_relays(self) -> dict[str, OutputState | None]:
        """States for all extension relay outputs.

        Keys follow the ``"EXT{bank}_{relay}"`` pattern, e.g. ``"EXT1_3"`` for
        relay 3 of bank 1.  Keys whose hardware module is absent are still
        included (they will be ``None``).
        """
        return {
            f"EXT{bank}_{relay}": _parse_output_state(self._raw.get(f"EXT{bank}_{relay}"))
            for bank in (1, 2)
            for relay in range(1, 9)
        }

    # ------------------------------------------------------------------
    # Digital input switching rules (1-8)
    # ------------------------------------------------------------------

    @cached_property
    def digital_rules(self) -> dict[int, RuleState | None]:
        """States for digital-input switching rules 1–8."""
        return {
            i: _parse_rule_state(self._raw.get(f"DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_{i}"))
            for i in range(1, 9)
        }

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        pump_s = self.pump.name if self.pump is not None else "?"
        ph_s = f"{self.ph:.2f}" if self.ph is not None else "?"
        orp_s = f"{self.orp:.0f}" if self.orp is not None else "?"
        return f"VioletReadings(keys={len(self._raw)}, pump={pump_s}, pH={ph_s}, ORP={orp_s})"
