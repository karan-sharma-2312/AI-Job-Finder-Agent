# Codebase Documentation

This document explains the purpose of each major file so future updates are fast and safe.

## Entry Point

1. `main.py`
- CLI command `run-local` for local JSON input.
- Actor command `run-actor` for Apify runtime.
- Builds plugin manager with proxy-aware scraper clients.
- Prints source diagnostics and writes run bundle (`jobs` + `summary`).

## Core

1. `src/core/plugin_manager.py`
- Registers source plugins.
- Executes all plugins concurrently.
- Captures source-level diagnostics: status, duration, item count, error.

## Pipeline

1. `src/services/pipeline_service.py`
- Applies filtering rules.
- Performs deduplication.
- Returns both final jobs and run summary metadata.

## Schemas

1. `src/schemas/input_schema.py`
- Validates actor/CLI input contract.
- Includes required and optional fields.
- Guards invalid ranges and conflicting posted-date flags.

2. `src/schemas/job_schema.py`
- Canonical output model for every source plugin.

## Plugins

1. `src/plugins/base.py`
- Shared plugin interface used by all job sources.

2. `src/plugins/templates/linkedin_plugin.py`
- Live staged extraction (HTTP guest endpoint + browser fallback).
- Parsed by `src/parsers/linkedin_parser.py`.

3. `src/plugins/templates/indeed_plugin.py`
- Live staged extraction from Indeed search HTML.
- Parsed by `src/parsers/indeed_parser.py`.

4. `src/plugins/templates/greenhouse_plugin.py`
- Live board endpoint integration.
- Parsed by `src/parsers/greenhouse_parser.py`.

5. `src/plugins/mock_jobs_plugin.py`
- Deterministic fallback source for local development.

## Scrapers

1. `src/scrapers/http_client.py`
- Retry-safe async HTTP calls.
- Supports default headers and proxy hook.

2. `src/scrapers/playwright_client.py`
- Retry-safe browser abstraction with proxy placeholder.

## Parsers

1. `src/parsers/linkedin_parser.py`
- Normalizes LinkedIn HTML cards into canonical model.

2. `src/parsers/indeed_parser.py`
- Normalizes Indeed HTML cards into canonical model.

3. `src/parsers/greenhouse_parser.py`
- Normalizes Greenhouse board API payload into canonical model.

## Actor And Deployment Files

1. `.actor/actor.json`
- Actor metadata, run command, storage defaults.

2. `.actor/input_schema.json`
- Apify GUI input fields and validation.

3. `Dockerfile`
- Runtime container image.

4. `docker-compose.yml`
- Local container orchestration.

## Tests

1. `tests/fixtures/*`
- Stable fixture payloads and HTML fragments.

2. `tests/test_pipeline.py`
- Pipeline filtering and dedup behavior.

3. `tests/test_input_schema.py`
- Input validation behavior.

4. `tests/test_greenhouse_live_integration.py`
- Greenhouse parser + plugin integration phase.

5. `tests/test_linkedin_indeed_live_integration.py`
- LinkedIn/Indeed parser + plugin integration phase.

6. `tests/test_template_plugins.py`
- Plugin-level canonical output checks.

## CI And Scripts

1. `.github/workflows/ci.yml`
- Runs tests on push and PR.

2. `scripts/preflight.ps1`
- Local pre-push check script.
