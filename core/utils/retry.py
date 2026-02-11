from __future__ import annotations

from typing import Any, Callable

from tenacity import retry, stop_after_attempt, wait_exponential

from config.logging_config import get_logger

log = get_logger(__name__)


def with_retry(
    attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 30,
) -> Callable:
    """Decorator factory: retry an async function with exponential backoff."""

    def decorator(func: Callable) -> Callable:
        @retry(
            stop=stop_after_attempt(attempts),
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            reraise=True,
        )
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception:
                log.warning("retry_attempt", function=func.__name__)
                raise

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator
