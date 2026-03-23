"""Grant posting scraper - fetch and parse grant listings from URLs."""

from __future__ import annotations

import re

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel


class GrantPostingData(BaseModel):
    """Scraped grant posting data."""

    title: str
    organization: str
    program: str | None = None
    description: str
    eligibility_text: str = ""
    amount_range: str | None = None
    deadline: str | None = None
    source_url: str


def clean_description(text: str) -> str:
    """Strip HTML tags and normalize whitespace."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_funding_amount(text: str) -> str | None:
    """Extract funding amount from grant text.

    Recognises patterns like "up to $500,000", "$100k to $500k",
    "$2 million", "maximum of $250,000", and bare dollar ranges.
    """
    patterns = [
        r"up\s+to\s+\$[\d,]+(?:\s*(?:million|billion|M|B))?",
        r"maximum\s+(?:of\s+)?\$[\d,]+(?:\s*(?:million|billion|M|B))?",
        r"\$[\d,]+(?:\s*(?:million|billion|M|B))?\s*(?:to|-)\s*\$[\d,]+(?:\s*(?:million|billion|M|B))?",
        r"\$[\d,]+(?:\s*(?:million|billion|M|B))",
        r"[\d,]+k\s*(?:to|-)\s*[\d,]+k",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group().strip()
    return None


def extract_deadline(text: str) -> str | None:
    """Extract application deadline from grant text.

    Recognises labelled deadlines, "applications due DATE", rolling basis,
    and ISO / long-form date patterns.
    """
    # Rolling / open basis takes priority as a special case
    if re.search(r"rolling\s+(?:basis|deadline|review|applications?)", text, re.IGNORECASE):
        return "Rolling"

    labelled_patterns = [
        r"(?:deadline|due\s+date|closing\s+date|apply\s+by)[:\s]+([A-Za-z0-9 ,/\-]+)",
        r"applications?\s+(?:are\s+)?due\s+(?:by\s+)?([A-Za-z0-9 ,/\-]+)",
        r"submit\s+by\s+([A-Za-z0-9 ,/\-]+)",
    ]
    for pattern in labelled_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip().rstrip(".")
            # Trim to a reasonable length to avoid capturing run-on sentences
            if len(candidate) <= 40:
                return candidate

    # Bare ISO date: 2026-06-30
    iso = re.search(r"\b(20\d{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01]))\b", text)
    if iso:
        return iso.group(1)

    # Long-form date: June 30, 2026 / 30 June 2026
    long_form = re.search(
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)"
        r"\s+\d{1,2},?\s+20\d{2}\b",
        text,
        re.IGNORECASE,
    )
    if long_form:
        return long_form.group().strip()

    return None


def extract_eligibility(soup: BeautifulSoup) -> str:
    """Extract eligibility section text from grant page.

    Looks for headings containing eligibility-related keywords and returns
    the text of the following sibling elements until the next heading.
    Falls back to any element whose class/id contains eligibility keywords.
    """
    eligibility_keywords = re.compile(
        r"eligib|who\s+can\s+apply|requirements?|criteria", re.IGNORECASE
    )

    # Search for a heading that introduces an eligibility section
    for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
        if eligibility_keywords.search(heading.get_text()):
            parts: list[str] = []
            for sibling in heading.find_next_siblings():
                if sibling.name in {"h1", "h2", "h3", "h4"}:
                    break
                text = sibling.get_text(separator=" ", strip=True)
                if text:
                    parts.append(text)
            if parts:
                return clean_description(" ".join(parts))[:2000]

    # Fallback: element with a matching class or id attribute
    candidate = soup.find(
        class_=eligibility_keywords
    ) or soup.find(id=eligibility_keywords)
    if candidate:
        return clean_description(candidate.get_text(separator=" ", strip=True))[:2000]

    return ""


def extract_organization(soup: BeautifulSoup) -> str:
    """Extract funding organization name from grant page.

    Tries Open Graph site_name, then common header/meta patterns,
    then falls back to the page <title>.
    """
    og_site = soup.find("meta", {"property": "og:site_name"})
    if og_site and og_site.get("content"):
        return og_site["content"].strip()

    meta_author = soup.find("meta", {"name": re.compile(r"author|publisher|organization", re.I)})
    if meta_author and meta_author.get("content"):
        return meta_author["content"].strip()

    # Look for an element whose class/id suggests it holds the org/site name
    org_elem = soup.find(class_=re.compile(r"org|funder|agency|brand|logo-text|site-name", re.I))
    if org_elem:
        text = org_elem.get_text(strip=True)
        if text:
            return text[:100]

    title_tag = soup.find("title")
    if title_tag:
        # Many sites use "Page Title | Organisation Name" — take the last segment
        parts = re.split(r"[|\-–—]", title_tag.get_text())
        if len(parts) > 1:
            return parts[-1].strip()[:100]

    return "Unknown Organization"


def extract_from_generic(html: str, url: str) -> GrantPostingData:
    """Parse a generic grant posting page."""
    soup = BeautifulSoup(html, "lxml")

    title_tag = (
        soup.find("h1", class_=re.compile(r"grant|title|heading", re.I))
        or soup.find("h1")
        or soup.find("title")
    )
    title_text = title_tag.get_text(strip=True) if title_tag else "Unknown Grant"

    # Program: a secondary heading beneath the main title, if present
    program_tag = soup.find("h2", class_=re.compile(r"program|scheme|initiative", re.I))
    program_text = program_tag.get_text(strip=True) if program_tag else None

    description_tag = (
        soup.find(class_=re.compile(r"description|grant-details?|content|body", re.I))
        or soup.find("article")
        or soup.find("main")
    )
    description_text = (
        description_tag.get_text(separator=" ", strip=True) if description_tag else ""
    )

    full_text = soup.get_text(separator=" ")

    return GrantPostingData(
        title=title_text[:200],
        organization=extract_organization(soup),
        program=program_text[:200] if program_text else None,
        description=clean_description(description_text)[:5000],
        eligibility_text=extract_eligibility(soup),
        amount_range=extract_funding_amount(full_text),
        deadline=extract_deadline(full_text),
        source_url=url,
    )


async def fetch_grant_posting(url: str, timeout: float = 30.0) -> GrantPostingData:
    """Fetch and parse a grant posting from URL.

    Args:
        url: The grant posting URL.
        timeout: Request timeout in seconds.

    Returns:
        Parsed grant posting data.

    Raises:
        httpx.HTTPError: If the request fails.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        html = response.text

    return extract_from_generic(html, url)
