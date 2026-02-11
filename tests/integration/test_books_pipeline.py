from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.export.json_exporter import JsonExporter
from portals.books_toscrape.pipeline import BooksToscrapePipeline


@pytest.mark.asyncio
async def test_books_pipeline_collects_data(tmp_path: Path):
    """Integration test: run pipeline against live books.toscrape.com."""
    exporter = JsonExporter(output_dir=tmp_path)
    pipeline = BooksToscrapePipeline(
        headless=True,
        max_pages=1,
        exporters=[exporter],
    )

    metadata = await pipeline.run()

    assert metadata.status == "completed"
    assert metadata.items_collected > 0

    # Verify JSON file was created
    json_files = list(tmp_path.glob("*.json"))
    assert len(json_files) == 1

    content = json.loads(json_files[0].read_text())
    assert len(content["data"]) > 0
    assert "title" in content["data"][0]
    assert "upc" in content["data"][0]
