from __future__ import annotations

import pytest

from src.core.plugin_manager import PluginManager
from src.plugins.mock_jobs_plugin import MockJobsPlugin
from src.schemas.input_schema import JobSearchInput
from src.services.pipeline_service import JobPipelineService


@pytest.mark.asyncio
async def test_pipeline_deduplicates_records() -> None:
    manager = PluginManager()
    manager.register(MockJobsPlugin())

    service = JobPipelineService(manager)
    request = JobSearchInput(keywords=["Python"], locations=["India", "Bangalore"], removeDuplicates=True)

    jobs = await service.run(request)

    assert len(jobs) == 2


@pytest.mark.asyncio
async def test_pipeline_filters_by_keyword() -> None:
    manager = PluginManager()
    manager.register(MockJobsPlugin())

    service = JobPipelineService(manager)
    request = JobSearchInput(keywords=["LLM"], locations=["Bangalore"], removeDuplicates=True)

    jobs = await service.run(request)

    assert len(jobs) == 1
    assert jobs[0].title == "LLM Engineer"
