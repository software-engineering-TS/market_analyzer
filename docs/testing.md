# Development and testing

## Supported runtime

Use Python 3.12 for the documented development and CI environment.

## Install

From the repository root:

```bash
python -m venv .venv
# Windows CMD: .venv\Scripts\activate
# PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install -r streamlit-app/requirements.txt
```

## Configure

Copy `.env.example` to `.env` and replace every placeholder. Generate a random `JWT_SECRET_KEY` at least 32 characters long.

Copy `streamlit-app/.env.example` to `streamlit-app/.env` if the Streamlit UI needs a non-default API URL.

## PostgreSQL

Create a local database and role matching the root `.env`, then apply:

```bash
psql -h 127.0.0.1 -U market_analyzer -d market_analyzer -f app/database/schema.sql
```

Load the NSE master list after schema initialization:

```bash
python -m scripts.load_master_stocks
```

## Run

Terminal 1:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
cd streamlit-app
streamlit run app.py
```

## Tests

```bash
python -m pytest -q
```

The default unit tests use fakes and do not require a live database or Yahoo Finance requests. The PostgreSQL schema smoke test runs when `TEST_DATABASE_URL` is set to a disposable test database. CI starts PostgreSQL 16 and runs that test automatically.

## Automated CI and dependency audit

The GitHub Actions CI workflow runs on pull requests targeting `main` and pushes to `main` or `hardening/**`. It provisions PostgreSQL 16, installs backend and Streamlit dependencies, compiles Python sources, and runs the complete pytest suite.

The dependency audit workflow separately runs pip-audit against backend and Streamlit runtime requirements on pull requests, on a weekly schedule, and on manual dispatch.

## Health endpoint checks

- `GET /health/live` should return HTTP 200 while the API process is running; it does not depend on backing services.
- `GET /health/ready` should return HTTP 200 only when required dependencies are reachable; otherwise it returns HTTP 503.
- In development readiness checks PostgreSQL. In production readiness checks PostgreSQL and Redis session-revocation storage.

## Checks before release

- Run the full test suite and dependency audit against the exact release commit.
- Verify signup/login and the profile endpoint against the local database.
- Verify stock search, stock details, historical prices, indicators and watchlist operations.
- Confirm no secret or password hash appears in API responses or logs.
- Exercise readiness behavior with database and Redis available and unavailable.
- Run deployment smoke tests against the real hosting environment, including authentication/logout and graceful process shutdown.
- Validate backups by restoring them; a successful backup job alone is not proof of recoverability.
- Review GitHub Actions before merging a release pull request.
