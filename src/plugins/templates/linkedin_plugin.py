from __future__ import annotations

from src.parsers.linkedin_parser import parse_linkedin_jobs
from src.plugins.base import JobSourcePlugin
from src.schemas.input_schema import JobSearchInput
from src.schemas.job_schema import JobPosting
from src.scrapers.http_client import RetrySafeHttpClient
from src.scrapers.playwright_client import RetrySafePlaywrightClient


class LinkedInJobsPlugin(JobSourcePlugin):
    """Live LinkedIn extraction using guest search endpoint and browser fallback."""

    def __init__(
        self,
        http_client: RetrySafeHttpClient | None = None,
        browser_client: RetrySafePlaywrightClient | None = None,
    ) -> None:
        self.http_client = http_client or RetrySafeHttpClient()
        self.browser_client = browser_client or RetrySafePlaywrightClient()

    @property
    def source_name(self) -> str:
        return "linkedin"

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
                for start in (0, 25, 50, 75):
                    html = ""

                    try:
                        html = await self.http_client.get_text(
                            "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search",
                            params={"keywords": keyword, "location": location, "start": start},
                            headers=headers,
                        )
                    except Exception:
                        html = ""

                    if not html and start == 0:
                        search_url = (
                            "https://www.linkedin.com/jobs/search"
                            f"?keywords={keyword.replace(' ', '%20')}&location={location.replace(' ', '%20')}"
                        )
                        try:
                            html = await self.browser_client.fetch_rendered_html(search_url)
                        except Exception:
                            html = ""

                    if not html:
                        continue

                    parsed = parse_linkedin_jobs(html, source=self.source_name, keywords=request.keywords)
                    for job in parsed:
                        dedupe_key = self._job_key(job)
                        if dedupe_key in seen:
                            continue
                        seen.add(dedupe_key)
                        collected.append(job)

                    if len(collected) >= request.maxResults:
                        return collected[: request.maxResults]

        return collected[: request.maxResults]
