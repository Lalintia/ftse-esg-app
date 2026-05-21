"""Singleton dependency providers for external service clients."""

import logging
import secrets
from functools import lru_cache

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from openai import AsyncOpenAI
from supabase import Client, create_client

from app.config import get_settings

logger = logging.getLogger(__name__)

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Security(_api_key_header)) -> None:
    """Reject requests that don't carry a valid X-API-Key header.

    Skipped when API_KEY env var is not set (local dev without auth).
    """
    settings = get_settings()
    expected = settings.API_KEY
    if not expected:
        return
    if not api_key or not secrets.compare_digest(api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")


@lru_cache
def get_supabase() -> Client:
    """Return cached Supabase client singleton.

    Uses the service role key for full database access
    since this is an internal sales tool.

    Returns:
        Authenticated Supabase client.
    """
    settings = get_settings()
    logger.info("Initializing Supabase client")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


@lru_cache
def get_openai() -> AsyncOpenAI:
    """Return cached AsyncOpenAI client singleton.

    Returns:
        AsyncOpenAI client configured with API key.
    """
    settings = get_settings()
    logger.info("Initializing OpenAI client")
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
