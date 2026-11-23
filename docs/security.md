# Security

## Authentication and sessions

- Passwords are stored as bcrypt hashes; password hashes are never included in public profile responses.
- JWT access tokens are signed with the configured HS256 secret, include a unique `jti`, issue time, and expiry, and are checked against the revocation store on protected requests.
- `POST /sma/v1/logout` revokes the current bearer token until its expiry.
- Production JWT revocation uses the same private Redis service configured for shared rate limiting. Redis failures fail closed for protected requests and logout.
- Development uses an in-process TTL store and is not suitable for multiple workers or production.
- Access-token lifetime is configurable up to 24 hours; the default is 30 minutes. Prefer short-lived access tokens.
- Refresh-token rotation/session renewal and account recovery are not implemented. Design these before offering persistent sessions or account recovery to external users.

## Configuration and deployment

- Production configuration rejects in-memory rate-limit storage, placeholder JWT secrets, and JWT algorithms other than HS256.
- Use a unique randomly generated JWT secret (at least 32 characters) from a secret manager. Never commit secrets.
- Keep PostgreSQL and Redis on private networks, restrict ingress, and use TLS where supported.
- The API exposes `/health/live` and `/health/ready`. Readiness checks PostgreSQL and production Redis.
- HTTPS, HSTS, CSP, trusted ingress/proxy configuration, and deployment-specific CORS/CSRF controls must be configured and tested at the hosting layer.
- Baseline API response headers include nosniff, frame denial, Referrer-Policy, and Permissions-Policy.

## Rate limiting and logging

- Login is limited to 5 requests per IP per minute and signup to 5 requests per IP per hour.
- Production rate limiting must use shared Redis storage to apply limits across workers.
- Logs include request metadata and request IDs. Do not log credentials, bearer tokens, authorization headers, or raw database connection strings.
- Treat forwarded client IP headers as untrusted unless the deployment explicitly configures trusted proxy addresses.

## Remaining security work

- Implement account recovery only with verified ownership, single-use expiring tokens, generic responses, and abuse controls.
- Design refresh-token rotation, reuse detection, and user-visible session revocation before implementing long-lived sessions.
- Test browser-specific CORS/cookie/CSRF behavior for the final frontend topology.
- Configure and validate CSP, HTTPS ingress, HSTS, monitoring, and data-retention controls before public deployment.
