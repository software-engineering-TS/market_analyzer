"""Authentication repository: database operations only."""

from psycopg2.errors import UniqueViolation
from psycopg2.extras import RealDictCursor

from app.database.connection import get_connection, release_connection
from app.exceptions.auth_exceptions import UserAlreadyExistsError
from app.exceptions.database_exceptions import DatabaseOperationError
from app.logger import logger


class AuthRepository:
    def create_user(self, username: str, email: str, password_hash: str) -> dict:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO user_credentials (username, email, hash_password)
                    VALUES (%s, %s, %s)
                    RETURNING id, username, email, created_at;
                    """,
                    (username, email, password_hash),
                )
                user = cursor.fetchone()
                conn.commit()
                return user
        except UniqueViolation as exc:
            conn.rollback()
            raise UserAlreadyExistsError(
                "An account with that username or email already exists."
            ) from exc
        except Exception as exc:
            conn.rollback()
            logger.exception("Database error while creating user account.")
            raise DatabaseOperationError("Unable to create the user account.") from exc
        finally:
            release_connection(conn)

    def get_user_by_username(self, username: str) -> dict | None:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, username, email, hash_password
                    FROM user_credentials
                    WHERE username = %s;
                    """,
                    (username,),
                )
                return cursor.fetchone()
        except Exception as exc:
            logger.exception("Database error while retrieving user account.")
            raise DatabaseOperationError("Unable to retrieve the user account.") from exc
        finally:
            release_connection(conn)

    def save_login_audit(self, user_id: int, client_ip: str) -> dict:
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO users_login_info (user_id, ip_address, status)
                    VALUES (%s, %s, 'success')
                    RETURNING last_login;
                    """,
                    (user_id, client_ip),
                )
                login_info = cursor.fetchone()
                conn.commit()
                return login_info
        except Exception as exc:
            conn.rollback()
            logger.exception(
                "Database error while saving login audit | UserId=%s",
                user_id,
            )
            raise DatabaseOperationError(
                "Unable to save the login audit record."
            ) from exc
        finally:
            release_connection(conn)

    def get_user_by_id(self, user_id: int) -> dict | None:
        """Return public user fields only. Password hashes are never selected."""
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, username, email, created_at
                    FROM user_credentials
                    WHERE id = %s;
                    """,
                    (user_id,),
                )
                return cursor.fetchone()
        except Exception as exc:
            logger.exception(
                "Database error while retrieving user profile | UserId=%s",
                user_id,
            )
            raise DatabaseOperationError(
                "Unable to retrieve the user profile."
            ) from exc
        finally:
            release_connection(conn)
