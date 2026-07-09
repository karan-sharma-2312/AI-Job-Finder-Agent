# Apify Deployment Guide

## Required Project Files

1. `.actor/actor.json`
2. `.actor/input_schema.json`
3. `Dockerfile`
4. `main.py`

## Runtime Contract

- Local run command:

```powershell
python main.py run-local --input-file docs/sample_input.json --output-file exports/jobs.json
```

- Apify run command:

```powershell
python main.py run-actor
```

## Input In Apify GUI

Use the JSON payload from `docs/sample_input.json` or fill fields via generated form from `.actor/input_schema.json`.

## Build And Run Checklist

1. Build succeeds in Apify.
2. Actor run starts without input validation errors.
3. Dataset receives job records.
4. Logs confirm graceful handling of blocked sources.

## Troubleshooting

1. If no jobs are returned from LinkedIn/Indeed, keep Greenhouse/custom URLs enabled.
2. If a source blocks requests, pipeline still returns from other plugins.
3. If input errors occur, compare payload fields against `.actor/input_schema.json`.
