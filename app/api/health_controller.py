"""Liveness and readiness probes for deployment platforms."""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.database.connection import get_connection, release_connection
from app.security.token_store import ping_token_store

router = APIRouter(tags=["Health"])


def _database_is_ready() -> bool:
    """Check database connectivity without changing persistent state."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        return cursor.fetchone() == (1,)
    except Exception:
        return False
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if connection is not None:
            release_connection(connection)


@router.get("/health/live", summary="Liveness probe")
def liveness():
    """Report that the API process is alive; do not depend on external services."""
    return {"status": "ok"}


@router.get("/health/ready", summary="Readiness probe")
def readiness():
    """Report whether required backing services are reachable."""
    components = {"database": _database_is_ready()}

    if settings.ENVIRONMENT.lower() == "production":
        components["session_store"] = ping_token_store()

    ready = all(components.values())
    return JSONResponse(
        status_code=status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "ok" if ready else "not_ready", "components": components},
    )
