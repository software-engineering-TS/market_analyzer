# Market Analyzer

A full-stack market-data analytics application built with **FastAPI**, **PostgreSQL**, **Streamlit** and **Yahoo Finance via yfinance**. Users can register, explore listed companies, review historical prices and technical indicators, and maintain personal watchlists.

> Market data is provided by a third-party service and may be delayed, incomplete or unavailable. This application is an engineering and learning project, not investment advice or a trading platform.

## Features

- JWT-based registration, login and protected profile access
- Market overview dashboard
- Search of the local stock master
- Company and quote details
- Historical OHLC price data
- SMA, EMA, RSI, MACD and Bollinger Bands
- Per-user stock watchlists
- Related market news
- PostgreSQL persistence and API documentation

## Architecture

- **Frontend:** Streamlit (streamlit-app/)
- **API:** FastAPI (app/main.py)
- **Business logic:** service layer (app/services/)
- **Persistence:** repositories using psycopg2 (app/repositories/)
- **External data:** Yahoo Finance provider (app/providers/)
- **Database:** PostgreSQL; canonical initial schema at app/database/schema.sql

## Technology

| Layer | Technologies |
|---|---|
| Backend | Python 3.12, FastAPI, Pydantic |
| Frontend | Streamlit, Plotly |
| Database | PostgreSQL, psycopg2 |
| Authentication | bcrypt, JWT |
| Market data | yfinance, Pandas, NumPy |
| Testing | pytest, FastAPI TestClient |
| CI | GitHub Actions |

## Screenshots

### Landing and dashboard

<p align="center">
  <img src="streamlit-app/assets/images/landing_page.png" width="800" alt="Market Analyzer landing page">
</p>
<p align="center">
  <img src="streamlit-app/assets/images/dashboard_full.png" width="800" alt="Market Analyzer dashboard">
</p>

### Search and stock analytics

<p align="center">
  <img src="streamlit-app/assets/images/searchbox_with_output.png" width="800" alt="Stock search results">
  <br><br>
  <img src="streamlit-app/assets/images/stock_details_1.png" width="800" alt="Stock overview">
  <br><br>
  <img src="streamlit-app/assets/images/stock_details_2.png" width="800" alt="Historical stock chart">
</p>

### Watchlist

<p align="center">
  <img src="streamlit-app/assets/images/watchlist.png" width="800" alt="Personal stock watchlist">
</p>

## Project structure

    app/
      api/                 FastAPI controllers
      database/            PostgreSQL connection pool and schema
      dependencies/        FastAPI dependency injection
      exceptions/          Typed domain and application errors
      middleware/          Request logging
      models/              Request and response models
      providers/           Yahoo Finance and news integrations
      repositories/        PostgreSQL data access
      security/             Password hashing and JWT helpers
      services/             Application business logic
      utils/                Indicators and response utilities
    streamlit-app/
      api/                  Backend API client functions
      components/           Reusable UI components
      screens/              Application screens
      assets/               Documentation screenshots and styles
    scripts/                Stock master CSV import
    tests/                  Unit and optional PostgreSQL integration tests
    docs/                   Architecture, security and test guides

## Local setup

### 1. Prerequisites

- Python 3.12
- PostgreSQL 16 (or a compatible supported PostgreSQL release)
- Git

### 2. Clone and install

    git clone https://github.com/software-engineering-TS/market_analyzer.git
    cd market_analyzer

    python -m venv .venv
    # Windows CMD: .venv\Scripts\activate
    # PowerShell: .\.venv\Scripts\Activate.ps1

    python -m pip install --upgrade pip
    python -m pip install -r requirements-dev.txt
    python -m pip install -r streamlit-app/requirements.txt

### 3. Configure environment

Copy .env.example to .env. Set your local PostgreSQL connection values and create a random JWT_SECRET_KEY of at least 32 characters. Never commit the populated .env.

Copy streamlit-app/.env.example to streamlit-app/.env when the frontend needs a custom API URL.

### 4. Initialize the database

Create the database and dedicated role corresponding to your .env, then apply the schema:

    psql -h 127.0.0.1 -U market_analyzer -d market_analyzer -f app/database/schema.sql

Load the supplied NSE equity master list:

    python -m scripts.load_master_stocks

### 5. Run the application

Terminal 1 — from the repository root:

    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Terminal 2:

    cd streamlit-app
    streamlit run app.py

- Streamlit UI: http://localhost:8501
- FastAPI docs: http://127.0.0.1:8000/docs

## Tests

Run the unit test suite:

    python -m pytest -q

The PostgreSQL schema smoke test is enabled when TEST_DATABASE_URL points to a disposable test database. GitHub Actions starts PostgreSQL and runs it automatically.

See docs/testing.md for full instructions.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /sma/v1/signup | Register |
| POST | /sma/v1/login | Authenticate |
| GET | /sma/v1/me | Current user profile |
| GET | /sma/v1/dashboard | Dashboard |
| GET | /sma/v1/search | Search stock master |
| GET | /sma/v1/stocks/{symbol} | Stock details |
| GET | /sma/v1/{symbol}/history | Historical prices |
| GET | /sma/v1/{symbol}/indicators | Technical indicators |
| GET | /watchlist | Current user's watchlist |
| POST | /watchlist/add | Add a symbol |
| DELETE | /watchlist/remove/{symbol} | Remove a symbol |

Protected routes require an Authorization: Bearer access-token header.

## Security and limitations

See docs/security.md. The application uses third-party market data and should not be used as a source of guaranteed real-time prices or investment recommendations. Before public multi-user deployment, add rate limiting, account recovery, token revocation policy, HTTPS, security headers, operational monitoring and a formal data-retention policy.

## License

MIT
