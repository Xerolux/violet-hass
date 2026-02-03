"""Rate Limiter für API-Requests - Token Bucket Algorithm."""

import asyncio
import logging
import time
from collections import deque
from typing import Optional

_LOGGER = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate Limiter mit Token Bucket Algorithm.

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
        """
        Initialisiere den Rate Limiter.

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
        self.request_history: deque = deque(maxlen=500)  # Reduced from 1000
        self.blocked_requests = 0
        self.total_requests = 0
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
        """
        Acquire a token from the rate limiter.

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
                await self._cleanup_history(current_time)
                self.last_cleanup_time = current_time

            # Update recent statistics
            self._update_recent_stats(current_time)

            # Refill tokens
            await self._refill_tokens(current_time)

            if self.tokens >= 1:
                self.tokens -= 1

                # Store minimal data for efficiency
                self.request_history.append(
                    {"time": current_time, "priority": priority, "blocked": False}
                )

                return True

            # Track failures efficiently
            self.blocked_requests += 1
            self._recent_stats["blocked_last_minute"] += 1
            return False

    async def _cleanup_history(self, current_time: float) -> None:
        """Clean up old history entries to prevent memory leaks."""
        # Remove entries older than 1 hour
        cutoff_time = current_time - 3600

        # Filter while maintaining order
        filtered_history = deque(
            (entry for entry in self.request_history if entry["time"] > cutoff_time),
            maxlen=500,
        )

        self.request_history = filtered_history
        _LOGGER.debug("Rate limiter history cleanup completed")

    def _update_recent_stats(self, current_time: float) -> None:
        """Update memory-efficient recent statistics."""
        # Reset minute stats every 60 seconds
        if current_time - self._recent_stats["last_minute_reset"] > 60:
            self._recent_stats["requests_last_minute"] = 0
            self._recent_stats["blocked_last_minute"] = 0
            self._recent_stats["last_minute_reset"] = current_time

        self._recent_stats["requests_last_minute"] += 1

    async def wait_if_needed(self, priority: int = 3, timeout: float = 10.0) -> None:
        """
        Warte bis ein Token verfügbar ist.

        Args:
            priority: Request-Priorität
            timeout: Maximale Wartezeit in Sekunden

        Raises:
            asyncio.TimeoutError: Wenn Timeout erreicht
        """
        start_time = time.monotonic()

        while True:
            if await self.acquire(priority):
                return

            # Timeout-Prüfung
            elapsed = time.monotonic() - start_time
            if elapsed >= timeout:
                raise asyncio.TimeoutError(f"Rate Limiter timeout nach {elapsed:.1f}s")

            # Warte auf Token-Refill
            await asyncio.sleep(self.retry_after)

    async def _refill_tokens(self, current_time: float) -> None:
        """Fülle Token-Bucket basierend auf verstrichener Zeit."""
        time_passed = current_time - self.last_refill

        # Refill proportional to time passed, not just when full window elapsed
        if time_passed > 0:
            # Berechne neue Tokens basierend auf verstrichener Zeit
            refill_rate = self.max_requests / self.time_window
            new_tokens = time_passed * refill_rate

            self.tokens = min(self.max_tokens, self.tokens + new_tokens)
            self.last_refill = current_time

            _LOGGER.debug(
                "Token-Bucket refilled: %.1f tokens (max: %d, time_passed: %.2fs)",
                self.tokens,
                self.max_tokens,
                time_passed,
            )

    def get_stats(self) -> dict:
        """Hole Rate-Limiter-Statistiken."""
        current_time = time.monotonic()

        # Berechne Requests in letzter Minute
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
                else 0
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


# Global Rate Limiter-Instanz (kann pro API-Instanz auch separat erstellt werden)
_global_rate_limiter: Optional[RateLimiter] = None


def get_global_rate_limiter() -> RateLimiter:
    """Hole oder erstelle globalen Rate Limiter."""
    global _global_rate_limiter
    if _global_rate_limiter is None:
        # Default-Werte aus const_api
        from .const import (
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
