from __future__ import annotations

import time

from playwright.async_api import BrowserContext, Page

from config.logging_config import get_logger
from core.browser.context_manager import BrowserManager

log = get_logger(__name__)

DEFAULT_SESSION_TIMEOUT = 1800  # 30 minutes


class SessionManager:
    """Track session age and refresh context when it goes stale."""

    def __init__(
        self,
        browser_manager: BrowserManager,
        timeout: float = DEFAULT_SESSION_TIMEOUT,
    ) -> None:
        self._browser_manager = browser_manager
        self._timeout = timeout
        self._session_start = time.monotonic()
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    @property
    def is_expired(self) -> bool:
        return (time.monotonic() - self._session_start) > self._timeout

    async def get_page(self, browser) -> Page:
        """Return the current page, refreshing the session if expired."""
        if self._page is None or self.is_expired:
            await self.refresh(browser)
        return self._page  # type: ignore[return-value]

    async def refresh(self, browser) -> None:
        """Close old context and create a fresh one with new fingerprint."""
        log.info("session_refresh", reason="expired" if self.is_expired else "initial")
        if self._context:
            await self._context.close()
        self._context = await self._browser_manager.new_context(browser)
        self._page = await self._browser_manager.new_stealth_page(self._context)
        self._session_start = time.monotonic()

    async def close(self) -> None:
        if self._context:
            await self._context.close()
            self._context = None
            self._page = None
