"""FastAPI application entry point and lifecycle management."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler

from app.api.auth_controller import router as auth_router
from app.api.dashboard_controller import router as dashboard_router
from app.api.health_controller import router as health_router
from app.api.search_controller import router as search_router
from app.api.stock_controller import router as stock_router
from app.api.watchlist_controller import router as watchlist_router
from app.config import settings
from app.database.connection import close_connection_pool, create_connection_pool
from app.exceptions.exceptions_handlers import register_exception_handlers
from app.middleware.request_logger import RequestLoggingMiddleware
from app.rate_limiting import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create shared resources at startup and release them at shutdown."""
    create_connection_pool()
    try:
        yield
    finally:
        close_connection_pool()


app = FastAPI(
    title="Market Analyzer API",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(RequestLoggingMiddleware)
register_exception_handlers(app)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(watchlist_router)
app.include_router(dashboard_router)
app.include_router(search_router)
app.include_router(stock_router)
