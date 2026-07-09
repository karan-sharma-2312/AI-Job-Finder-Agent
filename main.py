from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import typer
from apify import Actor
from dotenv import load_dotenv
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from src.config.settings import get_settings
from src.core.plugin_manager import PluginManager
from src.plugins.mock_jobs_plugin import MockJobsPlugin
from src.plugins.templates import GreenhouseJobsPlugin, IndeedJobsPlugin, LinkedInJobsPlugin
from src.schemas.input_schema import JobSearchInput
from src.scrapers.http_client import RetrySafeHttpClient
from src.scrapers.playwright_client import RetrySafePlaywrightClient
from src.services.pipeline_service import JobPipelineService

app = typer.Typer(help="AI Job Finder Agent CLI and Apify runtime")
console = Console()


def _load_request(input_file: Path | None) -> JobSearchInput:
    if input_file is None:
        raise ValueError("--input-file is required for local runs")

    payload = json.loads(input_file.read_text(encoding="utf-8"))
    return JobSearchInput.model_validate(payload)


def _build_plugin_manager(settings: Any) -> PluginManager:
    proxy_url = settings.proxy_url if settings.enable_proxy else None
    http_client = RetrySafeHttpClient(
        proxy_url=proxy_url,
        default_headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        },
    )
    browser_client = RetrySafePlaywrightClient(proxy_server=proxy_url)

    manager = PluginManager()
    manager.register(LinkedInJobsPlugin(http_client=http_client, browser_client=browser_client))
    manager.register(IndeedJobsPlugin(http_client=http_client))
    manager.register(GreenhouseJobsPlugin(http_client=http_client))
    manager.register(MockJobsPlugin())
    return manager


async def _run_pipeline(request: JobSearchInput, settings: Any) -> dict[str, Any]:
    manager = _build_plugin_manager(settings)
    pipeline = JobPipelineService(manager)
    jobs, summary = await pipeline.run_with_diagnostics(request)
    return {
        "jobs": [job.model_dump(mode="json") for job in jobs],
        "summary": summary,
    }


def _print_table(jobs: list[dict]) -> None:
    table = Table(title="AI Job Finder Results")
    table.add_column("Company")
    table.add_column("Title")
    table.add_column("Location")
    table.add_column("Source")

    for job in jobs:
        table.add_row(job.get("company", ""), job.get("title", ""), job.get("location", ""), job.get("source", ""))

    console.print(table)
    console.print(f"Total jobs: {len(jobs)}")


def _print_summary(summary: dict[str, Any]) -> None:
    diagnostics = summary.get("sourceDiagnostics", [])
    counts = summary.get("counts", {})
    console.print("Run Summary")
    console.print(
        f"Collected={counts.get('collected', 0)}, "
        f"AfterFilters={counts.get('afterFilters', 0)}, "
        f"DuplicatesRemoved={counts.get('duplicatesRemoved', 0)}, "
        f"Returned={counts.get('returned', 0)}"
    )

    diag_table = Table(title="Source Diagnostics")
    diag_table.add_column("Source")
    diag_table.add_column("Status")
    diag_table.add_column("Items")
    diag_table.add_column("Duration(ms)")
    diag_table.add_column("Error")

    for diag in diagnostics:
        diag_table.add_row(
            str(diag.get("source", "")),
            str(diag.get("status", "")),
            str(diag.get("item_count", "")),
            str(diag.get("duration_ms", "")),
            str(diag.get("error", "") or ""),
        )

    console.print(diag_table)


@app.command()
def run_local(
    input_file: Path = typer.Option(..., "--input-file", help="Path to JSON input payload"),
    output_file: Path | None = typer.Option(None, "--output-file", help="Write results to JSON file"),
) -> None:
    """Run the local job search pipeline."""

    load_dotenv()
    settings = get_settings()
    request = _load_request(input_file)
    run_bundle = asyncio.run(_run_pipeline(request, settings))
    jobs = run_bundle["jobs"]
    summary = run_bundle["summary"]
    _print_table(jobs)
    _print_summary(summary)
    console.print(f"AI scoring enabled by default: {settings.enable_ai_scoring}")

    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(run_bundle, indent=2), encoding="utf-8")
        console.print(f"Saved JSON output to {output_file}")


async def _run_actor_async() -> None:
    async with Actor:
        settings = get_settings()
        actor_input = await Actor.get_input() or {}
        try:
            request = JobSearchInput.model_validate(actor_input)
        except ValidationError as error:
            await Actor.fail(status_message=f"Input validation failed: {error}")
            return

        run_bundle = await _run_pipeline(request, settings)
        jobs = run_bundle["jobs"]
        summary = run_bundle["summary"]
        await Actor.push_data(jobs)
        await Actor.push_data({"recordType": "RUN_SUMMARY", **summary})
        Actor.log.info("Run finished", jobs_count=len(jobs), returned=summary.get("counts", {}).get("returned", 0))


@app.command()
def run_actor() -> None:
    """Run inside Apify Actor runtime (expects input from Apify GUI or API)."""

    load_dotenv()
    asyncio.run(_run_actor_async())


if __name__ == "__main__":
    app()
