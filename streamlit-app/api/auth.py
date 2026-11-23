from api.client import api_client


LOGIN_ENDPOINT = "/sma/v1/login"
SIGNUP_ENDPOINT = "/sma/v1/signup"
PROFILE_ENDPOINT = "/sma/v1/me"
LOGOUT_ENDPOINT = "/sma/v1/logout"


def login(username: str, password: str) -> dict:
    """Authenticate a user."""
    return api_client.post(LOGIN_ENDPOINT, {
        "user_name": username,
        "password": password,
    })


def signup(username: str, email: str, password: str) -> dict:
    """Register a user."""
    return api_client.post(SIGNUP_ENDPOINT, {
        "user_name": username,
        "email_id": email,
        "password": password,
    })


def get_current_user() -> dict:
    """Fetch the currently authenticated user's profile."""
    return api_client.get(PROFILE_ENDPOINT)


def logout() -> dict:
    """Revoke the current backend access token."""
    return api_client.post(LOGOUT_ENDPOINT)
