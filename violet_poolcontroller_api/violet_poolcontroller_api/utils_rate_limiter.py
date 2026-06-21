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

"""Rate Limiter für API-Requests - Token Bucket Algorithm."""

from __future__ import annotations

import asyncio
import logging
import time
from collections import deque

_LOGGER = logging.getLogger(__name__)

_STATS_WINDOW_SECONDS = 60


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
            max_requests: Maximale Anzahl Requests pro Zeitfenster
            time_window: Zeitfenster in Sekunden
            burst_size: Erlaubte Burst-Größe (zusätzliche Requests)
            retry_after: Wartezeit in Sekunden bei Limit-Überschreitung

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
        self.request_history: deque = deque(maxlen=500)
        self.blocked_requests = 0
        self.total_requests = 0
        self._last_known_tokens = 0.0
        self.history_cleanup_interval = 300  # 5 minutes
        self.last_cleanup_time = time.monotonic()

        # Memory-efficient statistics
        self._recent_stats = {
            "requests_last_minute": 0,
            "blocked_last_minute": 0,
            "last_minute_reset": time.monotonic(),
        }

        # Lock für Thread-Safety
        self._lock = asyncio.Lock()

        _LOGGER.debug(
            "Rate Limiter initialisiert: %d req/%ss (burst: %d)",
            max_requests,
            time_window,
            burst_size,
        )

    async def acquire(self, priority: int = 3) -> bool:
        """Acquire a token from the rate limiter.

        Args:
            priority: Priority level (0=highest, 3=lowest)

        Returns:
            True if token acquired, False otherwise

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

            # Refill tokens
            self._refill_tokens(current_time)

            if self.tokens >= 1:
                self.tokens -= 1

                # Store minimal data for efficiency
                self.request_history.append(
                    {"time": current_time, "priority": priority, "blocked": False},
                )

                return True

            # Track failures efficiently
            self.blocked_requests += 1
            self._recent_stats["blocked_last_minute"] += 1
            self._last_known_tokens = self.tokens
            return False

    def _cleanup_history(self, current_time: float) -> None:
        """Clean up old history entries to prevent memory leaks."""
        # Remove entries older than 1 hour
        cutoff_time = current_time - 3600

        while self.request_history and self.request_history[0]["time"] <= cutoff_time:
            self.request_history.popleft()

        _LOGGER.debug("Rate limiter history cleanup completed")

    def _update_recent_stats(self, current_time: float) -> None:
        """Update memory-efficient recent statistics."""
        # Reset minute stats every _STATS_WINDOW_SECONDS
        if current_time - self._recent_stats["last_minute_reset"] > _STATS_WINDOW_SECONDS:
            self._recent_stats["requests_last_minute"] = 0
            self._recent_stats["blocked_last_minute"] = 0
            self._recent_stats["last_minute_reset"] = current_time

        self._recent_stats["requests_last_minute"] += 1

    async def wait_if_needed(self, priority: int = 3, timeout: float = 10.0) -> None:  # noqa: ASYNC109
        """Warte bis ein Token verfügbar ist.

        Args:
            priority: Request-Priorität
            timeout: Maximale Wartezeit in Sekunden

        Raises:
            TimeoutError: Wenn Timeout erreicht

        """
        start_time = time.monotonic()

        while True:
            if await self.acquire(priority):
                return

            # Timeout-Prüfung
            elapsed = time.monotonic() - start_time
            if elapsed >= timeout:
                msg = f"Rate Limiter timeout nach {elapsed:.1f}s"
                raise TimeoutError(msg)

            refill_rate = self.max_requests / self.time_window
            needed_tokens = 1.0 - self._last_known_tokens
            if refill_rate > 0:
                optimal_wait = needed_tokens / refill_rate
                wait_time = min(optimal_wait, self.retry_after)
            else:
                wait_time = self.retry_after

            await asyncio.sleep(wait_time)

    def _refill_tokens(self, current_time: float) -> None:
        """Fülle Token-Bucket basierend auf verstrichener Zeit."""
        time_passed = current_time - self.last_refill

        # Refill proportional to time passed, not just when full window elapsed
        if time_passed > 0:
            # Berechne neue Tokens basierend auf verstrichener Zeit
            refill_rate = self.max_requests / self.time_window
            new_tokens = time_passed * refill_rate

            self.tokens = min(self.max_tokens, self.tokens + new_tokens)
            self.last_refill = current_time

    def get_stats(self) -> dict:
        """Hole Rate-Limiter-Statistiken."""
        current_time = time.monotonic()
        self._update_recent_stats(current_time)

        return {
            "total_requests": self.total_requests,
            "blocked_requests": self.blocked_requests,
            "recent_requests_1min": self._recent_stats["requests_last_minute"],
            "recent_blocked_1min": self._recent_stats["blocked_last_minute"],
            "current_tokens": self.tokens,
            "max_tokens": self.max_tokens,
            "block_rate": (
                self.blocked_requests / self.total_requests * 100 if self.total_requests > 0 else 0
            ),
        }

    def reset(self) -> None:
        """Setze Rate Limiter zurück."""
        self.tokens = float(self.max_tokens)
        self.last_refill = time.monotonic()
        self.blocked_requests = 0
        self.total_requests = 0
        self.request_history.clear()
        self._recent_stats["requests_last_minute"] = 0
        self._recent_stats["blocked_last_minute"] = 0
        _LOGGER.debug("Rate Limiter zurückgesetzt")


# Global Rate Limiter-Instanz (kann pro API-Instanz auch separat erstellt werden)
_global_rate_limiter: RateLimiter | None = None


def get_global_rate_limiter() -> RateLimiter:
    """Hole oder erstelle globalen Rate Limiter."""
    global _global_rate_limiter  # noqa: PLW0603
    if _global_rate_limiter is None:
        # Default-Werte aus const_api
        from .const_api import (  # noqa: PLC0415
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
