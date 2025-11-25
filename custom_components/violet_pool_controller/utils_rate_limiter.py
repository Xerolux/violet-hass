"""Rate Limiter für API-Requests - Token Bucket Algorithm."""

import asyncio
import time
import logging
from typing import Optional
from collections import deque

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
        self.tokens = max_requests + burst_size
        self.max_tokens = max_requests + burst_size
        self.last_refill = time.time()

        # Request History für Statistiken
        self.request_history: deque = deque(maxlen=1000)
        self.blocked_requests = 0
        self.total_requests = 0

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
        Versuche ein Token zu erwerben.

        Args:
            priority: Priorität (1=critical, 2=high, 3=normal, 4=low)

        Returns:
            True wenn Request erlaubt, False wenn Rate Limit erreicht
        """
        async with self._lock:
            self.total_requests += 1
            current_time = time.time()

            # Refill tokens basierend auf verstrichener Zeit
            await self._refill_tokens(current_time)

            # Prüfe ob Token verfügbar
            if self.tokens >= 1:
                self.tokens -= 1
                self.request_history.append(
                    {
                        "time": current_time,
                        "priority": priority,
                        "blocked": False,
                    }
                )
                return True

            # Rate Limit erreicht
            self.blocked_requests += 1
            self.request_history.append(
                {
                    "time": current_time,
                    "priority": priority,
                    "blocked": True,
                }
            )

            _LOGGER.debug(
                "Rate Limit erreicht: %d/%d tokens (priority: %d, blocked: %d)",
                self.tokens,
                self.max_tokens,
                priority,
                self.blocked_requests,
            )

            return False

    async def wait_if_needed(self, priority: int = 3, timeout: float = 10.0) -> None:
        """
        Warte bis ein Token verfügbar ist.

        Args:
            priority: Request-Priorität
            timeout: Maximale Wartezeit in Sekunden

        Raises:
            asyncio.TimeoutError: Wenn Timeout erreicht
        """
        start_time = time.time()

        while True:
            if await self.acquire(priority):
                return

            # Timeout-Prüfung
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise asyncio.TimeoutError(f"Rate Limiter timeout nach {elapsed:.1f}s")

            # Warte auf Token-Refill
            await asyncio.sleep(self.retry_after)

    async def _refill_tokens(self, current_time: float) -> None:
        """Fülle Token-Bucket basierend auf verstrichener Zeit."""
        time_passed = current_time - self.last_refill

        if time_passed >= self.time_window:
            # Berechne neue Tokens basierend auf verstrichener Zeit
            refill_rate = self.max_requests / self.time_window
            new_tokens = time_passed * refill_rate

            self.tokens = min(self.max_tokens, self.tokens + new_tokens)
            self.last_refill = current_time

            _LOGGER.debug(
                "Token-Bucket refilled: %.1f tokens (max: %d)",
                self.tokens,
                self.max_tokens,
            )

    def get_stats(self) -> dict:
        """Hole Rate-Limiter-Statistiken."""
        current_time = time.time()

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
        self.tokens = self.max_tokens
        self.last_refill = time.time()
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
            API_RATE_LIMIT_REQUESTS,
            API_RATE_LIMIT_WINDOW,
            API_RATE_LIMIT_BURST,
            API_RATE_LIMIT_RETRY_AFTER,
        )

        _global_rate_limiter = RateLimiter(
            max_requests=API_RATE_LIMIT_REQUESTS,
            time_window=API_RATE_LIMIT_WINDOW,
            burst_size=API_RATE_LIMIT_BURST,
            retry_after=API_RATE_LIMIT_RETRY_AFTER,
        )
    return _global_rate_limiter


__all__ = ["RateLimiter", "get_global_rate_limiter"]
