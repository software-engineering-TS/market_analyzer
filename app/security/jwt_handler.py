"""JWT creation and validation helpers."""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt

from app.config import settings
from app.exceptions.auth_exceptions import AuthenticationError
from app.logger import logger
from app.security.token_store import is_token_id_revoked, revoke_token_id


class JWTService:
    """Create, verify, and revoke short-lived bearer access tokens."""

    @staticmethod
    def create_access_token(data: dict[str, Any]) -> str:
        """Create a signed access token with a unique ID and explicit timestamps."""
        payload = data.copy()
        now = datetime.now(timezone.utc)
        payload.update({
            "jti": str(uuid4()),
            "iat": now,
            "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        })
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    @staticmethod
    def verify_access_token(token: str) -> dict[str, Any]:
        """Decode a token and reject invalid, expired, or revoked access claims."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            subject = payload.get("sub")
            issued_at = payload.get("iat")
            expires_at = payload.get("exp")
            token_id = payload.get("jti")

            if not isinstance(subject, str) or not subject.strip():
                raise jwt.InvalidTokenError("Token subject is missing.")
            if not isinstance(issued_at, (int, float)):
                raise jwt.InvalidTokenError("Token issue time is missing or invalid.")
            if not isinstance(expires_at, (int, float)):
                raise jwt.InvalidTokenError("Token expiry is missing or invalid.")
            if not isinstance(token_id, str) or not token_id.strip():
                raise jwt.InvalidTokenError("Token ID is missing or invalid.")
            if issued_at > datetime.now(timezone.utc).timestamp():
                raise jwt.InvalidTokenError("Token issue time is in the future.")
            if is_token_id_revoked(token_id):
                raise jwt.InvalidTokenError("Token has been revoked.")
            return payload
        except (jwt.InvalidTokenError, TypeError, ValueError) as exc:
            logger.warning("JWT verification failed.")
            raise AuthenticationError("Invalid or expired access token.") from exc

    @staticmethod
    def revoke_access_token(token: str) -> None:
        """Revoke a previously verified access token until its expiry."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            token_id = payload.get("jti")
            expires_at = payload.get("exp")
            if not isinstance(token_id, str) or not token_id.strip():
                raise jwt.InvalidTokenError("Token ID is missing or invalid.")
            if not isinstance(expires_at, (int, float)):
                raise jwt.InvalidTokenError("Token expiry is missing or invalid.")
            revoke_token_id(token_id, expires_at)
        except (jwt.InvalidTokenError, TypeError, ValueError) as exc:
            raise AuthenticationError("Invalid or expired access token.") from exc
