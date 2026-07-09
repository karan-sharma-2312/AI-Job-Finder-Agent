# AI Job Finder Agent

Python Apify Actor that finds jobs from LinkedIn and Indeed, normalizes the data into one format, applies your filters, removes duplicates, and returns a clean dataset ready for review or automation.

## What This Tool Is For

Use this tool when you want one repeatable job-search pipeline instead of manually checking multiple portals.

It is built for:

1. Job seekers who want targeted results (skills, locations, experience, salary).
2. Recruiters or talent teams who want a structured feed of matching roles.
3. Automation workflows that need job data in consistent JSON format.

## What You Can Do With It

1. Search LinkedIn and Indeed in one run.
2. Filter by keywords, location, experience, salary, job type, and posting recency.
3. Exclude unwanted terms, companies, or recruiter names.
4. Get run diagnostics (per-source counts, timings, and errors) for troubleshooting.
5. Use output in Apify Dataset, APIs, dashboards, or downstream scripts.

## Typical Use Cases

1. Daily job monitoring for AI Engineer, SDET, Python, and automation roles.
2. Building a personal job tracker from fresh postings.
3. Feeding BI/reporting systems with normalized hiring market data.
4. Running scheduled actor jobs and alerting on newly matched roles.

## What Is Ready

1. Local CLI runtime and Apify runtime in `main.py`.
2. Plugin architecture with independent source adapters.
3. Live conversion phases for LinkedIn and Indeed (with graceful fallbacks).
4. Retry-safe scraper interfaces (HTTP and browser abstraction).
5. Parser + fixture tests for each live-converted source.
6. Docker and Docker Compose setup.
7. Apify input schema and actor metadata files.
8. GitHub Actions CI for automated tests.
9. Source-level diagnostics and run-summary output.
10. Proxy hooks for HTTP and browser scraper clients.

## Runtime Commands

Local run:

```powershell
python main.py run-local --input-file .actor/sample_input.json --output-file exports/jobs.json
```

Apify run:

```powershell
python main.py run-actor
```

Run all tests:

```powershell
python -m pytest -q
```

Preflight script before Git push:

```powershell
./scripts/preflight.ps1
```

## Output Bundle Format

Local output files now contain both jobs and summary:

```json
{
  "jobs": [ ... ],
  "summary": {
    "generatedAt": "...",
    "requestMeta": { ... },
    "counts": {
      "collected": 0,
      "afterFilters": 0,
      "duplicatesRemoved": 0,
      "returned": 0
    },
    "sourceDiagnostics": [
      {
        "source": "linkedin",
        "status": "success|failed",
        "duration_ms": 123,
        "item_count": 0,
        "error": null
      }
    ]
  }
}
```

In Apify dataset output, jobs are pushed first and one additional run-summary record is pushed with `recordType: RUN_SUMMARY`.

## Proxy Configuration

Use `.env` values:

1. `ENABLE_PROXY=true`
2. `PROXY_URL=http://username:password@host:port`

If `ENABLE_PROXY=false`, proxy is not used.

## Important Files

1. Actor metadata: `.actor/actor.json`
2. Actor GUI input schema: `.actor/input_schema.json`
3. Actor sample input: `.actor/sample_input.json`
4. Output schema: `.actor/output_schema.json`
5. Actor folder reference: `.actor/README.md`
6. Apify deployment phases: `docs/PHASES_GIT_TO_APIFY.md`
7. Apify deployment guide: `docs/APIFY_DEPLOYMENT_GUIDE.md`
8. CI workflow: `.github/workflows/ci.yml`
9. Code documentation: `docs/CODEBASE_DOCUMENTATION.md`
10. MIT license: `LICENSE`

## Deployment Flow Summary

1. Validate local pipeline and tests.
2. Commit and push to GitHub.
3. Confirm CI green on GitHub Actions.
4. Create Actor in Apify GUI and connect this repository.
5. Build using Dockerfile and run with input form/JSON.
6. Verify Dataset output and logs.

## Upload This Actor To Apify Using GitHub

1. Push repository to GitHub.
2. In Apify Console, create new Actor.
3. Choose GitHub source and select this repository/branch.
4. Confirm Actor picks up `.actor/actor.json` and `.actor/input_schema.json`.
5. Build Actor.
6. Open Input tab and use form or paste JSON from `.actor/sample_input.json`.
7. Run and inspect logs plus dataset results.

## Notes

1. Some job portals can block anonymous scraping; plugins are implemented to fail safely without crashing the run.
2. LinkedIn and Indeed integrations include staged live extraction plus parser normalization with fixture-backed tests.

## License

This project is licensed under the MIT License. See `LICENSE`.
