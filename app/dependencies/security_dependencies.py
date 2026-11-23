"""Authentication dependencies for protected API routes."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.dependencies.repository_dependencies import get_auth_repository
from app.exceptions.auth_exceptions import AuthenticationError
from app.repositories.auth_repository import AuthRepository
from app.security.jwt_handler import JWTService

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    repository: AuthRepository = Depends(get_auth_repository),
) -> dict:
    """Validate the bearer token and return only non-sensitive user fields."""
    if credentials is None:
        raise AuthenticationError("Authentication required.")

    payload = JWTService.verify_access_token(credentials.credentials)
    subject = payload.get("sub")

    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise AuthenticationError("Invalid access token.") from exc

    if user_id <= 0:
        raise AuthenticationError("Invalid access token.")

    user = repository.get_user_by_id(user_id)
    if user is None:
        raise AuthenticationError("User not found.")

    # Defense in depth: never allow a repository implementation to expose
    # password hashes or other internal columns through a route dependency.
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user.get("email"),
        "created_at": user.get("created_at"),
    }
