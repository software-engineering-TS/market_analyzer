# Security

## Authentication

- Passwords are stored as bcrypt hashes; plaintext passwords must never be logged or persisted.
- JWT signing uses `JWT_SECRET_KEY` from the root environment file.
- Use a randomly generated secret of at least 32 characters and keep it out of source control.
- Access tokens currently use the configured `JWT_ALGORITHM` and an expiry in minutes.
- Protected endpoints use the bearer-token dependency.
- Login is limited to 5 attempts per client IP per minute; signup is limited to 5 attempts per client IP per hour. Excess requests receive HTTP 429 and rate-limit headers.
- Rate limits use the client socket address. Do not enable proxy-header trust unless the application is behind a trusted proxy that strips client-supplied forwarding headers.
- The in-memory rate-limit backend is for local development only and is not shared across processes. Production configuration must set `RATE_LIMIT_STORAGE_URI` to a private Redis endpoint (`redis://` or `rediss://`) so limits are shared across workers and instances.
- The profile endpoint returns only public fields (`id`, `username`, `email`, `created_at`); password hashes and internal account fields must not be returned.

## Database

- Use a dedicated PostgreSQL role with access only to the Market Analyzer database.
- Never commit `.env` files, database passwords, signing secrets, or production dumps.
- Apply schema changes through reviewed SQL migrations.
- Database errors are logged server-side; client responses use generic messages.

## HTTP response headers

The API middleware currently sets `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, a restrictive `Referrer-Policy`, and a `Permissions-Policy` that disables camera, microphone and geolocation access. These are baseline protections, not a complete browser security policy. A production deployment still needs a reviewed Content Security Policy and HTTPS/HSTS configuration at the trusted TLS-terminating edge.

## External market data

Yahoo Finance data is supplied by the third-party `yfinance` library. Availability, latency and returned fields depend on the upstream service. Do not treat values as guaranteed real-time exchange data.

## Operational controls

- Keep Redis private to the application network and configure authentication/TLS according to the hosting environment.
- Configure trusted proxy handling at the ASGI server or ingress only for known proxy addresses; never trust arbitrary `X-Forwarded-For` values.
- Terminate HTTPS at a trusted ingress and enable HSTS there after confirming every served domain is HTTPS-only. The API does not emit HSTS itself because TLS may be terminated upstream.
- Configure log retention, access controls, backups and monitoring in the deployment platform. Avoid logging credentials, authorization headers, request bodies or raw database exceptions.

## Deployment boundary

The project is a portfolio application, not a hardened financial trading platform. Before public multi-user deployment, complete account recovery, token revocation/refresh policy, a complete browser security policy, HTTPS termination, audit retention policy and operational monitoring. Never market its indicators as investment advice.
