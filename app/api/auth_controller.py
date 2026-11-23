"""Authentication endpoints."""

from fastapi import APIRouter, Depends, Request, Response, status

from app.dependencies.auth_dependencies import get_auth_service
from app.dependencies.security_dependencies import get_current_user
from app.models.request_models import LoginRequest, SignupRequest
from app.models.response_models import ApiResponse
from app.services.auth_service import AuthService
from app.utils.response_builders import success
from app.rate_limiting import limiter

router = APIRouter(prefix="/sma/v1", tags=["Authentication"])


@router.post(
    "/signup",
    summary="Register User",
    description="Create a new user account.",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/hour")
async def signup(
    credentials: SignupRequest,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Register a new application user."""
    return auth_service.signup(credentials)


@router.post(
    "/login",
    summary="Authenticate User",
    description="Authenticate a registered user using username and password.",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("5/minute")
async def login(
    credentials: LoginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Authenticate an application user."""
    client_ip = request.client.host if request.client else "Unknown"
    return auth_service.login(credentials, client_ip)


@router.get(
    "/me",
    summary="Get current profile",
    description="Return the authenticated user's public profile.",
    response_model=ApiResponse,
)
def get_profile(current_user: dict = Depends(get_current_user)):
    """Return a non-sensitive profile payload."""
    return success(
        message="Profile fetched successfully.",
        data=current_user,
    )
