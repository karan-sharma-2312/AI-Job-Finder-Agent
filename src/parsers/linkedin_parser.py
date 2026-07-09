from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import urljoin

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


def _text_or_default(node: Any, default: str = "") -> str:
    if node is None:
        return default
    return node.get_text(" ", strip=True)


def parse_linkedin_jobs(
    html: str,
    *,
    source: str,
    keywords: list[str] | None = None,
) -> list[JobPosting]:
    """Normalize LinkedIn search HTML fragments into canonical job postings."""

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("li .base-card") or soup.select("div.base-card") or soup.select("li")
    keywords = keywords or []

    jobs: list[JobPosting] = []

    for card in cards:
        title_node = card.select_one("h3.base-search-card__title") or card.select_one("h3")
        company_node = card.select_one("h4.base-search-card__subtitle") or card.select_one("h4")
        location_node = card.select_one("span.job-search-card__location") or card.select_one("span")
        link_node = card.select_one("a.base-card__full-link") or card.select_one("a")
        time_node = card.select_one("time")

        title = _text_or_default(title_node)
        company = _text_or_default(company_node, "Unknown Company")
        location = _text_or_default(location_node, "Unknown")

        if not title:
            continue

        raw_href = link_node.get("href") if link_node else None
        apply_url = urljoin("https://www.linkedin.com", str(raw_href)) if raw_href else None
        posted_date = _parse_datetime(time_node.get("datetime") if time_node else None)

        searchable_text = f"{title} {company} {location}".lower()
        matched_skills = [keyword for keyword in keywords if keyword.lower() in searchable_text]

        jobs.append(
            JobPosting(
                company=company,
                title=title,
                location=location,
                remote="remote" in location.lower(),
                hybrid="hybrid" in location.lower(),
                skills=matched_skills,
                job_description="LinkedIn listing parsed from search results.",
                source=source,
                company_career_url="https://www.linkedin.com/jobs",
                apply_url=apply_url,
                posted_date=posted_date,
                confidence_score=0.78,
            )
        )

    return jobs
