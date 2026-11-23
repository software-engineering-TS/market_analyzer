# Security

## Authentication

- Passwords are stored as bcrypt hashes; plaintext passwords must never be logged or persisted.
- JWT signing and verification use PyJWT with an explicit algorithm allowlist and `JWT_SECRET_KEY` from the root environment file. Use a random secret of at least 32 characters and keep it out of source control.
- Access tokens contain a unique `jti` claim and an expiry. Protected requests check revocation before resolving the user.
- `POST /sma/v1/logout` revokes the current bearer token until its original expiry. Clients must discard the token after logout.
- Production revocation records are stored in the same private Redis service configured by `RATE_LIMIT_STORAGE_URI`. If Redis is unavailable, token verification and revocation fail closed rather than silently accepting a token.
- Development uses a process-local TTL store only. It is not shared across workers and is not suitable for production.
- Login is limited to 5 attempts per client IP per minute; signup is limited to 5 attempts per client IP per hour.
- Rate limits use the client socket address. Trust proxy headers only from a known ingress that strips client-supplied forwarding headers.
- Profile responses contain public fields only; password hashes and internal account fields must not be returned.

## Database

- Use a dedicated PostgreSQL role with access only to the Market Analyzer database.
- Never commit `.env` files, database passwords, signing secrets, or production dumps.
- Apply schema changes through reviewed SQL migrations.
- Database errors are logged server-side; client responses use generic messages.

## HTTP response headers

The API currently sets `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, a restrictive `Referrer-Policy`, and a `Permissions-Policy` that disables camera, microphone and geolocation access. These are baseline protections, not a complete browser security policy. A production deployment still needs a reviewed Content Security Policy and HTTPS/HSTS at the trusted TLS edge.

## External market data

Yahoo Finance data is provided by the third-party `yfinance` library. Availability, latency and returned fields depend on the upstream service. Do not treat values as guaranteed real-time exchange data.

## Operational controls

Keep Redis private to the application network and configure authentication/TLS. Configure trusted proxies only for known ingress addresses. Configure log retention, access controls, backups, monitoring, alerting, restore tests, and rollback in the deployment platform.

## Deployment boundary

This is a portfolio market-data application, not a hardened trading platform. Before public deployment, complete account recovery, a refresh-token/session policy, CSP, HTTPS ingress, monitoring, and data-retention controls. Do not market indicators as investment advice.
