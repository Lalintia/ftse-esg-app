"""Singleton dependency providers for external service clients."""

import logging
from functools import lru_cache

from openai import AsyncOpenAI
from supabase import Client, create_client

from app.config import get_settings

logger = logging.getLogger(__name__)


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
