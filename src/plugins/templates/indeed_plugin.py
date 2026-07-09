from __future__ import annotations

from src.parsers.indeed_parser import parse_indeed_jobs
from src.plugins.base import JobSourcePlugin
from src.schemas.input_schema import JobSearchInput
from src.schemas.job_schema import JobPosting
from src.scrapers.http_client import RetrySafeHttpClient


class IndeedJobsPlugin(JobSourcePlugin):
    """Live Indeed extraction using retry-safe HTTP + parser normalization."""

    def __init__(self, http_client: RetrySafeHttpClient | None = None) -> None:
        self.http_client = http_client or RetrySafeHttpClient()

    @property
    def source_name(self) -> str:
        return "indeed"

    @staticmethod
    def _job_key(job: JobPosting) -> str:
        return "::".join(
            [
                job.company.strip().lower(),
                job.title.strip().lower(),
                job.location.strip().lower(),
                str(job.apply_url or "").strip().lower(),
            ]
        )

    async def collect_jobs(self, request: JobSearchInput) -> list[JobPosting]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }

        collected: list[JobPosting] = []
        seen: set[str] = set()

        for keyword in request.keywords:
            for location in request.locations:
                for start in (0, 10, 20, 30):
                    html = ""

                    try:
                        html = await self.http_client.get_text(
                            "https://www.indeed.com/jobs",
                            params={"q": keyword, "l": location, "start": start},
                            headers=headers,
                        )
                    except Exception:
                        html = ""

                    if not html:
                        continue

                    parsed = parse_indeed_jobs(html, source=self.source_name, keywords=request.keywords)
                    for job in parsed:
                        dedupe_key = self._job_key(job)
                        if dedupe_key in seen:
                            continue
                        seen.add(dedupe_key)
                        collected.append(job)

                    if len(collected) >= request.maxResults:
                        return collected[: request.maxResults]

        return collected[: request.maxResults]
