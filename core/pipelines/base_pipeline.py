from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from config.logging_config import get_logger
from core.anti_detection.rate_limiter import TokenBucketRateLimiter
from core.anti_detection.session_manager import SessionManager
from core.browser.context_manager import BrowserManager
from core.export.base_exporter import BaseExporter
from core.export.json_exporter import JsonExporter
from core.models.run_metadata import RunMetadata

log = get_logger(__name__)


class BasePipeline(ABC):
    """Template-method pipeline: run() → setup_pages → collect → transform → export."""

    portal_name: str

    def __init__(
        self,
        headless: bool | None = None,
        exporters: list[BaseExporter] | None = None,
        max_pages: int | None = None,
        rate_limit_requests: int = 10,
        rate_limit_period: float = 60,
    ) -> None:
        self._browser_manager = BrowserManager(headless=headless)
        self._exporters = exporters or [JsonExporter()]
        self._max_pages = max_pages
        self._rate_limiter = TokenBucketRateLimiter(rate_limit_requests, rate_limit_period)

    async def run(self) -> RunMetadata:
        """Execute the full pipeline."""
        metadata = RunMetadata(portal=self.portal_name)
        log.info("pipeline_start", portal=self.portal_name)

        errors = 0
        collected: list[BaseModel] = []

        try:
            async with self._browser_manager.launch() as browser:
                session = SessionManager(self._browser_manager)
                page = await session.get_page(browser)

                await self.setup_pages(page)

                raw_data = await self.collect(session, browser)
                collected = self.transform(raw_data)

                await session.close()

        except Exception as exc:
            log.error("pipeline_error", error=str(exc))
            errors += 1

        metadata.finish(items=len(collected), errors=errors)

        for exporter in self._exporters:
            try:
                await exporter.export(collected, metadata)
            except Exception as exc:
                log.error("export_error", exporter=type(exporter).__name__, error=str(exc))
                metadata.add_errors(1)

        log.info(
            "pipeline_complete",
            portal=self.portal_name,
            items=metadata.items_collected,
            duration=metadata.duration_seconds,
            status=metadata.status,
        )
        return metadata

    @abstractmethod
    async def setup_pages(self, page: Any) -> None:
        """Initialize page objects from the Playwright page."""

    @abstractmethod
    async def collect(self, session: SessionManager, browser: Any) -> list[Any]:
        """Collect raw data from the portal. Returns list of raw items."""

    def transform(self, raw_data: list[Any]) -> list[BaseModel]:
        """Optional transform step. Default: return as-is (assumes Pydantic models)."""
        return raw_data

    async def rate_limit(self) -> None:
        """Wait for rate limiter token."""
        await self._rate_limiter.acquire()
