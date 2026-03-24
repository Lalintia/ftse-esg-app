"""Health check endpoint."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return application health status.

    Returns:
        Dictionary with status and current timestamp.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }
