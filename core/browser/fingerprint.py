from __future__ import annotations

import random

FINGERPRINT_PROFILES = [
    {
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "viewport": {"width": 1920, "height": 1080},
        "locale": "en-US",
        "timezone_id": "America/New_York",
        "platform": "Win32",
    },
    {
        "user_agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "viewport": {"width": 1440, "height": 900},
        "locale": "en-US",
        "timezone_id": "America/Los_Angeles",
        "platform": "MacIntel",
    },
    {
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) "
            "Gecko/20100101 Firefox/125.0"
        ),
        "viewport": {"width": 1366, "height": 768},
        "locale": "en-US",
        "timezone_id": "America/Chicago",
        "platform": "Win32",
    },
    {
        "user_agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.4 Safari/605.1.15"
        ),
        "viewport": {"width": 1680, "height": 1050},
        "locale": "en-US",
        "timezone_id": "America/Denver",
        "platform": "MacIntel",
    },
]


def get_random_fingerprint() -> dict:
    return random.choice(FINGERPRINT_PROFILES)
