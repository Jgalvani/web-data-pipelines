from __future__ import annotations

from core.models.base import BaseDataModel


class BookSummary(BaseDataModel):
    """Summary data from the catalogue listing page."""

    title: str
    price: str
    rating: str
    availability: str
    detail_url: str


class BookDetail(BaseDataModel):
    """Full data from the book detail page."""

    title: str
    price: str
    price_excl_tax: str
    price_incl_tax: str
    tax: str
    availability: str
    rating: str
    upc: str
    product_type: str
    num_reviews: int
    category: str
    description: str
    image_url: str
