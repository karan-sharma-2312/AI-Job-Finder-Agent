from __future__ import annotations

import pytest

from src.core.plugin_manager import PluginManager
from src.schemas.input_schema import JobSearchInput
from src.schemas.job_schema import JobPosting
from src.services.pipeline_service import JobPipelineService


class _StaticSourcePlugin:
    @property
    def source_name(self) -> str:
        return "linkedin"

    async def collect_jobs(self, request: JobSearchInput) -> list[JobPosting]:
        return [
            JobPosting(
                company="Acme AI",
                title="Python Automation Engineer",
                location="Bangalore",
                remote=False,
                hybrid=True,
                skills=["Python", "Automation"],
                job_description="Automation role with Python",
                source="linkedin",
                apply_url="https://example.com/jobs/1",
            ),
            JobPosting(
                company="Acme AI",
                title="Python Automation Engineer",
                location="Bangalore",
                remote=False,
                hybrid=True,
                skills=["Python", "Automation"],
                job_description="Duplicate entry for dedupe check",
                source="linkedin",
                apply_url="https://example.com/jobs/1",
            ),
            JobPosting(
                company="Beta Labs",
                title="LLM Engineer",
                location="Bangalore",
                remote=False,
                hybrid=False,
                skills=["LLM", "Python"],
                job_description="Build enterprise LLM systems",
                source="indeed",
                apply_url="https://example.com/jobs/2",
            ),
        ]


@pytest.mark.asyncio
async def test_pipeline_deduplicates_records() -> None:
    manager = PluginManager()
    manager.register(_StaticSourcePlugin())

    service = JobPipelineService(manager)
    request = JobSearchInput(keywords=["Python"], locations=["India", "Bangalore"], removeDuplicates=True)

    jobs = await service.run(request)

    assert len(jobs) == 2


@pytest.mark.asyncio
async def test_pipeline_filters_by_keyword() -> None:
    manager = PluginManager()
    manager.register(_StaticSourcePlugin())

    service = JobPipelineService(manager)
    request = JobSearchInput(keywords=["LLM"], locations=["Bangalore"], removeDuplicates=True)

    jobs = await service.run(request)

    assert len(jobs) == 1
    assert jobs[0].title == "LLM Engineer"
