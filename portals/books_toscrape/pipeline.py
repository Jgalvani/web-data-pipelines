from __future__ import annotations

from typing import Any

import yaml

from config.logging_config import get_logger
from config.settings import settings
from core.anti_detection.delays import human_delay
from core.anti_detection.session_manager import SessionManager
from core.pipelines.base_pipeline import BasePipeline
from portals.books_toscrape.models import BookDetail
from portals.books_toscrape.pages.book_detail_page import BookDetailPage
from portals.books_toscrape.pages.catalogue_page import CataloguePage

log = get_logger(__name__)


class BooksToscrapePipeline(BasePipeline):
    portal_name = "books_toscrape"

    def __init__(self, **kwargs: Any) -> None:
        yaml_path = settings.portals_config_dir / "books_toscrape.yaml"
        with open(yaml_path) as f:
            portal_config = yaml.safe_load(f)

        rate_cfg = portal_config.get("rate_limit", {})
        rpm = rate_cfg.get("requests_per_minute", 20)

        self._delay_min = rate_cfg.get("delay_min", 1.0)
        self._delay_max = rate_cfg.get("delay_max", 3.0)
        self._base_url: str = portal_config["portal"]["base_url"]
        self._pagination_max = portal_config.get("pagination", {}).get("max_pages", 50)

        super().__init__(
            rate_limit_requests=rpm,
            rate_limit_period=60,
            **kwargs,
        )

    async def setup_pages(self, page: Any) -> None:
        self._catalogue = CataloguePage(page)
        self._detail = BookDetailPage(page)

    async def collect(self, session: SessionManager, browser: Any) -> list[BookDetail]:
        catalogue_url = f"{self._base_url}/catalogue/page-1.html"
        await self._catalogue.navigate(catalogue_url)

        all_books: list[BookDetail] = []
        page_num = 0
        max_pages = self._max_pages or self._pagination_max # Use the CLI value if provided, otherwise fall back to the YAML default. 

        while True:
            page_num += 1
            log.info("collecting_page", page=page_num)

            summaries = await self._catalogue.extract_books()

            for summary in summaries:
                await self.rate_limit()
                await human_delay(self._delay_min, self._delay_max)

                # Refresh session if expired (get a new page with fresh fingerprint)
                current_page = await session.get_page(browser)
                if current_page is not self._detail.page:
                    self._detail = BookDetailPage(current_page)
                    self._catalogue = CataloguePage(current_page)

                try:
                    detail = await self._detail.extract(summary.detail_url)
                    all_books.append(detail)
                except Exception as exc:
                    log.error("detail_extraction_error", url=summary.detail_url, error=str(exc))

            if page_num >= max_pages:
                log.info("max_pages_reached", max_pages=max_pages)
                break

            if not await self._catalogue.has_next_page():
                log.info("no_more_pages")
                break

            # Navigate back to catalogue for next page
            await self._catalogue.navigate(
                f"{self._base_url}/catalogue/page-{page_num + 1}.html"
            )
            await human_delay(self._delay_min, self._delay_max)

        log.info("collection_complete", total=len(all_books))
        return all_books
