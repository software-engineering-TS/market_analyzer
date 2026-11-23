"""PostgreSQL connection-pool lifecycle."""

from psycopg2 import OperationalError, pool
from psycopg2.pool import PoolError

from app.config import settings
from app.exceptions.database_exceptions import DatabaseConnectionError
from app.logger import logger

connection_pool: pool.ThreadedConnectionPool | None = None


def create_connection_pool() -> None:
    """Initialize the shared PostgreSQL connection pool."""
    global connection_pool

    if connection_pool is not None and not connection_pool.closed:
        return

    try:
        connection_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
        )
        logger.info("PostgreSQL connection pool initialized.")
    except OperationalError as exc:
        logger.error("Failed to initialize PostgreSQL connection pool.")
        raise DatabaseConnectionError(
            "Unable to establish a database connection."
        ) from exc


def get_connection():
    """Borrow a connection or raise a typed availability error."""
    if connection_pool is None or connection_pool.closed:
        raise DatabaseConnectionError("Database connection pool is not initialized.")

    try:
        return connection_pool.getconn()
    except (PoolError, OperationalError) as exc:
        logger.error("Unable to borrow a PostgreSQL connection.")
        raise DatabaseConnectionError(
            "No database connection is currently available."
        ) from exc


def release_connection(connection) -> None:
    """Reset transaction state before returning a borrowed connection."""
    if connection is None:
        return

    if connection_pool is None or connection_pool.closed:
        connection.close()
        return

    discard_connection = bool(connection.closed)

    if not discard_connection:
        try:
            # psycopg2 starts transactions for ordinary SELECT statements too.
            # Always roll back any unfinished transaction so a connection is
            # returned idle, including after a failed query.
            connection.rollback()
        except Exception:
            logger.exception(
                "Unable to reset a PostgreSQL connection; discarding it."
            )
            connection.close()
            discard_connection = True

    try:
        connection_pool.putconn(connection, close=discard_connection)
    except PoolError:
        logger.exception("Unable to return a PostgreSQL connection to the pool.")
        connection.close()


def close_connection_pool() -> None:
    """Close all pooled connections during application shutdown."""
    global connection_pool

    if connection_pool is not None and not connection_pool.closed:
        connection_pool.closeall()
        logger.info("PostgreSQL connection pool closed.")

    connection_pool = None
