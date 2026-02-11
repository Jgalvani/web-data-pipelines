from __future__ import annotations

import asyncio
import random


async def human_delay(min_seconds: float = 0.5, max_seconds: float = 2.0) -> None:
    """Sleep for a random duration to mimic human behavior."""
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)


async def typing_delay(min_ms: int = 50, max_ms: int = 150) -> int:
    """Return a random per-keystroke delay in milliseconds."""
    return random.randint(min_ms, max_ms)
