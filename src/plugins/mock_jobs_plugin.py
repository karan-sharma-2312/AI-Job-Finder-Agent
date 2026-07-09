from __future__ import annotations

from src.plugins.base import JobSourcePlugin
from src.schemas.input_schema import JobSearchInput
from src.schemas.job_schema import JobPosting


class MockJobsPlugin(JobSourcePlugin):
    """Local development plugin with deterministic sample data."""

    @property
    def source_name(self) -> str:
        return "mock"

    async def collect_jobs(self, request: JobSearchInput) -> list[JobPosting]:
        location = request.locations[0] if request.locations else "Remote"
        return [
            JobPosting(
                company="Acme AI",
                title="Python Automation Engineer",
                location=location,
                remote=True,
                employment_type="Full Time",
                skills=["Python", "Playwright", "Pytest"],
                job_description="Build test automation and scraping workflows.",
                source=self.source_name,
                apply_url="https://example.com/jobs/acme-automation",
                company_career_url="https://example.com/careers",
                confidence_score=0.92,
            ),
            JobPosting(
                company="Acme AI",
                title="Python Automation Engineer",
                location=location,
                remote=True,
                employment_type="Full Time",
                skills=["Python", "Playwright"],
                job_description="Build resilient automation systems.",
                source=self.source_name,
                apply_url="https://example.com/jobs/acme-automation",
                company_career_url="https://example.com/careers",
                confidence_score=0.88,
            ),
            JobPosting(
                company="Nimbus Labs",
                title="LLM Engineer",
                location="Bangalore",
                remote=False,
                hybrid=True,
                employment_type="Full Time",
                skills=["Python", "LangChain", "LLMs"],
                job_description="Build and evaluate LLM pipelines.",
                source=self.source_name,
                apply_url="https://example.com/jobs/nimbus-llm",
                company_career_url="https://example.com/nimbus-careers",
                confidence_score=0.9,
            ),
        ]
