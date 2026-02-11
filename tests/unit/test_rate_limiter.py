from __future__ import annotations

import time
import pytest

from core.anti_detection.rate_limiter import TokenBucketRateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_allows_burst():
    limiter = TokenBucketRateLimiter(max_tokens=5, refill_period=10.0)
    start = time.monotonic()
    for _ in range(5):
        await limiter.acquire()
    elapsed = time.monotonic() - start
    # All 5 should be near-instant (initial tokens)
    assert elapsed < 1.0


@pytest.mark.asyncio
async def test_rate_limiter_throttles():
    limiter = TokenBucketRateLimiter(max_tokens=2, refill_period=2.0)
    # Consume initial tokens
    await limiter.acquire()
    await limiter.acquire()
    # Next acquire should wait for refill
    start = time.monotonic()
    await limiter.acquire()
    elapsed = time.monotonic() - start
    assert elapsed >= 0.9  # Should wait ~1s for refill (1 token per second)
