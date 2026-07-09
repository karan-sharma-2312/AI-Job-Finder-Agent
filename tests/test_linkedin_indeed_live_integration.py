from __future__ import annotations

from pathlib import Path

import pytest

from src.parsers.indeed_parser import parse_indeed_jobs
from src.parsers.linkedin_parser import parse_linkedin_jobs
from src.plugins.templates.indeed_plugin import IndeedJobsPlugin
from src.plugins.templates.linkedin_plugin import LinkedInJobsPlugin
from src.schemas.input_schema import JobSearchInput


def _load_fixture(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_linkedin_parser_normalizes_html_fixture() -> None:
    html = _load_fixture("tests/fixtures/linkedin_search_fragment.html")

    jobs = parse_linkedin_jobs(html, source="linkedin", keywords=["Python", "LLM"])

    assert len(jobs) == 2
    assert jobs[0].company == "Acme AI"
    assert jobs[0].remote is True
    assert jobs[1].hybrid is True
    assert "LLM" in jobs[1].skills


def test_indeed_parser_normalizes_html_fixture() -> None:
    html = _load_fixture("tests/fixtures/indeed_search_page.html")

    jobs = parse_indeed_jobs(html, source="indeed", keywords=["Python", "LangChain"])

    assert len(jobs) == 2
    assert jobs[0].company == "Acme Careers"
    assert jobs[0].remote is True
    assert jobs[1].company == "Data Nova"
    assert "LangChain" in jobs[1].skills


class _FakeLinkedinHttpClient:
    async def get_text(self, url: str, params: dict | None = None, headers: dict | None = None) -> str:
        assert "linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search" in url
        return _load_fixture("tests/fixtures/linkedin_search_fragment.html")


class _FakeIndeedHttpClient:
    async def get_text(self, url: str, params: dict | None = None, headers: dict | None = None) -> str:
        assert "indeed.com/jobs" in url
        return _load_fixture("tests/fixtures/indeed_search_page.html")


class _FakeBrowserClient:
    async def fetch_rendered_html(self, url: str) -> str:
        return _load_fixture("tests/fixtures/linkedin_search_fragment.html")


@pytest.mark.asyncio
async def test_linkedin_plugin_live_phase_with_fixture_client() -> None:
    plugin = LinkedInJobsPlugin(http_client=_FakeLinkedinHttpClient(), browser_client=_FakeBrowserClient())
    request = JobSearchInput(keywords=["Python"], locations=["India"])

    jobs = await plugin.collect_jobs(request)

    assert len(jobs) == 2
    assert jobs[0].source == "linkedin"


@pytest.mark.asyncio
async def test_indeed_plugin_live_phase_with_fixture_client() -> None:
    plugin = IndeedJobsPlugin(http_client=_FakeIndeedHttpClient())
    request = JobSearchInput(keywords=["Python"], locations=["India"])

    jobs = await plugin.collect_jobs(request)

    assert len(jobs) == 2
    assert jobs[0].source == "indeed"
