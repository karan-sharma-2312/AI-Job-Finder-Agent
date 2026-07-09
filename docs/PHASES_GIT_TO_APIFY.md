# Git To Apify Phases

## Phase 1: Local Development

1. Create and activate Python 3.12 environment.
2. Install dependencies.
3. Install Playwright browsers.
4. Run tests.
5. Run local pipeline with sample JSON.

Commands:

```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python -m playwright install
python -m pytest -q
python main.py run-local --input-file .actor/sample_input.json --output-file exports/jobs_local.json
```

## Phase 2: Integration Validation

1. Validate live plugin phases through tests with fixtures.
2. Confirm parser normalization behavior.
3. Confirm fallback behavior for blocked sources.

Commands:

```powershell
python -m pytest -q
```

## Phase 3: Git Preparation

1. Ensure `.env` is not committed.
2. Verify `.gitignore` excludes logs, exports, and local envs.
3. Run preflight script before every push.

Commands:

```powershell
./scripts/preflight.ps1
```

## Phase 4: GitHub Push

1. Initialize repo (if needed).
2. Commit project files.
3. Push to main branch.
4. Confirm CI pipeline is green.

Commands:

```powershell
git init
git add .
git commit -m "Initial production-ready AI Job Finder Actor"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

## Phase 5: Apify Actor Setup (GUI)

1. Create a new Actor in Apify Console.
2. Connect GitHub repository.
3. Ensure `.actor/actor.json` and `.actor/input_schema.json` are detected.
4. Build Actor with `Dockerfile`.
5. Run with sample input from `.actor/sample_input.json`.

## Phase 6: Apify Runtime Validation

1. Check Run logs for source-level behavior.
2. Inspect Dataset outputs.
3. Verify input validation errors are clear.
4. Confirm Actor does not crash on source failures.

## Phase 7: Production Release

1. Pin any strict dependency versions if needed.
2. Add proxy/session configuration for blocked sites.
3. Add Apify Store listing metadata and usage docs.
4. Publish Actor.
