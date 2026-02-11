from __future__ import annotations

from playwright.async_api import Page
from playwright_stealth import Stealth

from config.logging_config import get_logger

log = get_logger(__name__)

_stealth = Stealth()


async def apply_stealth(page: Page) -> None:
    """Apply playwright-stealth patches to a page."""
    await _stealth.apply_stealth_async(page)
    log.debug("stealth_patches_applied")
