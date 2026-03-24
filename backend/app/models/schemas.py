"""Pydantic models for API request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class AnalysisRequest(BaseModel):
    """Request body to start a new ESG analysis.

    Attributes:
        company_url: The company website URL to crawl and analyze.
        subsector_code: ICB subsector code (e.g. "10101010").
    """

    company_url: HttpUrl
    subsector_code: str = Field(
        ...,
        min_length=4,
        max_length=10,
        description="ICB subsector code",
    )


class AnalysisCreateResponse(BaseModel):
    """Response after creating a new analysis.

    Attributes:
        analysis_id: UUID of the created analysis.
        status: Initial status (always 'pending').
        message: Human-readable status message.
    """

    analysis_id: str
    status: str
    message: str


class AnalysisResponse(BaseModel):
    """Summary response after creating or listing an analysis.

    Attributes:
        id: Unique analysis identifier.
        status: Current analysis status.
        company_url: The analyzed company URL.
        company_name: Detected company name (if available).
        overall_score: Overall ESG score (0.0-5.0).
        pages_crawled: Number of pages crawled.
        created_at: Timestamp when analysis was created.
    """

    id: UUID
    status: str
    company_url: str
    company_name: str | None = None
    overall_score: float | None = None
    pages_crawled: int = 0
    created_at: datetime


class FtseResultItem(BaseModel):
    """Single FTSE indicator result within an analysis.

    Attributes:
        indicator_code: FTSE indicator code (e.g. "EBD02").
        status: Whether evidence was found/partial/missing.
        score: Numeric score for this indicator.
        evidence: Extracted evidence text from the website.
        confidence: AI confidence level (0.0-1.0).
    """

    indicator_code: str
    status: str = Field(..., pattern="^(found|partial|missing)$")
    score: float | None = None
    evidence: str | None = None
    confidence: float | None = Field(None, ge=0.0, le=1.0)


class IfrsResultItem(BaseModel):
    """Single IFRS requirement result within an analysis.

    Attributes:
        requirement_id: UUID of the IFRS requirement.
        status: Whether evidence was found/partial/missing.
        evidence: Extracted evidence text from the website.
        confidence: AI confidence level (0.0-1.0).
    """

    requirement_id: UUID
    status: str = Field(..., pattern="^(found|partial|missing)$")
    evidence: str | None = None
    confidence: float | None = Field(None, ge=0.0, le=1.0)


class SitemapItem(BaseModel):
    """Recommended page for the company sitemap.

    Attributes:
        page_title: Suggested page title.
        page_path: Suggested URL path.
        reason: Why this page is recommended.
        priority: Priority level (high/medium/low).
    """

    page_title: str
    page_path: str | None = None
    reason: str
    priority: str = Field("medium", pattern="^(high|medium|low)$")


class ThemeSummary(BaseModel):
    """Aggregated score summary per FTSE theme.

    Attributes:
        theme_name: Name of the FTSE theme.
        pillar: E/S/G pillar this theme belongs to.
        total: Total number of applicable indicators.
        found: Number of indicators with status "found".
        partial: Number of indicators with status "partial".
        missing: Number of indicators with status "missing".
        score: Calculated theme score (0.0-5.0).
    """

    theme_name: str
    pillar: str = Field(..., pattern="^(Environmental|Social|Governance)$")
    total: int = Field(..., ge=0)
    found: int = Field(..., ge=0)
    partial: int = Field(..., ge=0)
    missing: int = Field(..., ge=0)
    score: float = Field(..., ge=0.0, le=5.0)


class AnalysisDetail(BaseModel):
    """Full analysis detail including all scores and results.

    Attributes:
        id: Unique analysis identifier.
        status: Current analysis status.
        company_url: The analyzed company URL.
        company_name: Detected company name.
        subsector_code: ICB subsector code used.
        overall_score: Overall ESG score (0.0-5.0).
        environmental_score: Environmental pillar score.
        social_score: Social pillar score.
        governance_score: Governance pillar score.
        ifrs_s1_score: IFRS S1 compliance percentage.
        ifrs_s2_score: IFRS S2 compliance percentage.
        pages_crawled: Number of pages crawled.
        theme_summaries: Per-theme score breakdown.
        ftse_results: Individual FTSE indicator results.
        ifrs_results: Individual IFRS requirement results.
        sitemap: Recommended sitemap pages.
        error_message: Error description if analysis failed.
        started_at: When analysis processing began.
        completed_at: When analysis processing finished.
        created_at: When analysis was created.
    """

    id: UUID
    status: str
    company_url: str
    company_name: str | None = None
    subsector_code: str | None = None
    overall_score: float | None = None
    environmental_score: float | None = None
    social_score: float | None = None
    governance_score: float | None = None
    ifrs_s1_score: float | None = None
    ifrs_s2_score: float | None = None
    pages_crawled: int = 0
    theme_summaries: list[ThemeSummary] = Field(default_factory=list)
    ftse_results: list[FtseResultItem] = Field(default_factory=list)
    ifrs_results: list[IfrsResultItem] = Field(default_factory=list)
    sitemap: list[SitemapItem] = Field(default_factory=list)
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime


class SubsectorItem(BaseModel):
    """ICB subsector for dropdown selection.

    Attributes:
        code: ICB subsector code.
        name: Subsector name.
        industry_name: Parent industry name.
        supersector_name: Parent supersector name.
    """

    code: str
    name: str
    industry_name: str
    supersector_name: str
