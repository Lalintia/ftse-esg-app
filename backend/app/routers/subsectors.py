"""Subsector listing endpoint for the ICB dropdown."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.dependencies import get_supabase
from app.models.schemas import SubsectorItem

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Subsectors"])


@router.get("/subsectors", response_model=list[SubsectorItem])
async def list_subsectors(
    supabase: Client = Depends(get_supabase),
) -> list[SubsectorItem]:
    """List all ICB subsectors for the dropdown selector.

    Returns:
        List of subsectors with code, name, industry, and supersector.

    Raises:
        HTTPException: If the database query fails.
    """
    try:
        response = (
            supabase.table("icb_subsectors")
            .select("code, name, industry_name, supersector_name")
            .order("code")
            .execute()
        )
        return [SubsectorItem(**row) for row in response.data]
    except Exception as exc:
        logger.error("Failed to fetch subsectors: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to load subsectors from database",
        ) from exc
