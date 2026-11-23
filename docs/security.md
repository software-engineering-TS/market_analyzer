# Security

## Authentication

- Passwords are stored as bcrypt hashes; plaintext passwords must never be logged or persisted.
- JWT signing uses `JWT_SECRET_KEY` from the root environment file.
- Use a randomly generated secret of at least 32 characters and keep it out of source control.
- Access tokens currently use the configured `JWT_ALGORITHM` and an expiry in minutes.
- Protected endpoints use the bearer-token dependency.
- The profile endpoint returns only public fields (`id`, `username`, `email`, `created_at`); password hashes and internal account fields must not be returned.

## Database

- Use a dedicated PostgreSQL role with access only to the Market Analyzer database.
- Never commit `.env` files, database passwords, signing secrets, or production dumps.
- Apply schema changes through reviewed SQL migrations.
- Database errors are logged server-side; client responses use generic messages.

## External market data

Yahoo Finance data is supplied by the third-party `yfinance` library. Availability, latency and returned fields depend on the upstream service. Do not treat values as guaranteed real-time exchange data.

## Deployment boundary

The project is a portfolio application, not a hardened financial trading platform. Before public multi-user deployment, add rate limiting, account recovery, token revocation/refresh policy, security headers, HTTPS termination, audit retention policy and operational monitoring. Never market its indicators as investment advice.
