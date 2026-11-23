# Production readiness runbook

This project is a market-data analysis application, not a brokerage, exchange, or hardened trading platform. Treat upstream market data as best-effort and do not present it as guaranteed real-time exchange data or investment advice.

## Before deploying

- [ ] Select and document the hosting platform, network topology, TLS termination point, and trusted ingress proxy addresses.
- [ ] Provision PostgreSQL with private networking, encrypted connections where supported, automated backups, and a tested restore procedure.
- [ ] Provision private Redis for shared rate-limit storage. Set `RATE_LIMIT_STORAGE_URI` to the authenticated TLS Redis endpoint; do not use `memory://` in production.
- [ ] Set `ENVIRONMENT=production` and provide secrets through the hosting platform's secret manager, not committed files or image layers.
- [ ] Configure HTTPS at the ingress/load balancer and enable HSTS there after confirming HTTPS is enforced for the whole application domain.
- [ ] Configure a restrictive Content Security Policy at the ingress after testing the actual API and Streamlit asset requirements. Start with report-only mode where supported.
- [ ] Configure trusted proxy handling only for known ingress addresses. Do not trust arbitrary forwarded headers from public clients.
- [ ] Restrict database and Redis ingress to application workloads; do not expose either service publicly.

## Identity and application security

- [ ] Verify password hashing parameters and authentication error behavior against the current security documentation.
- [ ] Decide and implement an account recovery process before offering accounts to external users.
- [ ] Define token expiry, logout, revocation, and refresh-token behavior before relying on long-lived sessions.
- [ ] Verify login and signup rate limits across multiple application workers using shared Redis storage.
- [ ] Review CORS, cookie, CSRF, and browser security requirements for the chosen frontend deployment model.
- [ ] Confirm logs contain request metadata but never passwords, tokens, authorization headers, or raw database connection strings.

## Release validation

- [ ] Run the complete CI workflow and review all test results.
- [ ] Run the Dependency Security Audit workflow and resolve or formally assess reported advisories.
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
- [ ] Decide whether one or two approvals are appropriate for the team size; do not require an approval rule that makes a solo-maintained repository impossible to merge.
- [ ] Enable GitHub vulnerability alerts and Dependabot security updates where available.

## Go-live decision

Do not describe the application as production-ready until the deployment-specific items above have owners, evidence, and successful verification. Passing unit tests and dependency scans alone do not validate infrastructure, recovery, browser policy, or operational readiness.