from __future__ import annotations

from abc import ABC, abstractmethod

from src.schemas.input_schema import JobSearchInput
from src.schemas.job_schema import JobPosting


class JobSourcePlugin(ABC):
    """Interface all job source plugins must implement."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human-readable source identifier (for example, LinkedIn)."""

    @abstractmethod
    async def collect_jobs(self, request: JobSearchInput) -> list[JobPosting]:
        """Collect jobs from this source and return canonical JobPosting items."""
