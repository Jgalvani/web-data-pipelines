from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.export.json_exporter import JsonExporter
from core.models.run_metadata import RunMetadata
from portals.books_toscrape.models import BookDetail


def _make_book(**overrides) -> BookDetail:
    defaults = dict(
        title="Test Book",
        price="£12.99",
        price_excl_tax="£12.99",
        price_incl_tax="£12.99",
        tax="£0.00",
        availability="In stock",
        rating="4",
        upc="abc123",
        product_type="Books",
        num_reviews=0,
        category="Fiction",
        description="A test book.",
        image_url="https://example.com/img.jpg",
    )
    defaults.update(overrides)
    return BookDetail(**defaults)


@pytest.mark.asyncio
async def test_json_exporter_creates_file(tmp_path: Path):
    exporter = JsonExporter(output_dir=tmp_path)
    metadata = RunMetadata(portal="test")
    books = [_make_book(title="Book 1"), _make_book(title="Book 2")]

    result = await exporter.export(books, metadata)

    assert result.exists()
    assert result.suffix == ".json"

    content = json.loads(result.read_text())
    assert len(content["data"]) == 2
    assert content["metadata"]["portal"] == "test"
    assert content["data"][0]["title"] == "Book 1"


@pytest.mark.asyncio
async def test_json_exporter_creates_output_dir(tmp_path: Path):
    output_dir = tmp_path / "nested" / "output"
    exporter = JsonExporter(output_dir=output_dir)
    metadata = RunMetadata(portal="test")

    result = await exporter.export([_make_book()], metadata)

    assert output_dir.exists()
    assert result.exists()
