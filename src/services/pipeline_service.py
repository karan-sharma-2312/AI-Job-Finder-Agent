from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.core.plugin_manager import PluginManager
from src.schemas.input_schema import JobSearchInput
from src.schemas.job_schema import JobPosting


class JobPipelineService:
    """Orchestrates collection, filtering, and deduplication."""

    def __init__(self, plugin_manager: PluginManager) -> None:
        self.plugin_manager = plugin_manager

    async def run(self, request: JobSearchInput) -> list[JobPosting]:
        jobs, _summary = await self.run_with_diagnostics(request)
        return jobs

    async def run_with_diagnostics(self, request: JobSearchInput) -> tuple[list[JobPosting], dict[str, Any]]:
        collected_jobs, source_diagnostics = await self.plugin_manager.collect_all_with_diagnostics(request)

        filtered_jobs = self._apply_filters(collected_jobs, request)
        filtered_count = len(filtered_jobs)

        deduped_jobs = filtered_jobs
        duplicates_removed = 0
        if request.removeDuplicates:
            deduped_jobs = self._deduplicate(filtered_jobs)
            duplicates_removed = max(filtered_count - len(deduped_jobs), 0)

        final_jobs = deduped_jobs[: request.maxResults]

        summary = {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "requestMeta": {
                "keywords": request.keywords,
                "locations": request.locations,
                "maxResults": request.maxResults,
                "removeDuplicates": request.removeDuplicates,
            },
            "counts": {
                "collected": len(collected_jobs),
                "afterFilters": filtered_count,
                "duplicatesRemoved": duplicates_removed,
                "returned": len(final_jobs),
            },
            "sourceDiagnostics": source_diagnostics,
        }

        return final_jobs, summary

    def _apply_filters(self, jobs: list[JobPosting], request: JobSearchInput) -> list[JobPosting]:
        filtered = jobs

        if request.keywords:
            keywords_lower = [keyword.lower() for keyword in request.keywords]
            filtered = [
                job
                for job in filtered
                if any(
                    keyword in f"{job.title} {job.job_description} {' '.join(job.skills)}".lower()
                    for keyword in keywords_lower
                )
            ]

        if request.locations:
            locations_lower = [location.lower() for location in request.locations]
            filtered = [
                job
                for job in filtered
                if any(location in job.location.lower() for location in locations_lower)
                or (request.remoteAllowed and job.remote)
            ]

        if request.employmentType:
            allowed_types = {job_type.lower() for job_type in request.employmentType}
            filtered = [
                job
                for job in filtered
                if job.employment_type is not None and job.employment_type.lower() in allowed_types
            ]

        if not request.hybridAllowed:
            filtered = [job for job in filtered if not job.hybrid]

        if request.includeCompanies:
            include_companies = {company.lower() for company in request.includeCompanies}
            filtered = [job for job in filtered if job.company.lower() in include_companies]

        if request.whitelist:
            whitelist_lower = [item.lower() for item in request.whitelist]
            filtered = [
                job
                for job in filtered
                if any(item in f"{job.company} {job.title}".lower() for item in whitelist_lower)
            ]

        if request.excludeCompanies:
            excluded = {company.lower() for company in request.excludeCompanies}
            filtered = [job for job in filtered if job.company.lower() not in excluded]

        if request.excludeRecruiters:
            excluded_recruiters = {recruiter.lower() for recruiter in request.excludeRecruiters}
            filtered = [
                job
                for job in filtered
                if job.recruiter is None or job.recruiter.lower() not in excluded_recruiters
            ]

        if request.excludeKeywords:
            excluded_keywords = [keyword.lower() for keyword in request.excludeKeywords]
            filtered = [
                job
                for job in filtered
                if not any(keyword in f"{job.title} {job.job_description}".lower() for keyword in excluded_keywords)
            ]

        if request.blacklist:
            blacklist_lower = [item.lower() for item in request.blacklist]
            filtered = [
                job
                for job in filtered
                if not any(item in f"{job.company} {job.title} {job.job_description}".lower() for item in blacklist_lower)
            ]

        return filtered

    def _deduplicate(self, jobs: list[JobPosting]) -> list[JobPosting]:
        seen: set[str] = set()
        deduped: list[JobPosting] = []

        for job in jobs:
            dedupe_key = "::".join(
                [
                    job.company.strip().lower(),
                    job.title.strip().lower(),
                    job.location.strip().lower(),
                    str(job.apply_url or "").strip().lower(),
                    str(job.company_career_url or "").strip().lower(),
                ]
            )
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            deduped.append(job)

        return deduped
