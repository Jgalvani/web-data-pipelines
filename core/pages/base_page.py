from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import yaml
from playwright.async_api import Locator, Page

from config.logging_config import get_logger
from config.settings import settings
from core.anti_detection.delays import human_delay
from core.utils.retry import with_retry

log = get_logger(__name__)


class BasePage(ABC):
    """Abstract base Page Object Model.

    Subclasses define `portal_name` and `page_section` to auto-load
    selectors from the portal YAML config.
    """

    portal_name: str  # e.g. "books_toscrape"
    page_section: str  # e.g. "catalogue" or "detail"

    def __init__(self, page: Page) -> None:
        self.page = page
        self._selectors: dict[str, str] = {}
        self._load_selectors()
        self._setup_locators()

    def _load_selectors(self) -> None:
        yaml_path = settings.portals_config_dir / f"{self.portal_name}.yaml"
        if not yaml_path.exists():
            raise FileNotFoundError(f"Portal config not found: {yaml_path}")
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        self._selectors = data.get("selectors", {}).get(self.page_section, {})

    @abstractmethod
    def _setup_locators(self) -> None:
        """Set up page-specific locators from self._selectors."""

    def selector(self, key: str) -> str:
        """Get a CSS selector by key."""
        return self._selectors[key]

    def locator(self, selector: str) -> Locator:
        return self.page.locator(selector)

    @with_retry(attempts=3, min_wait=1, max_wait=10)
    async def navigate(self, url: str, wait_until: str = "domcontentloaded") -> None:
        log.info("navigate", url=url)
        await self.page.goto(url, wait_until=wait_until)
        await human_delay(0.5, 1.5)

    async def safe_click(self, selector: str, **kwargs: Any) -> None:
        await human_delay(0.2, 0.8)
        await self.page.click(selector, **kwargs)

    async def safe_fill(self, selector: str, value: str, **kwargs: Any) -> None:
        await human_delay(0.2, 0.5)
        await self.page.fill(selector, value, **kwargs)

    async def get_text(
        self, selector: str, default: str = "", parent: Locator | None = None,
    ) -> str:
        root = parent or self.page
        el = root.locator(selector).first
        try:
            return (await el.inner_text()).strip()
        except Exception:
            return default

    async def get_attribute(
        self, selector: str, attr: str, default: str = "", parent: Locator | None = None,
    ) -> str:
        root = parent or self.page
        el = root.locator(selector).first
        try:
            val = await el.get_attribute(attr)
            return val.strip() if val else default
        except Exception:
            return default

    async def wait_for(self, selector: str, timeout: float = 10000) -> None:
        await self.page.wait_for_selector(selector, timeout=timeout)
