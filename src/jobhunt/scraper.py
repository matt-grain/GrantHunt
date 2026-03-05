"""Job posting scraper - fetch and parse job listings from URLs."""

from __future__ import annotations

import re

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel


class JobPostingData(BaseModel):
    """Scraped job posting data."""

    title: str
    company: str
    location: str
    description: str
    requirements: list[str] = []
    salary: str | None = None
    remote: bool | None = None
    source_url: str


def clean_description(text: str) -> str:
    """Strip HTML tags and normalize whitespace."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_requirements(soup: BeautifulSoup) -> list[str]:
    """Extract bullet point requirements from job posting."""
    requirements = []
    for li in soup.find_all("li"):
        text = li.get_text(strip=True)
        if len(text) > 10 and len(text) < 500:
            requirements.append(text)
    return requirements[:15]


def detect_remote(text: str) -> bool | None:
    """Detect if job is remote based on description."""
    text_lower = text.lower()
    if (
        "fully remote" in text_lower
        or "work from home" in text_lower
        or "100% remote" in text_lower
    ):
        return True
    if (
        "on-site only" in text_lower
        or "no remote" in text_lower
        or "in-office" in text_lower
    ):
        return False
    if "remote" in text_lower or "hybrid" in text_lower:
        return True
    return None


def extract_salary(text: str) -> str | None:
    """Extract salary information from text."""
    patterns = [
        r"\$[\d,]+(?:\s*-\s*\$[\d,]+)?(?:\s*(?:per year|annually|/year|/yr))?",
        r"[\d,]+k\s*-\s*[\d,]+k",
        r"(?:salary|compensation)[:\s]+\$?[\d,]+",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group()
    return None


def extract_from_linkedin(html: str, url: str) -> JobPostingData:
    """Parse LinkedIn job posting."""
    soup = BeautifulSoup(html, "lxml")

    title = soup.find("h1", class_="top-card-layout__title") or soup.find("h1")
    company = soup.find("a", class_="topcard__org-name-link") or soup.find(
        "span", class_="topcard__flavor"
    )
    location = soup.find("span", class_="topcard__flavor--bullet")
    description_div = soup.find("div", class_="description__text") or soup.find(
        "div", class_="show-more-less-html__markup"
    )

    title_text = title.get_text(strip=True) if title else "Unknown Title"
    company_text = company.get_text(strip=True) if company else "Unknown Company"
    location_text = location.get_text(strip=True) if location else "Unknown Location"
    description_text = (
        description_div.get_text(separator=" ", strip=True) if description_div else ""
    )

    return JobPostingData(
        title=title_text,
        company=company_text,
        location=location_text,
        description=clean_description(description_text),
        requirements=extract_requirements(soup),
        salary=extract_salary(description_text),
        remote=detect_remote(description_text),
        source_url=url,
    )


def extract_from_generic(html: str, url: str) -> JobPostingData:
    """Parse generic job posting page."""
    soup = BeautifulSoup(html, "lxml")

    title = (
        soup.find("h1", class_=re.compile(r"job|title", re.I))
        or soup.find("h1")
        or soup.find("title")
    )

    company = soup.find(
        class_=re.compile(r"company|employer|organization", re.I)
    ) or soup.find("meta", {"property": "og:site_name"})

    description = (
        soup.find(class_=re.compile(r"description|job-details|content", re.I))
        or soup.find("article")
        or soup.find("main")
    )

    title_text = title.get_text(strip=True) if title else "Unknown Title"
    company_text = (
        company.get("content")
        if company and company.get("content")
        else (company.get_text(strip=True) if company else "Unknown Company")
    )
    description_text = (
        description.get_text(separator=" ", strip=True) if description else ""
    )

    return JobPostingData(
        title=title_text[:200],
        company=company_text[:100],
        location="See posting",
        description=clean_description(description_text)[:5000],
        requirements=extract_requirements(soup),
        salary=extract_salary(description_text),
        remote=detect_remote(description_text),
        source_url=url,
    )


async def fetch_job_posting(url: str, timeout: float = 30.0) -> JobPostingData:
    """Fetch and parse a job posting from URL.

    Args:
        url: The job posting URL
        timeout: Request timeout in seconds

    Returns:
        Parsed job posting data

    Raises:
        httpx.HTTPError: If the request fails
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

    if "linkedin.com" in url:
        return extract_from_linkedin(html, url)
    return extract_from_generic(html, url)
