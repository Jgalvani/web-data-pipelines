from __future__ import annotations

import time

import pytest

from core.anti_detection.delays import human_delay, typing_delay


@pytest.mark.asyncio
async def test_human_delay_within_range():
    start = time.monotonic()
    await human_delay(0.1, 0.3)
    elapsed = time.monotonic() - start
    assert 0.09 <= elapsed <= 0.5


@pytest.mark.asyncio
async def test_typing_delay_returns_int():
    delay = await typing_delay(10, 100)
    assert isinstance(delay, int)
    assert 10 <= delay <= 100
