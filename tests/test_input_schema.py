from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.schemas.input_schema import JobSearchInput


def test_experience_range_validation_passes() -> None:
    payload = JobSearchInput(
        keywords=["Python"],
        locations=["Remote"],
        minimumExperience=3,
        maximumExperience=5,
    )
    assert payload.minimumExperience == 3
    assert payload.maximumExperience == 5


def test_experience_range_validation_fails_when_inverted() -> None:
    with pytest.raises(ValidationError):
        JobSearchInput(keywords=["Python"], locations=["Remote"], minimumExperience=5, maximumExperience=3)


def test_posted_filters_are_mutually_exclusive() -> None:
    with pytest.raises(ValidationError):
        JobSearchInput(
            keywords=["Python"],
            locations=["Remote"],
            postedToday=True,
            postedThisWeek=True,
        )
