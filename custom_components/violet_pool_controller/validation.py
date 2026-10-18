"""Use Home Assistant's schema engine with matching static types.

HA 2026.9+ aliases voluptuous at runtime, which static checkers cannot see.
Older supported HA releases still use voluptuous.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import probatio as vol
else:
    try:
        import probatio as vol
    except ImportError:
        import voluptuous as vol

__all__ = ["vol"]
