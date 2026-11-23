"""Watchlist repository: user-scoped PostgreSQL operations."""

from psycopg2.errors import ForeignKeyViolation, UniqueViolation
from psycopg2.extras import RealDictCursor

from app.database.connection import get_connection, release_connection
from app.exceptions.business_exceptions import ResourceNotFoundException
from app.exceptions.database_exceptions import DatabaseOperationError
from app.exceptions.watchlist_exceptions import WatchlistAlreadyExistsError
from app.logger import logger


class WatchlistRepository:
    def add_watchlist(self, user_id: int, symbol: str) -> dict:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO watchlist (user_id, symbol)
                    VALUES (%s, %s)
                    RETURNING id, user_id, symbol, created_at;
                    """,
                    (user_id, symbol),
                )
                row = cursor.fetchone()
                conn.commit()
                return row
        except UniqueViolation as exc:
            conn.rollback()
            raise WatchlistAlreadyExistsError(
                f"'{symbol}' is already in your watchlist."
            ) from exc
        except ForeignKeyViolation as exc:
            conn.rollback()
            raise ResourceNotFoundException(
                f"Stock '{symbol}' is not present in the stock master."
            ) from exc
        except Exception as exc:
            conn.rollback()
            logger.exception(
                "Database error while adding watchlist."
            )
            raise DatabaseOperationError("Unable to add the watchlist item.") from exc
        finally:
            release_connection(conn)

    def get_watchlist(self, user_id: int) -> list[dict]:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, symbol, created_at
                    FROM watchlist
                    WHERE user_id = %s
                    ORDER BY created_at DESC;
                    """,
                    (user_id,),
                )
                return cursor.fetchall()
        except Exception as exc:
            logger.exception(
                "Database error while retrieving watchlist."
            )
            raise DatabaseOperationError("Unable to retrieve the watchlist.") from exc
        finally:
            release_connection(conn)

    def remove_watchlist(self, user_id: int, symbol: str) -> bool:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM watchlist
                    WHERE user_id = %s AND symbol = %s;
                    """,
                    (user_id, symbol),
                )
                deleted = cursor.rowcount > 0
                conn.commit()
                return deleted
        except Exception as exc:
            conn.rollback()
            logger.exception(
                "Database error while deleting watchlist."
            )
            raise DatabaseOperationError("Unable to remove the watchlist item.") from exc
        finally:
            release_connection(conn)
