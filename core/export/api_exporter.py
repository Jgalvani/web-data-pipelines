from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel

from config.logging_config import get_logger
from config.settings import settings
from core.export.base_exporter import BaseExporter
from core.models.run_metadata import RunMetadata
from core.utils.retry import with_retry

log = get_logger(__name__)


class ApiExporter(BaseExporter):
    """Export data via HTTP POST with automatic retries."""

    def __init__(
        self,
        endpoint: str | None = None,
        token: str | None = None,
    ) -> None:
        self._endpoint = endpoint or settings.api_endpoint
        self._token = token or settings.api_token

    @with_retry(attempts=3, min_wait=2, max_wait=30)
    async def _post(self, payload: dict) -> httpx.Response:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                self._endpoint,  # type: ignore[arg-type]
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response

    async def export(
        self,
        data: list[BaseModel],
        metadata: RunMetadata,
    ) -> Any:
        if not self._endpoint:
            log.warning("api_export_skipped", reason="no endpoint configured")
            return None

        payload = {
            "metadata": metadata.model_dump(mode="json"),
            "data": [item.model_dump(mode="json") for item in data],
        }

        response = await self._post(payload)
        log.info(
            "api_exported",
            status=response.status_code,
            items=len(data),
        )
        return response
