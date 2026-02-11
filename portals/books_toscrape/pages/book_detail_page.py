from __future__ import annotations

from urllib.parse import urljoin

from playwright.async_api import Page

from config.logging_config import get_logger
from core.pages.base_page import BasePage
from portals.books_toscrape.models import BookDetail

log = get_logger(__name__)

RATING_MAP = {
    "One": "1",
    "Two": "2",
    "Three": "3",
    "Four": "4",
    "Five": "5",
}


class BookDetailPage(BasePage):
    portal_name = "books_toscrape"
    page_section = "detail"

    def _setup_locators(self) -> None:
        self._title_sel = self.selector("title")
        self._price_sel = self.selector("price")
        self._availability_sel = self.selector("availability")
        self._rating_sel = self.selector("rating")
        self._description_sel = self.selector("description")
        self._upc_sel = self.selector("upc")
        self._product_type_sel = self.selector("product_type")
        self._price_excl_tax_sel = self.selector("price_excl_tax")
        self._price_incl_tax_sel = self.selector("price_incl_tax")
        self._tax_sel = self.selector("tax")
        self._num_reviews_sel = self.selector("num_reviews")
        self._category_sel = self.selector("category")
        self._image_sel = self.selector("image")

    async def extract(self, url: str) -> BookDetail:
        """Navigate to a detail page and extract full book data."""
        await self.navigate(url)

        title = await self.get_text(self._title_sel)
        price = await self.get_text(self._price_sel)
        availability = await self.get_text(self._availability_sel)

        rating_classes = await self.get_attribute(self._rating_sel, "class")
        rating_word = rating_classes.replace("star-rating ", "").strip()
        rating = RATING_MAP.get(rating_word, "0")

        description = await self.get_text(self._description_sel, default="No description available.")
        upc = await self.get_text(self._upc_sel)
        product_type = await self.get_text(self._product_type_sel)
        price_excl_tax = await self.get_text(self._price_excl_tax_sel)
        price_incl_tax = await self.get_text(self._price_incl_tax_sel)
        tax = await self.get_text(self._tax_sel)
        num_reviews_str = await self.get_text(self._num_reviews_sel, default="0")
        category = await self.get_text(self._category_sel)

        img_src = await self.get_attribute(self._image_sel, "src")
        image_url = urljoin(url, img_src) if img_src else ""

        book = BookDetail(
            title=title,
            price=price,
            price_excl_tax=price_excl_tax,
            price_incl_tax=price_incl_tax,
            tax=tax,
            availability=availability,
            rating=rating,
            upc=upc,
            product_type=product_type,
            num_reviews=int(num_reviews_str),
            category=category,
            description=description,
            image_url=image_url,
        )
        log.info("detail_extracted", title=title)
        return book
