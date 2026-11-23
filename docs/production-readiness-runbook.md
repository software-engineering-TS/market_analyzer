# Production readiness runbook

Market Analyzer is a market-data analysis application, not a brokerage, exchange, or hardened trading platform. Upstream market data is best-effort; do not represent it as guaranteed real-time exchange data or investment advice.

## Deployment configuration

- [ ] Select and document the hosting platform, network topology, TLS termination point, and trusted ingress proxy addresses.
- [ ] Provision PostgreSQL with private networking, encrypted connections where supported, automated backups, and a tested restore procedure.
- [ ] Provision private Redis for shared rate-limit and JWT revocation storage. Set `RATE_LIMIT_STORAGE_URI` to the authenticated TLS Redis endpoint; never use `memory://` in production.
- [ ] Set `ENVIRONMENT=production` and provide secrets through the hosting platform's secret manager, not committed files or image layers.
- [ ] Use a unique JWT secret of at least 32 characters. The application currently permits HS256 only.
- [ ] Configure HTTPS at ingress and enable HSTS only after HTTPS is enforced across the application domain.
- [ ] Configure a restrictive Content Security Policy at ingress after testing API and Streamlit asset requirements. Start with report-only mode where supported.
- [ ] Configure trusted proxy handling only for known ingress addresses. Do not trust arbitrary forwarded headers from public clients.
- [ ] Restrict database and Redis ingress to application workloads; do not expose either service publicly.

## Health probes

- `GET /health/live` is a process liveness probe and does not depend on backing services.
- `GET /health/ready` checks PostgreSQL and, in production, Redis session-revocation storage. It returns HTTP 503 when a required dependency is unavailable.
- [ ] Configure the hosting platform's liveness and readiness probes against these endpoints.
- [ ] Confirm readiness behavior against the actual database and Redis services before traffic is routed.

## Identity and application security

- [ ] Verify password hashing parameters and authentication error behavior against the security documentation.
- [ ] Design and implement account recovery with verified email ownership, single-use expiring recovery tokens, abuse controls, and generic responses before offering accounts externally.
- [x] Access tokens have bounded expiry, unique token IDs, and server-side logout revocation. Production revocation uses shared Redis and fails closed if Redis is unavailable.
- [ ] Design a refresh/session renewal policy before relying on long-lived sessions. Refresh-token rotation, reuse detection, and session management are not implemented by this change.
- [ ] Verify login and signup rate limits across multiple application workers using shared Redis storage.
- [ ] Review CORS, cookie, CSRF, and browser security requirements for the chosen frontend deployment model.
- [ ] Confirm logs contain request metadata but never passwords, tokens, authorization headers, or raw database connection strings.

## Release validation

- [ ] Run the complete CI workflow and review all test results.
- [ ] Confirm the Dependency Security Audit workflow passes on the release commit and resolve or formally assess reported advisories.
- [ ] Review Dependabot pull requests individually; inspect changelogs and test compatibility before merging.
- [ ] Run deployment smoke tests for health, authentication, stock lookup, watchlists, and database failure handling.
- [ ] Verify graceful shutdown and database connection cleanup under the actual process manager.
- [ ] Confirm rollback steps and the previous known-good application image/artifact are available.

## Operations after deployment

- [ ] Configure uptime, error-rate, latency, database pool, Redis, and upstream market-data monitoring.
- [ ] Define alert thresholds, on-call ownership, and incident response contacts.
- [ ] Set log retention and access controls appropriate to the data collected.
- [ ] Test database restore and recovery objectives on a schedule; backups are not proven until restore is tested.
- [ ] Review dependency advisories and application security findings regularly.
- [ ] Reassess capacity limits, rate limits, and upstream provider constraints as usage grows.

## Repository governance

- [ ] Enable branch protection or a ruleset for `main` in GitHub repository settings.
- [ ] Require pull requests and the `test` status check before merging.
- [ ] Require branches to be up to date before merge where practical.
- [ ] Restrict force pushes and branch deletion on `main`.
- [ ] Decide whether one or two approvals are appropriate for the team size; avoid approval rules that prevent a solo-maintained repository from merging.
- [ ] Enable GitHub vulnerability alerts and Dependabot security updates where available.

## Go-live decision

Do not describe the application as production-ready until deployment-specific items above have owners, evidence, and successful verification. Passing unit tests and dependency scans alone do not validate infrastructure, recovery, browser policy, or operational readiness.
