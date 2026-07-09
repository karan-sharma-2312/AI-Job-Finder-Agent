from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, HttpUrl


class JobPosting(BaseModel):
    """Canonical job model produced by all plugins before export."""

    company: str
    title: str
    location: str = "Unknown"
    experience: str | None = None
    salary: str | None = None
    remote: bool = False
    hybrid: bool = False
    employment_type: str | None = None
    skills: List[str] = Field(default_factory=list)
    job_description: str = ""
    source: str
    company_career_url: HttpUrl | None = None
    apply_url: HttpUrl | None = None
    company_website: HttpUrl | None = None
    company_size: str | None = None
    industry: str | None = None
    technologies: List[str] = Field(default_factory=list)
    recruiter: str | None = None
    posted_date: datetime | None = None
    benefits: List[str] = Field(default_factory=list)
    ai_match_score: float | None = Field(default=None, ge=0, le=100)
    ai_summary: str | None = None
    missing_skills: List[str] = Field(default_factory=list)
    resume_suggestions: List[str] = Field(default_factory=list)
    interview_topics: List[str] = Field(default_factory=list)
    reason_for_match: str | None = None
    duplicate_detection_result: str | None = None
    confidence_score: float | None = Field(default=None, ge=0, le=1)
