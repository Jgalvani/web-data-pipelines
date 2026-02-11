from __future__ import annotations

from urllib.parse import urljoin

from config.logging_config import get_logger
from core.pages.base_page import BasePage
from portals.books_toscrape.models import BookSummary

log = get_logger(__name__)

RATING_MAP = {
    "One": "1",
    "Two": "2",
    "Three": "3",
    "Four": "4",
    "Five": "5",
}


class CataloguePage(BasePage):
    portal_name = "books_toscrape"
    page_section = "catalogue"

    def _setup_locators(self) -> None:
        self._book_card_sel = self.selector("book_card")
        self._title_sel = self.selector("book_title")
        self._price_sel = self.selector("book_price")
        self._rating_sel = self.selector("book_rating")
        self._availability_sel = self.selector("book_availability")
        self._link_sel = self.selector("book_link")
        self._next_page_sel = self.selector("next_page")

    async def extract_books(self) -> list[BookSummary]:
        """Extract book summaries from current catalogue page."""
        cards = self.page.locator(self._book_card_sel)
        count = await cards.count()
        books: list[BookSummary] = []

        for i in range(count):
            card = cards.nth(i)

            title = (
                await self.get_attribute(self._title_sel, "title", parent=card)
                or await self.get_text(self._title_sel, parent=card)
            )

            price = await self.get_text(self._price_sel, parent=card)

            rating_classes = await self.get_attribute(self._rating_sel, "class", parent=card)
            rating_word = rating_classes.replace("star-rating ", "").strip()
            rating = RATING_MAP.get(rating_word, "0")

            availability = await self.get_text(self._availability_sel, default="Unknown", parent=card)

            href = await self.get_attribute(self._link_sel, "href", parent=card)
            detail_url = urljoin(self.page.url, href)

            books.append(
                BookSummary(
                    title=title,
                    price=price,
                    rating=rating,
                    availability=availability,
                    detail_url=detail_url,
                )
            )

        log.info("catalogue_extracted", count=len(books))
        return books

    async def has_next_page(self) -> bool:
        return await self.page.locator(self._next_page_sel).count() > 0

    async def go_next_page(self) -> None:
        href = await self.page.locator(self._next_page_sel).get_attribute("href")
        if href:
            next_url = urljoin(self.page.url, href)
            await self.navigate(next_url)
