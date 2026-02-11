from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class BaseDataModel(BaseModel):
    """Base model for all collected data items."""

    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
