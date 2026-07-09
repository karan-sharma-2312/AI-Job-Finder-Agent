from __future__ import annotations

from typing import Literal
from typing import List

from pydantic import BaseModel, Field, HttpUrl, ValidationInfo, field_validator, model_validator


class JobSearchInput(BaseModel):
    """Validated search input accepted by CLI and Apify actor entrypoint."""

    keywords: List[str] = Field(..., min_length=1)
    locations: List[str] = Field(..., min_length=1)
    minimumExperience: int | None = Field(default=None, ge=0)
    maximumExperience: int | None = Field(default=None, ge=0)
    minimumSalary: int | None = Field(default=None, ge=0)
    maximumSalary: int | None = Field(default=None, ge=0)
    employmentType: List[str] = Field(default_factory=list)
    remoteAllowed: bool = False
    hybridAllowed: bool = True
    maxResults: int = Field(default=500, ge=1, le=5000)
    enableAIScoring: bool = True
    removeDuplicates: bool = True
    includeCompanyResearch: bool = True
    includeHiringManager: bool = False
    includeMockData: bool = False
    includeCompanies: List[str] = Field(default_factory=list)
    excludeCompanies: List[str] = Field(default_factory=list)
    excludeRecruiters: List[str] = Field(default_factory=list)
    excludeKeywords: List[str] = Field(default_factory=list)
    blacklist: List[str] = Field(default_factory=list)
    whitelist: List[str] = Field(default_factory=list)
    postedToday: bool = False
    postedThisWeek: bool = False
    postedThisMonth: bool = False
    customSearchUrls: List[HttpUrl] = Field(default_factory=list)
    aiProvider: Literal["auto", "openai", "gemini", "none"] = "auto"

    @field_validator("maximumExperience")
    @classmethod
    def validate_experience_range(cls, value: int | None, info: ValidationInfo) -> int | None:
        minimum = info.data.get("minimumExperience") if info.data else None
        if value is not None and minimum is not None and value < minimum:
            raise ValueError("maximumExperience must be >= minimumExperience")
        return value

    @field_validator("maximumSalary")
    @classmethod
    def validate_salary_range(cls, value: int | None, info: ValidationInfo) -> int | None:
        minimum = info.data.get("minimumSalary") if info.data else None
        if value is not None and minimum is not None and value < minimum:
            raise ValueError("maximumSalary must be >= minimumSalary")
        return value

    @model_validator(mode="after")
    def validate_posted_filter_flags(self) -> "JobSearchInput":
        enabled = [self.postedToday, self.postedThisWeek, self.postedThisMonth]
        if sum(1 for flag in enabled if flag) > 1:
            raise ValueError("Only one of postedToday, postedThisWeek, postedThisMonth can be true")
        return self
