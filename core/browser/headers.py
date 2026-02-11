from __future__ import annotations


def build_headers(user_agent: str) -> dict[str, str]:
    """Build realistic HTTP headers that match the given User-Agent."""
    is_chrome = "Chrome" in user_agent and "Safari" in user_agent and "Firefox" not in user_agent
    is_firefox = "Firefox" in user_agent

    headers: dict[str, str] = {
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    if is_chrome:
        headers["Sec-CH-UA"] = '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"'
        headers["Sec-CH-UA-Mobile"] = "?0"
        headers["Sec-CH-UA-Platform"] = '"Windows"' if "Windows" in user_agent else '"macOS"'
        headers["Sec-Fetch-Dest"] = "document"
        headers["Sec-Fetch-Mode"] = "navigate"
        headers["Sec-Fetch-Site"] = "none"
        headers["Sec-Fetch-User"] = "?1"
    elif is_firefox:
        headers["Sec-Fetch-Dest"] = "document"
        headers["Sec-Fetch-Mode"] = "navigate"
        headers["Sec-Fetch-Site"] = "none"
        headers["Sec-Fetch-User"] = "?1"

    return headers
