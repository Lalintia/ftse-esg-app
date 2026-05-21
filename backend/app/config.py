"""Application configuration loaded from environment variables."""

import logging
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent


class Settings(BaseSettings):
    """Application settings loaded from .env file.

    Attributes:
        SUPABASE_URL: Supabase project URL.
        SUPABASE_ANON_KEY: Supabase anonymous/public key.
        SUPABASE_SERVICE_ROLE_KEY: Supabase service role key for admin ops.
        OPENAI_API_KEY: OpenAI API key for GPT analysis.
        OPENAI_MODEL: OpenAI model to use for analysis.
        ALLOWED_ORIGINS: Comma-separated list of allowed CORS origins.
        MAX_PAGES_TO_CRAWL: Maximum HTML pages to crawl per analysis.
        MAX_PDFS_TO_READ: Maximum number of PDF files to download and extract.
        MAX_PDF_CHARS: Maximum characters to extract per PDF file.
        ANALYSIS_CONCURRENCY: Max concurrent AI analysis tasks.
    """

    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    OPENAI_API_KEY: str
    API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4.1-mini"
    ALLOWED_ORIGINS: str = "https://esg.ohmai.me,http://localhost:3000"
    MAX_PAGES_TO_CRAWL: int = 50
    MAX_PDFS_TO_READ: int = 5
    MAX_PDF_CHARS: int = 200_000
    ANALYSIS_CONCURRENCY: int = 2

    model_config = {
        "env_file": str(PROJECT_ROOT / ".env"),
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings singleton.

    Returns:
        Settings instance loaded from environment.
    """
    logger.info("Loading application settings")
    return Settings()
