# Testing

## Automated CI

The GitHub Actions CI workflow runs on pull requests targeting `main` and pushes to `main` or `hardening/**`. It provisions PostgreSQL 16, installs backend and Streamlit dependencies, compiles Python sources, and runs the complete pytest suite.

The dependency audit workflow separately runs pip-audit against backend and Streamlit runtime requirements on pull requests, on a weekly schedule, and on manual dispatch.

## Health endpoint checks

- `GET /health/live` should return HTTP 200 while the API process is running.
- `GET /health/ready` should return HTTP 200 only when required dependencies are reachable; otherwise it returns HTTP 503.
- In development readiness checks PostgreSQL. In production readiness checks PostgreSQL and Redis session-revocation storage.

## Before a production release

Run CI and dependency audit against the exact release commit. Then execute deployment smoke tests against the real hosting environment, including database and Redis failure cases, authentication/logout, stock lookup, watchlists, and graceful process shutdown. Validate backups by restoring them; a successful backup job alone is not proof of recoverability.
