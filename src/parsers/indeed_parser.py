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


def parse_indeed_jobs(
    html: str,
    *,
    source: str,
    keywords: list[str] | None = None,
    base_url: str = "https://www.indeed.com",
) -> list[JobPosting]:
    """Normalize Indeed search HTML into canonical job postings."""

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div.job_seen_beacon") or soup.select("div.cardOutline")
    keywords = keywords or []

    jobs: list[JobPosting] = []

    for card in cards:
        title_node = card.select_one("h2.jobTitle") or card.select_one("h2")
        link_node = card.select_one("a.jcs-JobTitle") or card.select_one("a")
        company_node = card.select_one("span.companyName")
        location_node = card.select_one("div.companyLocation")
        snippet_node = card.select_one("div.job-snippet")
        posted_node = card.select_one("span.date")

        title = _text_or_default(title_node)
        if not title:
            title = _text_or_default(link_node)
        company = _text_or_default(company_node, "Unknown Company")
        location = _text_or_default(location_node, "Unknown")
        description = _text_or_default(snippet_node, "Indeed listing parsed from search results.")

        if not title:
            continue

        raw_href = link_node.get("href") if link_node else None
        apply_url = urljoin(base_url, str(raw_href)) if raw_href else None
        posted_date = _parse_datetime(posted_node.get("datetime") if posted_node else None)

        searchable_text = f"{title} {company} {location} {description}".lower()
        matched_skills = [keyword for keyword in keywords if keyword.lower() in searchable_text]

        jobs.append(
            JobPosting(
                company=company,
                title=title,
                location=location,
                remote="remote" in location.lower(),
                hybrid="hybrid" in location.lower(),
                skills=matched_skills,
                job_description=description,
                source=source,
                company_career_url=base_url,
                apply_url=apply_url,
                posted_date=posted_date,
                confidence_score=0.76,
            )
        )

    return jobs
