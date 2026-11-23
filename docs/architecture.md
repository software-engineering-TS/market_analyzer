# Architecture

## Components

- **Streamlit frontend** (`streamlit-app/`): user interface, authentication state, dashboard, search, stock detail pages and watchlists.
- **FastAPI application** (`app/main.py`): HTTP routing, request logging, lifecycle management and exception handling.
- **Services** (`app/services/`): authentication, stock analysis, dashboard aggregation, search and watchlist business logic.
- **Repositories** (`app/repositories/`): parameterized PostgreSQL queries.
- **Providers** (`app/providers/`): Yahoo Finance market data and news integration.
- **PostgreSQL**: account credentials, login audit, master stock data and user watchlists.

## Request flow

1. Streamlit calls the FastAPI API through its shared API client.
2. FastAPI validates request models and, for protected endpoints, validates a JWT bearer token.
3. Controllers delegate to services.
4. Services coordinate repositories and external providers.
5. Repositories access PostgreSQL through the shared threaded connection pool.
6. Responses are serialized using Pydantic models and the common response builders.

## Data model

- `user_credentials`: user identity, unique username/email and bcrypt password hash.
- `users_login_info`: successful login audit entries associated with a user.
- `stocks`: NSE/BSE stock master data and active status.
- `watchlist`: a user's selected symbols, unique per user/symbol pair.

The canonical initial schema is `app/database/schema.sql`.

## Technical indicators

The indicator calculator is a pure transformation over historical closing-price data. The stock service validates period/interval inputs and fetches the requested history once before calculating SMA, EMA, RSI, MACD and Bollinger Bands.

## External dependencies

The application relies on PostgreSQL and Yahoo Finance through `yfinance`. External market data can be delayed, incomplete or temporarily unavailable; the API should return a clear service-unavailable response rather than presenting missing values as valid market data.
