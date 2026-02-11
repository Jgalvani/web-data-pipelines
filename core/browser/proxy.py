from __future__ import annotations

import random
from urllib.parse import urlparse

from config.logging_config import get_logger

log = get_logger(__name__)


class ProxyRotator:
    """Rotate through a list of proxies using configurable strategy."""

    def __init__(self, proxies: list[str], strategy: str = "round_robin") -> None:
        self._proxies = proxies
        self._strategy = strategy
        self._index = 0

    @property
    def has_proxies(self) -> bool:
        return len(self._proxies) > 0

    def get_next(self) -> dict | None:
        if not self._proxies:
            return None

        if self._strategy == "random":
            proxy_url = random.choice(self._proxies)
        elif self._strategy == "sticky":
            proxy_url = self._proxies[0]
        else:  # round_robin
            proxy_url = self._proxies[self._index % len(self._proxies)]
            self._index += 1

        return self._parse_proxy_url(proxy_url)

    @staticmethod
    def _parse_proxy_url(proxy_url: str) -> dict:
        parsed = urlparse(proxy_url)
        result: dict = {"server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"}
        if parsed.username:
            result["username"] = parsed.username
        if parsed.password:
            result["password"] = parsed.password
        return result
