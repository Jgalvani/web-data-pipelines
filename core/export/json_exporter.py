from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from config.logging_config import get_logger
from config.settings import settings
from core.export.base_exporter import BaseExporter
from core.models.run_metadata import RunMetadata

log = get_logger(__name__)


class JsonExporter(BaseExporter):
    """Export data as normalized JSON files."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self._output_dir = output_dir or settings.output_dir

    async def export(
        self,
        data: list[BaseModel],
        metadata: RunMetadata,
    ) -> Path:
        self._output_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{metadata.portal}_{ts}.json"
        filepath = self._output_dir / filename

        payload = {
            "metadata": metadata.model_dump(mode="json"),
            "data": [item.model_dump(mode="json") for item in data],
        }

        filepath.write_text(json.dumps(payload, indent=2, default=str))
        log.info("json_exported", path=str(filepath), items=len(data))
        return filepath
