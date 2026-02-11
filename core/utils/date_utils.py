from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Iterator


def date_range(start: date, end: date) -> Iterator[date]:
    """Yield each date from start to end (inclusive)."""
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def format_date(d: date | datetime, fmt: str = "%Y-%m-%d") -> str:
    """Format a date/datetime to a string."""
    return d.strftime(fmt)


def parse_date(s: str, fmt: str = "%Y-%m-%d") -> date:
    """Parse a date string into a date object."""
    return datetime.strptime(s, fmt).date()
