from __future__ import annotations

from datetime import datetime, timezone

from core.models.base import BaseDataModel
from core.models.run_metadata import RunMetadata
from portals.books_toscrape.models import BookDetail, BookSummary


class TestBaseDataModel:
    def test_collected_at_auto_populated(self):
        class Sample(BaseDataModel):
            name: str

        item = Sample(name="test")
        assert item.collected_at is not None
        assert item.collected_at.tzinfo is not None

    def test_collected_at_is_utc(self):
        class Sample(BaseDataModel):
            name: str

        item = Sample(name="test")
        assert item.collected_at.tzinfo == timezone.utc


class TestRunMetadata:
    def test_initial_status(self):
        meta = RunMetadata(portal="test")
        assert meta.status == "running"
        assert meta.items_collected == 0

    def test_finish_sets_fields(self):
        meta = RunMetadata(portal="test")
        meta.finish(items=42, errors=0)
        assert meta.status == "completed"
        assert meta.items_collected == 42
        assert meta.errors == 0
        assert meta.finished_at is not None
        assert meta.duration_seconds is not None
        assert meta.duration_seconds >= 0

    def test_finish_completed_with_errors(self):
        meta = RunMetadata(portal="test")
        meta.finish(items=42, errors=3)
        assert meta.status == "completed_with_errors"

    def test_finish_failed_status(self):
        meta = RunMetadata(portal="test")
        meta.finish(items=0, errors=5)
        assert meta.status == "failed"


class TestBookModels:
    def test_book_summary_creation(self):
        book = BookSummary(
            title="Test Book",
            price="£12.99",
            rating="4",
            availability="In stock",
            detail_url="https://example.com/book/1",
        )
        assert book.title == "Test Book"
        assert book.collected_at is not None

    def test_book_detail_creation(self):
        book = BookDetail(
            title="Test Book",
            price="£12.99",
            price_excl_tax="£12.99",
            price_incl_tax="£12.99",
            tax="£0.00",
            availability="In stock (19 available)",
            rating="4",
            upc="abc123",
            product_type="Books",
            num_reviews=0,
            category="Fiction",
            description="A great book.",
            image_url="https://example.com/img.jpg",
        )
        assert book.title == "Test Book"
        assert book.num_reviews == 0

    def test_book_detail_serialization(self):
        book = BookDetail(
            title="Test",
            price="£1.00",
            price_excl_tax="£1.00",
            price_incl_tax="£1.00",
            tax="£0.00",
            availability="In stock",
            rating="5",
            upc="xyz",
            product_type="Books",
            num_reviews=3,
            category="Nonfiction",
            description="Description.",
            image_url="https://example.com/img.jpg",
        )
        data = book.model_dump(mode="json")
        assert isinstance(data, dict)
        assert "collected_at" in data
        assert data["title"] == "Test"
