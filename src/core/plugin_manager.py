from __future__ import annotations

import asyncio
import time
from dataclasses import asdict, dataclass
from typing import Any

from src.plugins.base import JobSourcePlugin
from src.schemas.input_schema import JobSearchInput
from src.schemas.job_schema import JobPosting


class PluginManager:
    """Registers source plugins and executes them concurrently."""

    def __init__(self) -> None:
        self._plugins: list[JobSourcePlugin] = []

    def register(self, plugin: JobSourcePlugin) -> None:
        self._plugins.append(plugin)

    @property
    def plugins(self) -> list[JobSourcePlugin]:
        return self._plugins

    async def collect_all(self, request: JobSearchInput) -> list[JobPosting]:
        jobs, _diagnostics = await self.collect_all_with_diagnostics(request)
        return jobs

    async def collect_all_with_diagnostics(self, request: JobSearchInput) -> tuple[list[JobPosting], list[dict[str, Any]]]:
        if not self._plugins:
            return [], []

        results = await asyncio.gather(*(self._run_single_plugin(plugin, request) for plugin in self._plugins))

        jobs: list[JobPosting] = []
        diagnostics: list[dict[str, Any]] = []
        for plugin_jobs, plugin_diag in results:
            jobs.extend(plugin_jobs)
            diagnostics.append(asdict(plugin_diag))

        return jobs, diagnostics

    async def _run_single_plugin(
        self,
        plugin: JobSourcePlugin,
        request: JobSearchInput,
    ) -> tuple[list[JobPosting], "PluginExecutionDiagnostic"]:
        started = time.perf_counter()
        plugin_name = plugin.source_name

        try:
            jobs = await plugin.collect_jobs(request)
            duration_ms = int((time.perf_counter() - started) * 1000)
            diagnostic = PluginExecutionDiagnostic(
                source=plugin_name,
                status="success",
                duration_ms=duration_ms,
                item_count=len(jobs),
                error=None,
            )
            return jobs, diagnostic
        except Exception as error:  # noqa: BLE001 - must never fail entire run for single plugin
            duration_ms = int((time.perf_counter() - started) * 1000)
            diagnostic = PluginExecutionDiagnostic(
                source=plugin_name,
                status="failed",
                duration_ms=duration_ms,
                item_count=0,
                error=str(error),
            )
            return [], diagnostic


@dataclass(slots=True)
class PluginExecutionDiagnostic:
    """Diagnostics captured for each plugin run."""

    source: str
    status: str
    duration_ms: int
    item_count: int
    error: str | None
