"""FastAPI application entry point for FTSE ESG Analyzer."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import get_supabase
from app.routers import analyses, health, subsectors
from app.utils.data_loader import load_ftse_indicators, load_ifrs_requirements, sync_indicator_names_to_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Preload reference data on startup and clean up on shutdown.

    Args:
        app: The FastAPI application instance.
    """
    logger.info("Starting FTSE ESG Analyzer — preloading data")
    indicators = load_ftse_indicators()
    requirements = load_ifrs_requirements()
    logger.info(
        "Preloaded %d FTSE indicators and %d IFRS requirements",
        len(indicators),
        len(requirements),
    )

    try:
        supabase = get_supabase()
        updated = sync_indicator_names_to_db(supabase)
        if updated:
            logger.info("Synced %d indicator names on startup", updated)
    except Exception as exc:
        logger.warning("Failed to sync indicator names: %s", exc)

    yield
    logger.info("Shutting down FTSE ESG Analyzer")


app = FastAPI(
    title="FTSE ESG Analyzer",
    description="Analyze company websites against FTSE Russell ESG and IFRS S1/S2 standards",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(subsectors.router, prefix="/api")
app.include_router(analyses.router, prefix="/api")


@app.get("/")
async def root() -> dict[str, str]:
    """Return application info at root endpoint.

    Returns:
        Dictionary with app name and version.
    """
    return {
        "app": "FTSE ESG Analyzer",
        "version": "1.0.0",
    }
