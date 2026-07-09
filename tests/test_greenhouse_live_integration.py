from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.parsers.greenhouse_parser import parse_greenhouse_jobs
from src.plugins.templates.greenhouse_plugin import GreenhouseJobsPlugin
from src.schemas.input_schema import JobSearchInput


def _load_fixture() -> dict:
    fixture_path = Path("tests/fixtures/greenhouse_jobs_response.json")
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def test_greenhouse_parser_normalizes_fixture_payload() -> None:
    payload = _load_fixture()

    jobs = parse_greenhouse_jobs(
        payload,
        source="greenhouse",
        board_token="acme",
        keywords=["Python", "LLM", "LangChain"],
    )

    assert len(jobs) == 2
    assert jobs[0].company == "Acme Careers"
    assert jobs[0].remote is True
    assert jobs[1].hybrid is True
    assert jobs[1].source == "greenhouse"
    assert "LangChain" in jobs[1].skills


class _FakeHttpClient:
    async def get_json(self, url: str, params: dict | None = None) -> dict:
        assert "boards-api.greenhouse.io/v1/boards/acme/jobs" in url
        assert params == {"content": "true"}
        return _load_fixture()


@pytest.mark.asyncio
async def test_greenhouse_plugin_fetches_live_board_endpoint_with_fixture_payload() -> None:
    plugin = GreenhouseJobsPlugin(http_client=_FakeHttpClient())
    request = JobSearchInput(
        keywords=["Python", "LLM"],
        locations=["India", "Bangalore"],
        customSearchUrls=["https://boards.greenhouse.io/acme"],
    )

    jobs = await plugin.collect_jobs(request)

    assert len(jobs) == 2
    assert jobs[0].source == "greenhouse"
