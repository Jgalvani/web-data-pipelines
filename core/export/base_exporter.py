from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from core.models.run_metadata import RunMetadata


class BaseExporter(ABC):
    """Abstract interface for exporting collected data."""

    @abstractmethod
    async def export(
        self,
        data: list[BaseModel],
        metadata: RunMetadata,
    ) -> Any:
        """Export a batch of data items along with run metadata."""
