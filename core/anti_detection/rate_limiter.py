from __future__ import annotations

import asyncio
import time


class TokenBucketRateLimiter:
    """Async token-bucket rate limiter."""

    def __init__(self, max_tokens: int, refill_period: float) -> None:
        self._max_tokens = max_tokens
        self._refill_period = refill_period
        self._tokens = float(max_tokens)
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        new_tokens = elapsed * (self._max_tokens / self._refill_period)
        self._tokens = min(self._max_tokens, self._tokens + new_tokens)
        self._last_refill = now

    async def acquire(self) -> None:
        """Wait until a token is available, then consume one."""
        while True:
            async with self._lock:
                self._refill()
                if self._tokens >= 1:
                    self._tokens -= 1
                    return
            # Wait a fraction of refill period before retrying
            await asyncio.sleep(self._refill_period / self._max_tokens)
