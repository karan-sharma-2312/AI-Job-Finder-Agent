from __future__ import annotations

from urllib.parse import urlparse

from src.parsers.greenhouse_parser import parse_greenhouse_jobs
from src.plugins.base import JobSourcePlugin
from src.schemas.input_schema import JobSearchInput
from src.schemas.job_schema import JobPosting
from src.scrapers.http_client import RetrySafeHttpClient


class GreenhouseJobsPlugin(JobSourcePlugin):
    """Live Greenhouse board integration using retry-safe HTTP + parser normalization."""

    def __init__(self, http_client: RetrySafeHttpClient | None = None, board_tokens: list[str] | None = None) -> None:
        self.http_client = http_client or RetrySafeHttpClient()
        self.board_tokens = board_tokens or []

    @property
    def source_name(self) -> str:
        return "greenhouse"

    def _extract_board_tokens(self, request: JobSearchInput) -> list[str]:
        tokens: list[str] = list(self.board_tokens)

        for raw_url in request.customSearchUrls:
            parsed = urlparse(str(raw_url))
            hostname = (parsed.hostname or "").lower()
            if "greenhouse" not in hostname:
                continue
            path_chunks = [chunk for chunk in parsed.path.split("/") if chunk]
            if path_chunks:
                tokens.append(path_chunks[0])

        deduped: list[str] = []
        seen: set[str] = set()
        for token in tokens:
            normalized = token.strip().lower()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            deduped.append(normalized)
        return deduped

    async def collect_jobs(self, request: JobSearchInput) -> list[JobPosting]:
        board_tokens = self._extract_board_tokens(request)
        if not board_tokens:
            return []

        collected: list[JobPosting] = []
        for token in board_tokens:
            api_url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
            params = {"content": "true"}

            try:
                payload = await self.http_client.get_json(api_url, params=params)
            except Exception:
                continue

            parsed = parse_greenhouse_jobs(
                payload,
                source=self.source_name,
                board_token=token,
                keywords=request.keywords,
            )
            collected.extend(parsed)

        return collected
