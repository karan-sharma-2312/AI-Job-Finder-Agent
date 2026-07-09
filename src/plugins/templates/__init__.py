"""Template source plugins for production integration."""

from src.plugins.templates.indeed_plugin import IndeedJobsPlugin
from src.plugins.templates.linkedin_plugin import LinkedInJobsPlugin

__all__ = [
    "LinkedInJobsPlugin",
    "IndeedJobsPlugin",
]
