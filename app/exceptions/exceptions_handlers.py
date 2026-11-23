"""Register safe, consistent API exception handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.auth_exceptions import AuthenticationError, UserAlreadyExistsError
from app.exceptions.business_exceptions import (
    MarketDataUnavailableException,
    ResourceNotFoundException,
)
from app.exceptions.watchlist_exceptions import (
    WatchlistAlreadyExistsError,
    WatchlistNotFoundError,
)
from app.exceptions.database_exceptions import (
    DatabaseConnectionError,
    DatabaseOperationError,
)
from app.logger import logger
from app.utils.response_builders import error


def register_exception_handlers(app: FastAPI) -> None:
    """Register application-specific and fallback exception handlers."""

    @app.exception_handler(AuthenticationError)
    async def authentication_exception_handler(request: Request, exc: AuthenticationError):
        logger.warning("Authentication failed | Path=%s", request.url.path)
        return JSONResponse(status_code=401, content=error(message=str(exc)))

    @app.exception_handler(UserAlreadyExistsError)
    async def user_exists_exception_handler(request: Request, exc: UserAlreadyExistsError):
        logger.warning("User registration conflict | Path=%s", request.url.path)
        return JSONResponse(
            status_code=409,
            content=error(message="An account with that username or email already exists."),
        )

    @app.exception_handler(WatchlistAlreadyExistsError)
    async def watchlist_conflict_handler(request: Request, exc: WatchlistAlreadyExistsError):
        return JSONResponse(status_code=409, content=error(message=str(exc)))

    @app.exception_handler(WatchlistNotFoundError)
    async def watchlist_not_found_handler(request: Request, exc: WatchlistNotFoundError):
        return JSONResponse(status_code=404, content=error(message=str(exc)))

    @app.exception_handler(ResourceNotFoundException)
    async def resource_not_found_handler(request: Request, exc: ResourceNotFoundException):
        return JSONResponse(status_code=404, content=error(message=str(exc)))

    @app.exception_handler(MarketDataUnavailableException)
    async def market_data_unavailable_handler(request: Request, exc: MarketDataUnavailableException):
        logger.warning("Market data unavailable | Path=%s", request.url.path)
        return JSONResponse(
            status_code=503,
            content=error(message="Market data is temporarily unavailable. Please try again."),
        )

    @app.exception_handler(DatabaseConnectionError)
    async def database_connection_handler(request: Request, exc: DatabaseConnectionError):
        logger.error("Database unavailable | Path=%s", request.url.path)
        return JSONResponse(
            status_code=503,
            content=error(message="The database service is currently unavailable."),
        )

    @app.exception_handler(DatabaseOperationError)
    async def database_operation_handler(request: Request, exc: DatabaseOperationError):
        logger.error("Database operation failed | Path=%s", request.url.path)
        return JSONResponse(
            status_code=500,
            content=error(message="The database operation could not be completed."),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(
            "Unhandled application error | Path=%s | ErrorType=%s",
            request.url.path,
            type(exc).__name__,
        )
        return JSONResponse(
            status_code=500,
            content=error(message="An unexpected error occurred. Please try again."),
        )
