from __future__ import annotations

from typing import AsyncIterator

from contextlib import asynccontextmanager

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from config.logging_config import get_logger
from config.settings import settings
from core.anti_detection.stealth import apply_stealth
from core.browser.fingerprint import get_random_fingerprint
from core.browser.headers import build_headers
from core.browser.proxy import ProxyRotator

log = get_logger(__name__)


class BrowserManager:
    """Manages browser lifecycle with stealth and fingerprint rotation."""

    def __init__(self, headless: bool | None = None) -> None:
        self._headless = headless if headless is not None else settings.headless
        self._proxy_rotator = ProxyRotator(
            proxies=settings.proxy_list,
            strategy=settings.proxy_strategy,
        )

    @asynccontextmanager
    async def launch(self) -> AsyncIterator[Browser]:
        async with async_playwright() as pw:
            launcher = getattr(pw, settings.browser_type)
            launch_kwargs: dict = {
                "headless": self._headless,
                "slow_mo": settings.slow_mo,
            }
            proxy = self._proxy_rotator.get_next()
            if proxy:
                launch_kwargs["proxy"] = proxy
                log.info("using_proxy", server=proxy["server"])

            browser = await launcher.launch(**launch_kwargs)
            log.info("browser_launched", browser_type=settings.browser_type, headless=self._headless)
            try:
                yield browser
            finally:
                await browser.close()
                log.info("browser_closed")

    async def new_context(self, browser: Browser) -> BrowserContext:
        fp = get_random_fingerprint()
        extra_headers = build_headers(fp["user_agent"])

        context = await browser.new_context(
            user_agent=fp["user_agent"],
            viewport=fp["viewport"],
            locale=fp["locale"],
            timezone_id=fp["timezone_id"],
            extra_http_headers=extra_headers,
        )
        log.info("context_created", user_agent=fp["user_agent"][:50] + "...")
        return context

    async def new_stealth_page(self, context: BrowserContext) -> Page:
        page = await context.new_page()
        await apply_stealth(page)
        log.info("stealth_page_created")
        return page
