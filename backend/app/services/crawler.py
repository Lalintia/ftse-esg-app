"""Playwright-based crawler for scraping company websites."""

import asyncio
import io
import logging
import re
import xml.etree.ElementTree as ET
from collections.abc import Callable
from dataclasses import dataclass, field as dataclass_field
from pathlib import PurePosixPath
from urllib.parse import urljoin, urlparse

import httpx
import pdfplumber
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

ESG_KEYWORDS: list[str] = [
    "sustainability",
    "sustainability-report",
    "esg",
    "csr",
    "governance",
    "environment",
    "climate",
    "safety",
    "human-rights",
    "annual-report",
    "supply-chain",
    "green",
    "carbon",
    "emission",
    "diversity",
    "ethics",
    "compliance",
    "risk-management",
    "stakeholder",
    "community",
    "biodiversity",
    "water",
    "waste",
    "pollution",
    "anti-corruption",
    "labor",
    "labour",
    "health",
    "report",
    "policy",
    "56-1",
    "one-report",
    "sd-report",
    "sustainable-development",
    "integrated-report",
    "investor-relations",
    "ir",
    "download",
    "publication",
    "document",
    "resources",
]

_HIGH_PRIORITY_KEYWORDS: list[str] = [
    "sustainability-report",
    "sustainability",
    "sd-report",
    "sustainable-development",
    "esg",
    "56-1",
    "one-report",
    "integrated-report",
    "annual-report",
    "investor-relations",
    "download",
    "report",
]

_PAGE_TIMEOUT_MS = 15_000
_MIN_CONTENT_LENGTH = 100
_SKIP_SCHEMES = {"javascript:", "mailto:", "tel:", "data:"}

_PDF_MAX_BYTES = 50 * 1024 * 1024  # 50 MB
_PDF_MAX_CHARS_PER_FILE = 200_000
_PDF_MAX_CHARS_TOTAL = 800_000
_PDF_MAX_FILES = 7
_PDF_DOWNLOAD_TIMEOUT = 120.0

_ESG_PDF_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"sustainability[_-]?report", re.IGNORECASE),
    re.compile(r"sd[_-]?report", re.IGNORECASE),
    re.compile(r"integrated[_-]?report", re.IGNORECASE),
    re.compile(r"annual[_-]?report", re.IGNORECASE),
    re.compile(r"56-1", re.IGNORECASE),
    re.compile(r"one[_-]?report", re.IGNORECASE),
    re.compile(r"corporate[_-]?governance", re.IGNORECASE),
    re.compile(r"cdp", re.IGNORECASE),
    re.compile(r"human[_-]?rights[_-]?policy", re.IGNORECASE),
    re.compile(r"supplier[_-]?code", re.IGNORECASE),
    re.compile(r"anti[_-]?corruption", re.IGNORECASE),
    re.compile(r"environment(al)?[_-]?policy", re.IGNORECASE),
    re.compile(r"health[_-]?(and[_-]?)?safety", re.IGNORECASE),
    re.compile(r"esg", re.IGNORECASE),
    re.compile(r"csr", re.IGNORECASE),
    re.compile(r"annex", re.IGNORECASE),
    re.compile(r"performance[_-]?indicator", re.IGNORECASE),
    re.compile(r"tcfd", re.IGNORECASE),
    re.compile(r"tu[_-]?performance", re.IGNORECASE),
]

_PDF_PRIORITY_MAP: dict[str, int] = {
    "sustainability": 100,
    "sd-report": 95,
    "sd_report": 95,
    "integrated-report": 85,
    "integrated_report": 85,
    "annual-report": 80,
    "annual_report": 80,
    "56-1": 80,
    "one-report": 80,
    "one_report": 80,
    "corporate-governance": 70,
    "corporate_governance": 70,
    "governance-report": 70,
    "cdp": 65,
    "climate-change": 60,
    "human-rights": 55,
    "human_rights": 55,
    "supplier-code": 50,
    "supply-chain": 50,
    "anti-corruption": 45,
    "anti_corruption": 45,
    "environmental-policy": 40,
    "environmental_policy": 40,
    "health-safety": 35,
    "health_safety": 35,
    "esg": 30,
    "csr": 30,
    "annex": 92,
    "performance": 88,
    "tcfd": 75,
}


@dataclass
class PageContent:
    """A single crawled page's content.

    Attributes:
        url: The page URL.
        title: The page title.
        markdown_text: The page content as markdown.
    """

    url: str
    title: str
    markdown_text: str


@dataclass
@dataclass
class PdfDownloadInfo:
    """Metadata about a downloaded PDF."""

    url: str
    filename: str
    method: str  # "httpx" or "playwright"
    chars_extracted: int
    pages_in_pdf: int


@dataclass
class CrawlResult:
    """Result of crawling a company website.

    Attributes:
        pages: List of crawled page contents.
        total_pages_found: Total pages discovered.
        pages_crawled: Number of pages actually scraped.
        pdf_downloads: Details of each PDF downloaded.
        html_pages_scraped: Number of HTML pages scraped.
    """

    pages: list[PageContent]
    total_pages_found: int
    pages_crawled: int
    pdf_downloads: list[PdfDownloadInfo] = dataclass_field(default_factory=list)
    html_pages_scraped: int = 0


def _get_domain(url: str) -> str:
    """Extract the domain from a URL.

    Args:
        url: Full URL string.

    Returns:
        Hostname string (e.g. 'www.example.com').
    """
    parsed = urlparse(url)
    return parsed.hostname or ""


def _is_valid_link(href: str, base_domain: str) -> bool:
    """Check if a link is valid for crawling.

    Filters out anchors, javascript/mailto/tel links,
    and links to different domains.

    Args:
        href: The href value from an anchor tag.
        base_domain: The domain of the website being crawled.

    Returns:
        True if the link should be followed.
    """
    if not href or href.startswith("#"):
        return False

    href_lower = href.lower().strip()
    if any(href_lower.startswith(scheme) for scheme in _SKIP_SCHEMES):
        return False

    parsed = urlparse(href)
    if parsed.hostname and parsed.hostname != base_domain:
        return False

    return True


def _is_esg_relevant(url: str) -> bool:
    """Check if a URL is likely ESG-relevant based on keywords.

    Also treats PDF links as ESG-relevant when they contain
    sustainability/report-related terms.

    Args:
        url: The URL to check.

    Returns:
        True if the URL contains ESG-related keywords.
    """
    url_lower = url.lower()
    if any(keyword in url_lower for keyword in ESG_KEYWORDS):
        return True
    if url_lower.endswith(".pdf"):
        pdf_hints = [
            "sustain", "esg", "csr", "annual", "report",
            "56-1", "governance", "environment", "social",
            "sd", "integrated",
        ]
        return any(hint in url_lower for hint in pdf_hints)
    return False


def _page_priority_score(url: str) -> int:
    """Score a URL for priority ranking (higher = more important).

    Args:
        url: The URL to rank.

    Returns:
        Priority score (0-10).
    """
    url_lower = url.lower()
    score = 0
    for keyword in _HIGH_PRIORITY_KEYWORDS:
        if keyword in url_lower:
            score += 3
    if url_lower.endswith(".pdf"):
        score += 1
    return score


def _select_pages(urls: list[str], max_pages: int) -> list[str]:
    """Select the most relevant pages to crawl.

    Prioritizes ESG-relevant URLs sorted by priority score,
    then fills with remaining pages up to the limit.

    Args:
        urls: All discovered URLs.
        max_pages: Maximum number of pages to select.

    Returns:
        Selected list of URLs to crawl.
    """
    if not urls:
        return []

    esg_urls = [u for u in urls if _is_esg_relevant(u)]
    other_urls = [u for u in urls if not _is_esg_relevant(u)]

    esg_urls.sort(key=_page_priority_score, reverse=True)

    selected = esg_urls[:max_pages]
    remaining_slots = max_pages - len(selected)

    if remaining_slots > 0:
        selected.extend(other_urls[:remaining_slots])

    return selected


def _deduplicate_urls(urls: list[str]) -> list[str]:
    """Remove duplicate URLs preserving order.

    Also normalizes trailing slashes for dedup.

    Args:
        urls: List of URLs.

    Returns:
        Deduplicated list.
    """
    seen: set[str] = set()
    result: list[str] = []
    for url in urls:
        normalized = url.rstrip("/")
        if normalized not in seen:
            seen.add(normalized)
            result.append(url)
    return result


async def _fetch_sitemap_urls(base_url: str) -> list[str]:
    """Try to fetch and parse /sitemap.xml for URL discovery.

    Args:
        base_url: The base website URL.

    Returns:
        List of URLs found in sitemap, or empty list if unavailable.
    """
    sitemap_url = urljoin(base_url.rstrip("/") + "/", "sitemap.xml")
    logger.info("Trying sitemap at %s", sitemap_url)

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(sitemap_url)
            if response.status_code != 200:
                logger.info("No sitemap found at %s (status %d)", sitemap_url, response.status_code)
                return []

            root = ET.fromstring(response.text)
            namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            urls = [
                loc.text.strip()
                for loc in root.findall(".//ns:loc", namespace)
                if loc.text and loc.text.strip()
            ]

            if not urls:
                urls = [
                    loc.text.strip()
                    for loc in root.findall(".//loc")
                    if loc.text and loc.text.strip()
                ]

            logger.info("Found %d URLs in sitemap", len(urls))
            return urls

    except Exception as exc:
        logger.info("Sitemap fetch failed: %s", exc)
        return []


async def _extract_links_from_page(
    page: "playwright.async_api.Page",
    base_url: str,
    base_domain: str,
) -> list[str]:
    """Extract all same-domain links from a page.

    Args:
        page: Playwright page instance.
        base_url: Base URL for resolving relative links.
        base_domain: Domain to filter same-domain links.

    Returns:
        List of absolute URLs found on the page.
    """
    try:
        hrefs = await page.eval_on_selector_all(
            "a[href]",
            "elements => elements.map(el => el.href)",
        )
    except Exception as exc:
        logger.warning("Failed to extract links: %s", exc)
        return []

    valid_links: list[str] = []
    for href in hrefs:
        if not isinstance(href, str):
            continue
        absolute_url = urljoin(base_url, href)
        if _is_valid_link(absolute_url, base_domain):
            valid_links.append(absolute_url.split("#")[0])

    return valid_links


async def _scrape_page(
    page: "playwright.async_api.Page",
    url: str,
) -> PageContent | None:
    """Navigate to a URL and extract text content.

    Args:
        page: Playwright page instance.
        url: URL to scrape.

    Returns:
        PageContent if successful, None if failed or content too short.
    """
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=_PAGE_TIMEOUT_MS)
    except Exception as exc:
        logger.warning("Failed to load %s: %s", url, exc)
        return None

    try:
        title = await page.title() or url
    except Exception:
        title = url

    try:
        body_text = await page.inner_text("body")
    except Exception as exc:
        logger.warning("Failed to extract text from %s: %s", url, exc)
        return None

    if not body_text or len(body_text.strip()) < _MIN_CONTENT_LENGTH:
        logger.warning("Skipping %s — content too short (%d chars)", url, len(body_text.strip()) if body_text else 0)
        return None

    markdown_text = f"# {title}\n\n{body_text.strip()}"

    logger.info("Scraped: %s (%d chars)", title, len(body_text))
    return PageContent(url=url, title=title, markdown_text=markdown_text)


def _is_esg_pdf(url: str) -> bool:
    """Check if a PDF URL matches ESG-relevant filename patterns.

    Args:
        url: The URL to check.

    Returns:
        True if the PDF filename matches ESG patterns.
    """
    if not url.lower().endswith(".pdf"):
        return False
    return any(pattern.search(url) for pattern in _ESG_PDF_PATTERNS)


def _pdf_priority_score(url: str) -> int:
    """Score a PDF URL for download priority (higher = more important).

    Args:
        url: The PDF URL.

    Returns:
        Priority score.
    """
    url_lower = url.lower()
    best_score = 0
    for keyword, score in _PDF_PRIORITY_MAP.items():
        if keyword in url_lower:
            best_score = max(best_score, score)
    return best_score


def _pdf_filename(url: str) -> str:
    """Extract filename from a PDF URL.

    Args:
        url: The PDF URL.

    Returns:
        Filename string.
    """
    path = PurePosixPath(urlparse(url).path)
    return path.name or "document.pdf"


async def _download_pdf_via_playwright(url: str) -> bytes | None:
    """Fallback PDF download using Playwright's API request context.

    Some websites block non-browser HTTP clients (returning 405/404).
    This uses Playwright's request API which sends real browser headers.
    """
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()

            response = await context.request.get(url, timeout=60000)
            if response.ok:
                pdf_bytes = await response.body()
                await browser.close()
                if pdf_bytes and len(pdf_bytes) > 100:
                    logger.info("Playwright API download succeeded for %s (%d bytes)", url, len(pdf_bytes))
                    return pdf_bytes

            logger.info("Playwright API download got status %d for %s", response.status, url)
            await browser.close()
    except Exception as exc:
        logger.warning("Playwright PDF download failed for %s: %s", url, exc)

    return None


async def _download_and_extract_pdf(
    url: str,
    max_chars: int = _PDF_MAX_CHARS_PER_FILE,
) -> tuple[PageContent | None, PdfDownloadInfo | None]:
    """Download a PDF and extract text content (all pages).

    Downloads the PDF via httpx first. If that fails (e.g. 404 from
    sites that block non-browser clients), falls back to Playwright
    headless browser download.

    Args:
        url: The PDF URL to download.
        max_chars: Maximum characters to extract from this PDF.

    Returns:
        Tuple of (PageContent, PdfDownloadInfo) or (None, None).
    """
    filename = _pdf_filename(url)
    logger.info("Downloading PDF: %s", filename)

    pdf_bytes: bytes | None = None
    download_method = "httpx"

    _browser_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/pdf,*/*",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        async with httpx.AsyncClient(
            timeout=_PDF_DOWNLOAD_TIMEOUT,
            follow_redirects=True,
            headers=_browser_headers,
        ) as client:
            response = await client.get(url)
            if response.status_code == 200:
                pdf_bytes = response.content
            else:
                logger.info(
                    "httpx download got status %d for %s — trying Playwright",
                    response.status_code,
                    filename,
                )

    except httpx.TimeoutException:
        logger.info("httpx timed out for %s — trying Playwright", filename)
    except Exception as exc:
        logger.info("httpx error for %s: %s — trying Playwright", filename, exc)

    if pdf_bytes is None:
        pdf_bytes = await _download_pdf_via_playwright(url)
        if pdf_bytes is not None:
            download_method = "playwright"

    if pdf_bytes is None:
        logger.warning("PDF download failed for %s (all methods)", filename)
        return None, None

    content_length = len(pdf_bytes)
    if content_length > _PDF_MAX_BYTES:
        logger.warning(
            "PDF too large: %s (%.1f MB) — skipping",
            filename,
            content_length / (1024 * 1024),
        )
        return None, None

    try:
        extracted_parts: list[str] = []
        total_chars = 0
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            total_pdf_pages = len(pdf.pages)
            logger.info(
                "PDF %s: %d pages total, reading all pages",
                filename,
                total_pdf_pages,
            )

            for i in range(total_pdf_pages):
                page_text = pdf.pages[i].extract_text()
                if page_text and page_text.strip():
                    part = f"--- Page {i + 1} ---\n{page_text.strip()}"
                    extracted_parts.append(part)
                    total_chars += len(part)
                    if total_chars >= max_chars:
                        logger.info(
                            "PDF %s: char limit reached at page %d/%d",
                            filename,
                            i + 1,
                            total_pdf_pages,
                        )
                        break

        if not extracted_parts:
            logger.warning("No text extracted from PDF: %s", filename)
            return None, None

        full_text = "\n\n".join(extracted_parts)

        if len(full_text) > max_chars:
            full_text = full_text[:max_chars]
            logger.info(
                "PDF text truncated to %d chars: %s",
                max_chars,
                filename,
            )

        markdown_text = f"# PDF: {filename}\n\n{full_text}"

        pages_read = len(extracted_parts)
        logger.info(
            "PDF extracted: %s (%d chars from %d/%d pages) via %s",
            filename,
            len(full_text),
            pages_read,
            total_pdf_pages,
            download_method,
        )

        page_content = PageContent(
            url=url,
            title=f"PDF: {filename}",
            markdown_text=markdown_text,
        )
        pdf_info = PdfDownloadInfo(
            url=url,
            filename=filename,
            method=download_method,
            chars_extracted=len(full_text),
            pages_in_pdf=total_pdf_pages,
        )
        return page_content, pdf_info

    except Exception as exc:
        logger.warning("PDF extraction error for %s: %s", filename, exc)
        return None, None


_REPORT_PAGE_PATHS: list[str] = [
    "/investor-relations",
    "/ir",
    "/sustainability",
    "/esg",
    "/downloads",
    "/reports",
    "/publications",
    "/governance",
    "/policies",
    "/resources",
    "/documents",
    "/investor-relations/reports",
    "/investor-relations/downloads",
    "/sustainability/reports",
    "/sustainability/downloads",
    "/esg/reports",
]


async def _discover_report_pdfs(
    page: "playwright.async_api.Page",
    base_url: str,
) -> list[str]:
    """Navigate to common report pages and discover ESG-relevant PDF links.

    Visits investor relations, sustainability, downloads, and governance
    pages to find PDFs that FTSE Russell typically reads (Sustainability
    Report, Annual Report, 56-1 One Report, policies, etc.).

    Args:
        page: Playwright page instance.
        base_url: The company website base URL.

    Returns:
        List of PDF URLs sorted by FTSE relevance priority.
    """
    base_domain = _get_domain(base_url)
    discovered_pdfs: set[str] = set()

    for path in _REPORT_PAGE_PATHS:
        target_url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
        try:
            response = await page.goto(
                target_url,
                wait_until="domcontentloaded",
                timeout=_PAGE_TIMEOUT_MS,
            )
            if response is None or response.status >= 400:
                continue

            pdf_links = await page.eval_on_selector_all(
                "a[href]",
                "elements => elements.map(el => el.href).filter(h => h.toLowerCase().endsWith('.pdf'))",
            )

            for link in pdf_links:
                if not isinstance(link, str):
                    continue
                absolute_url = urljoin(base_url, link)
                link_domain = _get_domain(absolute_url)
                if link_domain == base_domain or _is_esg_pdf(absolute_url):
                    discovered_pdfs.add(absolute_url)

            logger.info(
                "Report page %s: found %d PDF links",
                path,
                len(pdf_links),
            )

        except Exception as exc:
            logger.debug("Could not access %s: %s", target_url, exc)

    # Filter to ESG-relevant PDFs and sort by priority
    esg_pdfs = [url for url in discovered_pdfs if _is_esg_pdf(url)]
    other_pdfs = [url for url in discovered_pdfs if not _is_esg_pdf(url)]

    esg_pdfs.sort(key=_pdf_priority_score, reverse=True)

    all_pdfs = esg_pdfs + other_pdfs
    logger.info(
        "Discovered %d report PDFs (%d ESG-relevant)",
        len(all_pdfs),
        len(esg_pdfs),
    )
    return all_pdfs


async def crawl_website(
    url: str,
    max_pages: int = 20,
    on_progress: Callable[[str], None] | None = None,
) -> CrawlResult:
    """Crawl a company website and extract ESG-relevant content.

    Uses Playwright to discover and scrape pages. First tries
    sitemap.xml, then falls back to link extraction from homepage
    and subpages (2 levels deep).

    Args:
        url: The company website URL to crawl.
        max_pages: Maximum number of pages to crawl.
        on_progress: Optional callback for progress messages.

    Returns:
        CrawlResult with crawled page contents.

    Raises:
        RuntimeError: If crawling fails completely.
    """
    def _progress(msg: str) -> None:
        if on_progress:
            on_progress(msg)

    logger.info("Starting crawl for %s (max %d pages)", url, max_pages)
    _progress("Looking for sitemap.xml...")

    base_domain = _get_domain(url)
    all_urls: list[str] = []

    # Step 1: Try sitemap first
    sitemap_urls = await _fetch_sitemap_urls(url)
    if sitemap_urls:
        all_urls = sitemap_urls
        _progress(f"Found sitemap with {len(all_urls)} URLs")
        logger.info("Using %d URLs from sitemap", len(all_urls))

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            )
            page = await context.new_page()

            # Step 2: If no sitemap, crawl links from homepage + subpages
            if not all_urls:
                _progress("No sitemap found — crawling links from homepage...")
                logger.info("No sitemap — crawling links from homepage")

                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=_PAGE_TIMEOUT_MS)
                except Exception as exc:
                    logger.warning("Failed to load homepage %s: %s", url, exc)
                    raise RuntimeError(f"Cannot load homepage: {url}") from exc

                homepage_links = await _extract_links_from_page(page, url, base_domain)
                all_urls = [url] + homepage_links
                all_urls = _deduplicate_urls(all_urls)

                # Level 2: visit a few subpages to discover more links
                level2_candidates = [
                    u for u in homepage_links
                    if _is_esg_relevant(u) and not u.lower().endswith(".pdf")
                ][:5]

                for sub_url in level2_candidates:
                    try:
                        await page.goto(sub_url, wait_until="domcontentloaded", timeout=_PAGE_TIMEOUT_MS)
                        sub_links = await _extract_links_from_page(page, sub_url, base_domain)
                        all_urls.extend(sub_links)
                    except Exception as exc:
                        logger.warning("Failed level-2 crawl of %s: %s", sub_url, exc)

                all_urls = _deduplicate_urls(all_urls)

            total_pages_found = len(all_urls)
            logger.info("Discovered %d pages for %s", total_pages_found, url)

            # Step 3: Select ESG-relevant pages
            selected_urls = _select_pages(all_urls, max_pages)
            logger.info(
                "Selected %d pages to crawl (%d ESG-relevant)",
                len(selected_urls),
                sum(1 for u in selected_urls if _is_esg_relevant(u)),
            )

            # Step 4: Separate PDF and HTML URLs
            pdf_urls = [u for u in selected_urls if u.lower().endswith(".pdf")]
            html_urls = [u for u in selected_urls if not u.lower().endswith(".pdf")]

            # Also collect ESG PDFs from all discovered URLs (not just selected)
            all_esg_pdfs = [u for u in all_urls if _is_esg_pdf(u)]
            for pdf_url in all_esg_pdfs:
                if pdf_url not in pdf_urls:
                    pdf_urls.append(pdf_url)

            # Step 4b: Discover report PDFs from common report pages
            report_pdfs = await _discover_report_pdfs(page, url)
            for pdf_url in report_pdfs:
                if pdf_url not in pdf_urls:
                    pdf_urls.append(pdf_url)

            # Step 4c: Auto-discover annex + TCFD + policy PDFs
            # Find the latest year from sd-report PDFs and generate
            # annex/TCFD candidates for that year only
            sd_years: list[int] = []
            for pdf_url in list(pdf_urls):
                year_match = re.search(r"sd-report-(\d{4})", pdf_url, re.IGNORECASE)
                if year_match:
                    sd_years.append(int(year_match.group(1)))

            extra_candidates: list[str] = []
            if sd_years:
                latest_year = max(sd_years)
                parsed_base = urlparse(url)
                base = f"{parsed_base.scheme}://{parsed_base.netloc}"

                # Annex for latest year only
                annex_paths = [
                    f"{base}/files/download/sustainability/sd-report-{latest_year}-annex.pdf",
                ]
                # TCFD Report
                tcfd_paths = [
                    f"{base}/files/download/sustainability/TCFD-Report-{latest_year}.pdf",
                    f"{base}/files/download/sustainability/tu-tcfd-report-{latest_year}.pdf",
                ]
                # Common policy PDFs
                policy_paths = [
                    f"{base}/files/download/sustainability/SupplyChainProgressReport.pdf",
                    f"{base}/files/download/policy/TU-global-tax-policy.pdf",
                ]

                for candidate in annex_paths + tcfd_paths + policy_paths:
                    if candidate not in pdf_urls and candidate not in extra_candidates:
                        extra_candidates.append(candidate)
                        logger.info("Auto-discovered PDF candidate: %s", candidate)

            for extra_url in extra_candidates:
                pdf_urls.append(extra_url)

            # Remove older year duplicates — keep only latest year
            # for sd-report and annex (e.g. keep 2024, drop 2023)
            if sd_years:
                latest_year_str = str(max(sd_years))
                filtered_pdf_urls: list[str] = []
                for pdf_url in pdf_urls:
                    fname_lower = _pdf_filename(pdf_url).lower()
                    is_sd = "sd-report" in fname_lower
                    if is_sd:
                        if latest_year_str in fname_lower:
                            filtered_pdf_urls.append(pdf_url)
                        else:
                            logger.info("Dropping older PDF: %s (keeping %s only)", fname_lower, latest_year_str)
                    else:
                        filtered_pdf_urls.append(pdf_url)
                pdf_urls = filtered_pdf_urls

            # Dedup PDFs by filename (different URLs, same file)
            seen_filenames: set[str] = set()
            deduped_pdf_urls: list[str] = []
            for pdf_url in pdf_urls:
                fname = _pdf_filename(pdf_url).lower()
                if fname not in seen_filenames:
                    seen_filenames.add(fname)
                    deduped_pdf_urls.append(pdf_url)
                else:
                    logger.info("Dedup: skipping duplicate PDF %s", fname)
            pdf_urls = deduped_pdf_urls

            # Sort PDFs by priority and limit
            pdf_urls.sort(key=_pdf_priority_score, reverse=True)
            pdf_urls = pdf_urls[:_PDF_MAX_FILES]

            # Step 5: Scrape HTML pages
            pages: list[PageContent] = []
            for idx, page_url in enumerate(html_urls, 1):
                _progress(f"Scraping page {idx}/{len(html_urls)}...")
                result = await _scrape_page(page, page_url)
                if result:
                    pages.append(result)

            await context.close()

        finally:
            await browser.close()

    # Step 6: Download and extract PDFs
    pdf_download_infos: list[PdfDownloadInfo] = []

    if pdf_urls:
        _progress(f"Downloading {len(pdf_urls)} ESG PDF(s)...")
        logger.info(
            "Processing %d ESG PDF(s): %s",
            len(pdf_urls),
            [_pdf_filename(u) for u in pdf_urls],
        )

        pdf_total_chars = 0
        pdf_count = 0

        for pdf_url in pdf_urls:
            if pdf_total_chars >= _PDF_MAX_CHARS_TOTAL:
                logger.info("PDF total char limit reached — stopping PDF extraction")
                break

            _progress(f"Reading PDF: {_pdf_filename(pdf_url)} ({pdf_count + 1}/{len(pdf_urls)})")
            pdf_result, pdf_info = await _download_and_extract_pdf(pdf_url)
            if pdf_result and pdf_info:
                # Enforce total character budget
                remaining_budget = _PDF_MAX_CHARS_TOTAL - pdf_total_chars
                if len(pdf_result.markdown_text) > remaining_budget:
                    pdf_result = PageContent(
                        url=pdf_result.url,
                        title=pdf_result.title,
                        markdown_text=pdf_result.markdown_text[:remaining_budget],
                    )

                pages.append(pdf_result)
                pdf_download_infos.append(pdf_info)
                pdf_total_chars += len(pdf_result.markdown_text)
                pdf_count += 1

        logger.info(
            "PDF extraction complete: %d PDF(s) extracted (%d chars total)",
            pdf_count,
            pdf_total_chars,
        )

    if not pages:
        raise RuntimeError(f"Failed to crawl any pages from {url}")

    logger.info(
        "Crawl complete: %d pages scraped (including PDFs) out of %d discovered",
        len(pages),
        total_pages_found,
    )

    html_count = len(pages) - len(pdf_download_infos)

    return CrawlResult(
        pages=pages,
        total_pages_found=total_pages_found,
        pages_crawled=len(pages),
        pdf_downloads=pdf_download_infos,
        html_pages_scraped=html_count,
    )
