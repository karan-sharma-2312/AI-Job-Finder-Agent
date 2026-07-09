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

    async def collect_jobs(self, request: JobSearchInput) -> list[JobPosting]:
        keyword = request.keywords[0]
        location = request.locations[0]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }

        html = ""

        # Phase 2: direct guest endpoint.
        try:
            html = await self.http_client.get_text(
                "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search",
                params={"keywords": keyword, "location": location, "start": 0},
                headers=headers,
            )
        except Exception:
            html = ""

        # Phase 2 fallback: rendered page capture.
        if not html:
            search_url = (
                "https://www.linkedin.com/jobs/search"
                f"?keywords={keyword.replace(' ', '%20')}&location={location.replace(' ', '%20')}"
            )
            try:
                html = await self.browser_client.fetch_rendered_html(search_url)
            except Exception:
                html = ""

        if not html:
            return []

        return parse_linkedin_jobs(html, source=self.source_name, keywords=request.keywords)
