Param(
    [string]$InputFile = "docs/sample_input.json"
)

$ErrorActionPreference = "Stop"

Write-Host "[1/3] Running tests..."
python -m pytest -q

Write-Host "[2/3] Running local pipeline smoke test..."
python main.py run-local --input-file $InputFile --output-file exports/preflight_jobs.json

Write-Host "[3/3] Preflight completed successfully."
