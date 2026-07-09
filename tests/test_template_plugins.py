from __future__ import annotations

import pytest

from src.plugins.templates import GreenhouseJobsPlugin, IndeedJobsPlugin, LinkedInJobsPlugin
from src.schemas.input_schema import JobSearchInput


@pytest.mark.asyncio
async def test_linkedin_template_plugin_returns_canonical_jobs() -> None:
    class _FakeHttpClient:
        async def get_text(self, url: str, params: dict | None = None, headers: dict | None = None) -> str:
            return """
            <div class='base-card'>
                <h3 class='base-search-card__title'>Python Engineer</h3>
                <h4 class='base-search-card__subtitle'>Template LinkedIn</h4>
                <span class='job-search-card__location'>Remote</span>
                <a class='base-card__full-link' href='/jobs/view/111'></a>
            </div>
            """

    class _FakeBrowserClient:
        async def fetch_rendered_html(self, url: str) -> str:
            return ""

    plugin = LinkedInJobsPlugin(http_client=_FakeHttpClient(), browser_client=_FakeBrowserClient())
    request = JobSearchInput(keywords=["Python"], locations=["Remote"], remoteAllowed=True)

    jobs = await plugin.collect_jobs(request)

    assert jobs
    assert jobs[0].source == "linkedin"


@pytest.mark.asyncio
async def test_indeed_template_plugin_returns_canonical_jobs() -> None:
    class _FakeHttpClient:
        async def get_text(self, url: str, params: dict | None = None, headers: dict | None = None) -> str:
            return """
            <div class='job_seen_beacon'>
                <h2 class='jobTitle'><a class='jcs-JobTitle' href='/rc/clk?jk=1'>SDET</a></h2>
                <span class='companyName'>Template Indeed</span>
                <div class='companyLocation'>Noida</div>
                <div class='job-snippet'>Automation testing role.</div>
            </div>
            """

    plugin = IndeedJobsPlugin(http_client=_FakeHttpClient())
    request = JobSearchInput(keywords=["SDET"], locations=["Noida"], remoteAllowed=False)

    jobs = await plugin.collect_jobs(request)

    assert jobs
    assert jobs[0].source == "indeed"


@pytest.mark.asyncio
async def test_greenhouse_template_plugin_returns_canonical_jobs() -> None:
    class _FakeHttpClient:
        async def get_json(self, url: str, params: dict | None = None) -> dict:
            return {
                "company": "Template Co",
                "jobs": [
                    {
                        "title": "LLM Engineer",
                        "location": {"name": "Bangalore"},
                        "absolute_url": "https://boards.greenhouse.io/template/jobs/1",
                        "updated_at": "2026-07-01T00:00:00Z",
                        "content": "<p>Work on LLM systems.</p>",
                    }
                ],
            }

    plugin = GreenhouseJobsPlugin(http_client=_FakeHttpClient())
    request = JobSearchInput(
        keywords=["LLM Engineer"],
        locations=["Bangalore"],
        customSearchUrls=["https://boards.greenhouse.io/template"],
    )

    jobs = await plugin.collect_jobs(request)

    assert jobs
    assert jobs[0].source == "greenhouse"
