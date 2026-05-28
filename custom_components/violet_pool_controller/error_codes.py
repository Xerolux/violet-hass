# =============================================================================
# Violet Pool Controller – Home Assistant Custom Integration
# Copyright © 2026 Xerolux
# Developed and created by Xerolux
# https://github.com/Xerolux/violet-hass
# =============================================================================

"""Mappings for Violet Pool Controller error codes."""

from __future__ import annotations

# The dictionary below is intentionally focused on the most common error codes
# observed in production systems.  Unknown codes fall back to a generic
# response so the integration remains robust even when the controller ships a
# firmware with additional diagnostics.

ERROR_CODES: dict[str, dict[str, str]] = {
    "0": {
        "type": "MESSAGE",
        "subject": "Test message",
        "severity": "info",
        "description": (
            "Test message from ."
            " The message was triggered on  at  and sent on  at ."
        ),
    },
    "1": {
        "type": "MESSAGE",
        "subject": "Status message",
        "severity": "info",
        "description": "Status message from .",
    },
    "2": {
        "type": "ALERT",
        "subject": "Hardware problem (COM link to carrier faulty)",
        "severity": "critical",
        "description": "Communication link to the carrier board is faulty.",
    },
    "3": {
        "type": "REMINDER",
        "subject": "Happy Birthday",
        "severity": "info",
        "description": "Birthday greeting from the system.",
    },
    "8": {
        "type": "WARNING",
        "subject": "CPU temperature high",
        "severity": "warning",
        "description": "The main processor temperature is approaching the limit.",
    },
    "9": {
        "type": "ALERT",
        "subject": "CPU temperature too high",
        "severity": "critical",
        "description": (
            "The CPU temperature is significantly above the permissible value."
        ),
    },
    "10": {
        "type": "REMINDER",
        "subject": "Update available (Auto)",
        "severity": "info",
        "description": (
            "A software update will be automatically installed"
            " during the coming night."
        ),
    },
    "11": {
        "type": "REMINDER",
        "subject": "Update available (Confirmation required)",
        "severity": "info",
        "description": "A new software update requires manual confirmation.",
    },
    "12": {
        "type": "REMINDER",
        "subject": "Update available (Manual)",
        "severity": "info",
        "description": "A software update is available and must be triggered manually.",
    },
    "20": {
        "type": "ALERT",
        "subject": "Filter pressure too low",
        "severity": "critical",
        "description": (
            "The filter pump remains deactivated until the error is resolved."
        ),
    },
    "21": {
        "type": "ALERT",
        "subject": "Filter pressure too high",
        "severity": "critical",
        "description": (
            "The filter pump remains deactivated until the error is resolved."
        ),
    },
    "22": {
        "type": "WARNING",
        "subject": "Measuring water inflow missing",
        "severity": "warning",
        "description": "Inflow to the electrodes is too low or absent.",
    },
    "23": {
        "type": "WARNING",
        "subject": "Measuring water inflow too high",
        "severity": "warning",
        "description": "Inflow to the electrodes exceeds the limit.",
    },
    "24": {
        "type": "ALERT",
        "subject": "Circulation missing",
        "severity": "critical",
        "description": (
            "The filter pump has been deactivated until circulation is restored."
        ),
    },
    "25": {
        "type": "ALERT",
        "subject": "Circulation too high",
        "severity": "critical",
        "description": (
            "The filter pump has been deactivated until circulation normalizes."
        ),
    },
    "26": {
        "type": "ALERT",
        "subject": "Frost protection filter pump unavailable",
        "severity": "critical",
        "description": (
            "Temperature sensor error prevents the pump frost protection function."
        ),
    },
    "27": {
        "type": "ALERT",
        "subject": "Frost protection absorber unavailable",
        "severity": "critical",
        "description": (
            "Temperature sensor error prevents"
            " the absorber frost protection function."
        ),
    },
    "30": {
        "type": "WARNING",
        "subject": "Heat exchanger temperature high",
        "severity": "warning",
        "description": "The heat exchanger has exceeded the limit.",
    },
    "31": {
        "type": "ALERT",
        "subject": "Overheat protection unavailable",
        "severity": "critical",
        "description": "Temperature sensor error prevents overheat protection.",
    },
    "40": {
        "type": "WARNING",
        "subject": "Backwash skipped",
        "severity": "warning",
        "description": "The scheduled backwash could not be performed.",
    },
    "41": {
        "type": "MESSAGE",
        "subject": "Refill before backwash failed",
        "severity": "info",
        "description": "The minimum fill level was not reached in time.",
    },
    "42": {
        "type": "MESSAGE",
        "subject": "Refill not possible",
        "severity": "info",
        "description": "Refill valve is locked or manually switched off.",
    },
    "45": {
        "type": "ALERT",
        "subject": "Omnitronic no feedback (Backwash)",
        "severity": "critical",
        "description": "Actuator has not reached the backwash position.",
    },
    "46": {
        "type": "ALERT",
        "subject": "Omnitronic no feedback (Rinse)",
        "severity": "critical",
        "description": "Actuator has not reached the rinse position.",
    },
    "47": {
        "type": "ALERT",
        "subject": "Omni actuator position not reached",
        "severity": "critical",
        "description": "The actuator is not reporting position feedback.",
    },
    "49": {
        "type": "ALERT",
        "subject": "Omnitronic feedback contact open",
        "severity": "critical",
        "description": "Filter pump remains deactivated until the contact is closed.",
    },
    "50": {
        "type": "ALERT",
        "subject": "Water refill safety time exceeded",
        "severity": "critical",
        "description": "Float switch has not switched in time.",
    },
    "51": {
        "type": "ALERT",
        "subject": "Water refill upper float",
        "severity": "critical",
        "description": "Upper float switch has not responded.",
    },
    "52": {
        "type": "ALERT",
        "subject": "Water refill lower float",
        "severity": "critical",
        "description": "Lower float switch has not switched back.",
    },
    "60": {
        "type": "ALERT",
        "subject": "Overflow tank refill failed",
        "severity": "critical",
        "description": "Upper fill level could not be reached.",
    },
    "61": {
        "type": "WARNING",
        "subject": "Overflow tank dry run",
        "severity": "warning",
        "description": "Dry run protection of the filter pump triggered.",
    },
    "62": {
        "type": "WARNING",
        "subject": "Overflow tank level measurement faulty",
        "severity": "warning",
        "description": "Level probe is faulty or not connected.",
    },
    "71": {
        "type": "WARNING",
        "subject": "Temperature control program 1",
        "severity": "warning",
        "description": (
            "Switching program 1 of the temperature control has been triggered."
        ),
    },
    "72": {
        "type": "WARNING",
        "subject": "Temperature control program 2",
        "severity": "warning",
        "description": (
            "Switching program 2 of the temperature control has been triggered."
        ),
    },
    "73": {
        "type": "WARNING",
        "subject": "Temperature control program 3",
        "severity": "warning",
        "description": (
            "Switching program 3 of the temperature control has been triggered."
        ),
    },
    "74": {
        "type": "WARNING",
        "subject": "Temperature control program 4",
        "severity": "warning",
        "description": (
            "Switching program 4 of the temperature control has been triggered."
        ),
    },
    "75": {
        "type": "MESSAGE",
        "subject": "Temperature control program 5",
        "severity": "info",
        "description": (
            "Switching program 5 of the temperature control has been triggered."
        ),
    },
    "76": {
        "type": "WARNING",
        "subject": "Temperature control program 6",
        "severity": "warning",
        "description": (
            "Switching program 6 of the temperature control has been triggered."
        ),
    },
    "77": {
        "type": "WARNING",
        "subject": "Temperature control program 7",
        "severity": "warning",
        "description": (
            "Switching program 7 of the temperature control has been triggered."
        ),
    },
    "78": {
        "type": "WARNING",
        "subject": "Temperature control program 8",
        "severity": "warning",
        "description": (
            "Switching program 8 of the temperature control has been triggered."
        ),
    },
    "81": {
        "type": "WARNING",
        "subject": "Analog control program 1",
        "severity": "warning",
        "description": "Switching program 1 of the analog controls has been triggered.",
    },
    "82": {
        "type": "WARNING",
        "subject": "Analog control program 2",
        "severity": "warning",
        "description": "Switching program 2 of the analog controls has been triggered.",
    },
    "83": {
        "type": "WARNING",
        "subject": "Analog control program 3",
        "severity": "warning",
        "description": "Switching program 3 of the analog controls has been triggered.",
    },
    "84": {
        "type": "WARNING",
        "subject": "Analog control program 4",
        "severity": "warning",
        "description": "Switching program 4 of the analog controls has been triggered.",
    },
    "85": {
        "type": "WARNING",
        "subject": "Analog control program 5",
        "severity": "warning",
        "description": "Switching program 5 of the analog controls has been triggered.",
    },
    "86": {
        "type": "WARNING",
        "subject": "Analog control program 6",
        "severity": "warning",
        "description": "Switching program 6 of the analog controls has been triggered.",
    },
    "87": {
        "type": "WARNING",
        "subject": "Analog control program 7",
        "severity": "warning",
        "description": "Switching program 7 of the analog controls has been triggered.",
    },
    "88": {
        "type": "WARNING",
        "subject": "Analog control program 8",
        "severity": "warning",
        "description": "Switching program 8 of the analog controls has been triggered.",
    },
    "91": {
        "type": "WARNING",
        "subject": "Switching rule program 1",
        "severity": "warning",
        "description": "Switching program 1 of the switching rules has been triggered.",
    },
    "92": {
        "type": "WARNING",
        "subject": "Switching rule program 2",
        "severity": "warning",
        "description": "Switching program 2 of the switching rules has been triggered.",
    },
    "93": {
        "type": "WARNING",
        "subject": "Switching rule program 3",
        "severity": "warning",
        "description": "Switching program 3 of the switching rules has been triggered.",
    },
    "94": {
        "type": "WARNING",
        "subject": "Switching rule program 4",
        "severity": "warning",
        "description": "Switching program 4 of the switching rules has been triggered.",
    },
    "95": {
        "type": "WARNING",
        "subject": "Switching rule program 5",
        "severity": "warning",
        "description": "Switching program 5 of the switching rules has been triggered.",
    },
    "96": {
        "type": "WARNING",
        "subject": "Switching rule program 6",
        "severity": "warning",
        "description": "Switching program 6 of the switching rules has been triggered.",
    },
    "97": {
        "type": "WARNING",
        "subject": "Switching rule program 7",
        "severity": "warning",
        "description": "Switching program 7 of the switching rules has been triggered.",
    },
    "98": {
        "type": "WARNING",
        "subject": "Switching rule program 8",
        "severity": "warning",
        "description": "Switching program 8 of the switching rules has been triggered.",
    },
    "101": {
        "type": "WARNING",
        "subject": "Temperature sensor 1 error",
        "severity": "warning",
        "description": "Temperature sensor 1 is no longer detected.",
    },
    "102": {
        "type": "WARNING",
        "subject": "Temperature sensor 2 error",
        "severity": "warning",
        "description": "Temperature sensor 2 is no longer detected.",
    },
    "103": {
        "type": "WARNING",
        "subject": "Temperature sensor 3 error",
        "severity": "warning",
        "description": "Temperature sensor 3 is no longer detected.",
    },
    "104": {
        "type": "WARNING",
        "subject": "Temperature sensor 4 error",
        "severity": "warning",
        "description": "Temperature sensor 4 is no longer detected.",
    },
    "105": {
        "type": "WARNING",
        "subject": "Temperature sensor 5 error",
        "severity": "warning",
        "description": "Temperature sensor 5 is no longer detected.",
    },
    "106": {
        "type": "WARNING",
        "subject": "Temperature sensor 6 error",
        "severity": "warning",
        "description": "Temperature sensor 6 is no longer detected.",
    },
    "107": {
        "type": "WARNING",
        "subject": "Temperature sensor 7 error",
        "severity": "warning",
        "description": "Temperature sensor 7 is no longer detected.",
    },
    "108": {
        "type": "WARNING",
        "subject": "Temperature sensor 8 error",
        "severity": "warning",
        "description": "Temperature sensor 8 is no longer detected.",
    },
    "109": {
        "type": "WARNING",
        "subject": "Temperature sensor 9 error",
        "severity": "warning",
        "description": "Temperature sensor 9 is no longer detected.",
    },
    "110": {
        "type": "WARNING",
        "subject": "Temperature sensor 10 error",
        "severity": "warning",
        "description": "Temperature sensor 10 is no longer detected.",
    },
    "111": {
        "type": "WARNING",
        "subject": "Temperature sensor 11 error",
        "severity": "warning",
        "description": "Temperature sensor 11 is no longer detected.",
    },
    "112": {
        "type": "WARNING",
        "subject": "Temperature sensor 12 error",
        "severity": "warning",
        "description": "Temperature sensor 12 is no longer detected.",
    },
    "120": {
        "type": "WARNING",
        "subject": "Chlorine dosing ORP limit",
        "severity": "warning",
        "description": "ORP warning limit of chlorine dosing reached.",
    },
    "121": {
        "type": "WARNING",
        "subject": "Chlorine dosing chlorine limit",
        "severity": "warning",
        "description": "Chlorine warning limit of chlorine dosing reached.",
    },
    "122": {
        "type": "WARNING",
        "subject": "Chlorine dosing max. daily output",
        "severity": "warning",
        "description": "Daily dosing output exceeded.",
    },
    "123": {
        "type": "WARNING",
        "subject": "Chlorine canister low",
        "severity": "warning",
        "description": "Remaining contents of the chlorine canister is low.",
    },
    "124": {
        "type": "WARNING",
        "subject": "Chlorine canister empty",
        "severity": "warning",
        "description": "The chlorine canister is empty.",
    },
    "125": {
        "type": "WARNING",
        "subject": "Chlorine canister empty detector",
        "severity": "warning",
        "description": "Empty detection contact of the suction lance triggered.",
    },
    "130": {
        "type": "WARNING",
        "subject": "Electrolysis ORP limit",
        "severity": "warning",
        "description": "ORP warning limit of electrolysis reached.",
    },
    "131": {
        "type": "WARNING",
        "subject": "Electrolysis chlorine limit",
        "severity": "warning",
        "description": "Chlorine warning limit of electrolysis reached.",
    },
    "132": {
        "type": "WARNING",
        "subject": "Electrolysis max. daily production",
        "severity": "warning",
        "description": "Daily production output reached.",
    },
    "133": {
        "type": "WARNING",
        "subject": "Electrolysis remaining runtime",
        "severity": "warning",
        "description": "Remaining runtime warning of the electrolysis cell reached.",
    },
    "134": {
        "type": "WARNING",
        "subject": "Electrolysis max. operating time",
        "severity": "warning",
        "description": "Maximum total operating time of the electrolysis cell reached.",
    },
    "135": {
        "type": "WARNING",
        "subject": "Flow switch electrolysis",
        "severity": "warning",
        "description": "Flow switch of the electrolysis cell triggered.",
    },
    "142": {
        "type": "WARNING",
        "subject": "H2O2 max. daily dosing output",
        "severity": "warning",
        "description": "Maximum daily dosing output reached.",
    },
    "143": {
        "type": "WARNING",
        "subject": "H2O2 canister low",
        "severity": "warning",
        "description": "Remaining contents of the H2O2 canister is low.",
    },
    "144": {
        "type": "WARNING",
        "subject": "H2O2 canister empty",
        "severity": "warning",
        "description": "The H2O2 canister is empty.",
    },
    "145": {
        "type": "WARNING",
        "subject": "Oxygen canister empty detector",
        "severity": "warning",
        "description": "Empty detection contact of the suction lance triggered.",
    },
    "150": {
        "type": "WARNING",
        "subject": "pH-minus limit",
        "severity": "warning",
        "description": "Warning limits of pH-minus dosing reached.",
    },
    "152": {
        "type": "WARNING",
        "subject": "pH-minus max. daily dosing output",
        "severity": "warning",
        "description": "Daily dosing output exceeded.",
    },
    "153": {
        "type": "WARNING",
        "subject": "pH-minus canister low",
        "severity": "warning",
        "description": "Remaining contents of the pH-minus canister is low.",
    },
    "154": {
        "type": "WARNING",
        "subject": "pH-minus canister empty",
        "severity": "warning",
        "description": "The pH-minus canister is empty.",
    },
    "155": {
        "type": "WARNING",
        "subject": "pH-minus empty detection contact",
        "severity": "warning",
        "description": "Empty detection contact of the suction lance triggered.",
    },
    "160": {
        "type": "WARNING",
        "subject": "pH-plus limit",
        "severity": "warning",
        "description": "Warning limits of pH-plus dosing reached.",
    },
    "162": {
        "type": "WARNING",
        "subject": "pH-plus max. daily dosing output",
        "severity": "warning",
        "description": "Daily dosing output exceeded.",
    },
    "163": {
        "type": "WARNING",
        "subject": "pH-plus canister low",
        "severity": "warning",
        "description": "Remaining contents of the pH-plus canister is low.",
    },
    "164": {
        "type": "WARNING",
        "subject": "pH-plus canister empty",
        "severity": "warning",
        "description": "The pH-plus canister is empty.",
    },
    "165": {
        "type": "WARNING",
        "subject": "pH-plus empty detection contact",
        "severity": "warning",
        "description": "Empty detection contact of the suction lance triggered.",
    },
    "172": {
        "type": "WARNING",
        "subject": "Flocculant max. daily dosing output",
        "severity": "warning",
        "description": "Daily dosing output of flocculant dosing reached.",
    },
    "173": {
        "type": "WARNING",
        "subject": "Flocculant canister low",
        "severity": "warning",
        "description": "Remaining contents of the flocculant canister is low.",
    },
    "174": {
        "type": "WARNING",
        "subject": "Flocculant canister empty",
        "severity": "warning",
        "description": "The flocculant canister is empty.",
    },
    "175": {
        "type": "WARNING",
        "subject": "Flocculant empty detection contact",
        "severity": "warning",
        "description": "Empty detection contact of the suction lance triggered.",
    },
    "180": {
        "type": "REMINDER",
        "subject": "Calibrate pH electrode",
        "severity": "info",
        "description": "Calibration of the pH electrode is due.",
    },
    "181": {
        "type": "REMINDER",
        "subject": "Calibrate ORP electrode",
        "severity": "info",
        "description": "Calibration of the ORP electrode is due.",
    },
    "182": {
        "type": "REMINDER",
        "subject": "Calibrate chlorine electrode",
        "severity": "info",
        "description": "Calibration of the chlorine electrode is due.",
    },
    "200": {
        "type": "WARNING",
        "subject": "Dosing module disconnected",
        "severity": "warning",
        "description": "No communication link to the dosing module.",
    },
    "201": {
        "type": "WARNING",
        "subject": "Dosing module communication lost",
        "severity": "warning",
        "description": "Communication to the dosing module has been interrupted.",
    },
    "203": {
        "type": "WARNING",
        "subject": "Relay extension 1 disconnected",
        "severity": "warning",
        "description": "No communication link to relay extension 1.",
    },
    "204": {
        "type": "WARNING",
        "subject": "Relay extension 1 communication lost",
        "severity": "warning",
        "description": "Communication to relay extension 1 has been interrupted.",
    },
    "206": {
        "type": "WARNING",
        "subject": "Relay extension 2 disconnected",
        "severity": "warning",
        "description": "No communication link to relay extension 2.",
    },
    "207": {
        "type": "WARNING",
        "subject": "Relay extension 2 communication lost",
        "severity": "warning",
        "description": "Communication to relay extension 2 has been interrupted.",
    },
    "209": {
        "type": "ALERT",
        "subject": "Second dosing module detected",
        "severity": "critical",
        "description": "A second dosing module is being ignored.",
    },
    "210": {
        "type": "ALERT",
        "subject": "Incorrectly coded relay extension",
        "severity": "critical",
        "description": "A second relay extension has the same coding.",
    },
}


def get_error_info(code: str) -> dict[str, str]:
    """Return error information for a given code."""

    return ERROR_CODES.get(
        str(code).strip(),
        {
            "type": "UNKNOWN",
            "subject": f"Unknown code: {code}",
            "severity": "info",
            "description": "",
        },
    )
