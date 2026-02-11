from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class RunMetadata(BaseModel):
    """Metadata about a single pipeline run."""

    portal: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    duration_seconds: float | None = None
    items_collected: int = 0
    errors: int = 0
    status: Literal["running", "completed", "completed_with_errors", "failed"] = "running"

    def _update_status(self) -> None:
        if self.items_collected == 0 and self.errors > 0:
            self.status = "failed"
        elif self.errors > 0:
            self.status = "completed_with_errors"
        else:
            self.status = "completed"

    def finish(self, items: int, errors: int = 0) -> None:
        self.finished_at = datetime.now(timezone.utc)
        self.duration_seconds = (self.finished_at - self.started_at).total_seconds()
        self.items_collected = items
        self.errors = errors
        self._update_status()

    def add_errors(self, count: int) -> None:
        self.errors += count
        self._update_status()
