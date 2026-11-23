"""JWT creation and validation helpers."""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.config import settings
from app.exceptions.auth_exceptions import AuthenticationError
from app.logger import logger


class JWTService:
    """Create and verify short-lived bearer access tokens."""

    @staticmethod
    def create_access_token(data: dict[str, Any]) -> str:
        """Create a signed access token with explicit issue and expiry times."""
        payload = data.copy()
        now = datetime.now(timezone.utc)
        payload.update(
            {
                "iat": now,
                "exp": now + timedelta(
                    minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
                ),
            }
        )

        token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        logger.debug("JWT access token generated.")
        return token

    @staticmethod
    def verify_access_token(token: str) -> dict[str, Any]:
        """Decode a token and reject payloads missing required access claims."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )

            subject = payload.get("sub")
            issued_at = payload.get("iat")
            expires_at = payload.get("exp")

            if not isinstance(subject, str) or not subject.strip():
                raise JWTError("Token subject is missing.")

            if not isinstance(issued_at, (int, float)):
                raise JWTError("Token issue time is missing or invalid.")

            if not isinstance(expires_at, (int, float)):
                raise JWTError("Token expiry is missing or invalid.")

            if issued_at > datetime.now(timezone.utc).timestamp():
                raise JWTError("Token issue time is in the future.")

            return payload

        except (JWTError, TypeError, ValueError) as exc:
            logger.warning("JWT verification failed.")
            raise AuthenticationError(
                "Invalid or expired access token."
            ) from exc
