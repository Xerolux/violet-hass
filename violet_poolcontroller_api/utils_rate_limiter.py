# violet-poolController-api - API für Violet Pool Controller
# Copyright (C) 2024–2026  Xerolux
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

"""Rate Limiter für API-Requests — Token Bucket Algorithm."""

from __future__ import annotations

import asyncio
import logging
import time
from collections import deque

_LOGGER = logging.getLogger(__name__)


class RateLimiter:
    """Rate Limiter mit Token Bucket Algorithm.

    Verhindert API-Overload durch:
    - Maximale Requests pro Zeitfenster
    - Burst-Support für kurzzeitige Spitzen
    - Priority Queue für kritische Requests
    - Graceful Degradation bei Limit-Überschreitung
    """

    def __init__(
        self,
        max_requests: int = 10,
        time_window: float = 1.0,
        burst_size: int = 3,
        retry_after: float = 0.1,
    ) -> None:
        """Initialisiere den Rate Limiter.

        Args:
            max_requests: Maximale Anzahl Requests pro Zeitfenster.
            time_window: Zeitfenster in Sekunden.
            burst_size: Erlaubte Burst-Größe (zusätzliche Requests).
            retry_after: Wartezeit in Sekunden bei Limit-Überschreitung.
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.burst_size = burst_size
        self.retry_after = retry_after

        # Token Bucket
        self.tokens = float(max_requests + burst_size)
        self.max_tokens = max_requests + burst_size
        self.last_refill = time.monotonic()

        # Optimized request history with size and time limits
        self.request_history: deque[dict] = deque(maxlen=500)
        self.blocked_requests = 0
        self.total_requests = 0
        self.history_cleanup_interval = 300  # 5 minutes
        self.last_cleanup_time = time.monotonic()

        # Memory-efficient statistics
        self._recent_stats: dict[str, float | int] = {
            "requests_last_minute": 0,
            "blocked_last_minute": 0,
            "last_minute_reset": time.monotonic(),
        }

        # Lock für Thread-Safety (asyncio coroutines)
        self._lock = asyncio.Lock()

        _LOGGER.debug(
            "Rate Limiter initialisiert: %d req/%.1fs (burst: %d)",
            max_requests,
            time_window,
            burst_size,
        )

    async def acquire(self, priority: int = 3) -> bool:
        """Acquire a token from the rate limiter.

        Args:
            priority: Priority level (1=highest, 4=lowest).

        Returns:
            True if token acquired, False otherwise.
        """
        async with self._lock:
            current_time = time.monotonic()
            self.total_requests += 1

            # Periodic cleanup to prevent memory growth
            if current_time - self.last_cleanup_time > self.history_cleanup_interval:
                self._cleanup_history(current_time)
                self.last_cleanup_time = current_time

            # Update recent statistics
            self._update_recent_stats(current_time)

            # Refill tokens based on elapsed time
            self._refill_tokens(current_time)

            if self.tokens >= 1:
                self.tokens -= 1
                self.request_history.append(
                    {"time": current_time, "priority": priority, "blocked": False}
                )
                return True

            # Token exhausted
            self.blocked_requests += 1
            self._recent_stats["blocked_last_minute"] = (
                int(self._recent_stats["blocked_last_minute"]) + 1
            )
            self.request_history.append(
                {"time": current_time, "priority": priority, "blocked": True}
            )
            return False

    def _cleanup_history(self, current_time: float) -> None:
        """Clean up old history entries to prevent memory leaks."""
        cutoff_time = current_time - 3600  # keep last hour
        while self.request_history and self.request_history[0]["time"] <= cutoff_time:
            self.request_history.popleft()
        _LOGGER.debug("Rate limiter history cleanup completed")

    def _update_recent_stats(self, current_time: float) -> None:
        """Update memory-efficient recent statistics."""
        if current_time - float(self._recent_stats["last_minute_reset"]) > 60:
            self._recent_stats["requests_last_minute"] = 0
            self._recent_stats["blocked_last_minute"] = 0
            self._recent_stats["last_minute_reset"] = current_time
        self._recent_stats["requests_last_minute"] = (
            int(self._recent_stats["requests_last_minute"]) + 1
        )

    async def wait_if_needed(self, priority: int = 3, timeout: float = 10.0) -> None:
        """Warte bis ein Token verfügbar ist.

        Args:
            priority: Request-Priorität (1=highest, 4=lowest).
            timeout: Maximale Wartezeit in Sekunden.

        Raises:
            asyncio.TimeoutError: Wenn Timeout erreicht wird.
        """
        start_time = time.monotonic()

        while True:
            if await self.acquire(priority):
                return

            elapsed = time.monotonic() - start_time
            if elapsed >= timeout:
                raise asyncio.TimeoutError(
                    f"Rate Limiter timeout after {elapsed:.1f}s"
                )

            await asyncio.sleep(self.retry_after)

    def _refill_tokens(self, current_time: float) -> None:
        """Fülle Token-Bucket basierend auf verstrichener Zeit."""
        time_passed = current_time - self.last_refill
        if time_passed > 0:
            refill_rate = self.max_requests / self.time_window
            new_tokens = time_passed * refill_rate
            self.tokens = min(self.max_tokens, self.tokens + new_tokens)
            self.last_refill = current_time

    def get_stats(self) -> dict[str, object]:
        """Hole Rate-Limiter-Statistiken."""
        current_time = time.monotonic()
        recent_requests = [
            r for r in self.request_history if current_time - r["time"] <= 60
        ]
        recent_blocked = sum(1 for r in recent_requests if r["blocked"])

        return {
            "total_requests": self.total_requests,
            "blocked_requests": self.blocked_requests,
            "recent_requests_1min": len(recent_requests),
            "recent_blocked_1min": recent_blocked,
            "current_tokens": self.tokens,
            "max_tokens": self.max_tokens,
            "block_rate": (
                self.blocked_requests / self.total_requests * 100
                if self.total_requests > 0
                else 0.0
            ),
        }

    def reset(self) -> None:
        """Setze Rate Limiter zurück."""
        self.tokens = float(self.max_tokens)
        self.last_refill = time.monotonic()
        self.blocked_requests = 0
        self.total_requests = 0
        self.request_history.clear()
        _LOGGER.debug("Rate Limiter zurückgesetzt")


# ---------------------------------------------------------------------------
# Legacy global singleton — kept for backward compatibility with any external
# code that calls get_global_rate_limiter().
# The VioletPoolAPI class now creates a per-instance RateLimiter so that
# multiple API instances (multiple controllers) each get their own budget.
# ---------------------------------------------------------------------------

_global_rate_limiter: RateLimiter | None = None


def get_global_rate_limiter() -> RateLimiter:
    """Return (or create) the module-level global rate limiter.

    .. deprecated::
        Prefer creating a ``RateLimiter`` per ``VioletPoolAPI`` instance so
        that multiple controllers do not share the same token budget.
    """
    global _global_rate_limiter
    if _global_rate_limiter is None:
        from .const_api import (
            API_RATE_LIMIT_BURST,
            API_RATE_LIMIT_REQUESTS,
            API_RATE_LIMIT_RETRY_AFTER,
            API_RATE_LIMIT_WINDOW,
        )

        _global_rate_limiter = RateLimiter(
            max_requests=API_RATE_LIMIT_REQUESTS,
            time_window=API_RATE_LIMIT_WINDOW,
            burst_size=API_RATE_LIMIT_BURST,
            retry_after=API_RATE_LIMIT_RETRY_AFTER,
        )
    return _global_rate_limiter


__all__ = ["RateLimiter", "get_global_rate_limiter"]
