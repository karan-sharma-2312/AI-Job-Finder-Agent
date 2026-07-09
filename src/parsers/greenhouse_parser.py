from __future__ import annotations

from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup

from src.schemas.job_schema import JobPosting


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _extract_metadata_value(job: dict[str, Any], candidate_names: list[str]) -> str | None:
    metadata = job.get("metadata") or []
    for item in metadata:
        name = str(item.get("name", "")).strip().lower()
        value = str(item.get("value", "")).strip()
        if not value:
            continue
        if any(candidate.lower() in name for candidate in candidate_names):
            return value
    return None


def parse_greenhouse_jobs(
    payload: dict[str, Any],
    *,
    source: str,
    board_token: str,
    keywords: list[str] | None = None,
) -> list[JobPosting]:
    """Normalize Greenhouse board response into canonical JobPosting records."""

    jobs_data = payload.get("jobs") or []
    company = str(payload.get("company") or board_token).strip() or "Unknown Company"
    career_url = f"https://boards.greenhouse.io/{board_token}"

    parsed_jobs: list[JobPosting] = []
    keywords = keywords or []

    for raw in jobs_data:
        title = str(raw.get("title") or "").strip()
        if not title:
            continue

        location_name = str((raw.get("location") or {}).get("name") or "Unknown").strip()
        location_lower = location_name.lower()

        content_html = str(raw.get("content") or "")
        description = BeautifulSoup(content_html, "html.parser").get_text(" ", strip=True)

        posted_date = _parse_datetime(raw.get("updated_at") or raw.get("created_at"))
        apply_url = raw.get("absolute_url")

        employment_type = _extract_metadata_value(raw, ["employment", "work type", "contract"])
        experience = _extract_metadata_value(raw, ["experience", "seniority"])
        salary = _extract_metadata_value(raw, ["salary", "compensation", "ctc"])

        matched_skills = [
            keyword
            for keyword in keywords
            if keyword.lower() in f"{title} {description}".lower()
        ]

        parsed_jobs.append(
            JobPosting(
                company=company,
                title=title,
                location=location_name,
                experience=experience,
                salary=salary,
                remote="remote" in location_lower,
                hybrid="hybrid" in location_lower,
                employment_type=employment_type,
                skills=matched_skills,
                job_description=description,
                source=source,
                company_career_url=career_url,
                apply_url=apply_url,
                posted_date=posted_date,
                confidence_score=0.83,
            )
        )

    return parsed_jobs
