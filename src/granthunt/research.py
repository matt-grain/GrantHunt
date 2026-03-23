"""Organization research module - gather information about funding organizations."""

from __future__ import annotations

import json
import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel


class OrganizationResearch(BaseModel):
    """Research data about a funding organization."""

    name: str
    website: str | None = None
    org_type: str | None = None  # "federal agency", "provincial", "foundation", etc.
    description: str | None = None
    programs: list[str] = []          # Known grant programs
    funding_signals: list[str] = []   # What they fund
    application_tips: list[str] = []  # Tips for applying


# Cache directory for research results
CACHE_DIR = Path.cwd() / ".granthunt_cache"


def get_cache_path(org_name: str) -> Path:
    """Get cache file path for an organization."""
    safe_name = re.sub(r"[^\w\s-]", "", org_name.lower()).replace(" ", "_")
    return CACHE_DIR / f"{safe_name}.json"


def load_cached_research(org_name: str) -> OrganizationResearch | None:
    """Load cached research if available."""
    cache_path = get_cache_path(org_name)
    if cache_path.exists():
        try:
            data = json.loads(cache_path.read_text())
            return OrganizationResearch.model_validate(data)
        except Exception:
            return None
    return None


def save_cached_research(research: OrganizationResearch) -> None:
    """Save research to cache."""
    CACHE_DIR.mkdir(exist_ok=True)
    cache_path = get_cache_path(research.name)
    cache_path.write_text(research.model_dump_json(indent=2))


def extract_programs(text: str) -> list[str]:
    """Extract grant program names and funding streams from website text."""
    program_keywords = [
        "Program",
        "Fund",
        "Grant",
        "Initiative",
        "Stream",
        "Funding",
        "Contribution",
        "Investment",
        "Challenge",
        "Competition",
        "Accelerator",
        "Incubator",
        "Voucher",
        "Subsidy",
        "Bursary",
        "Fellowship",
        "Award",
    ]
    found = []
    text_lower = text.lower()
    for keyword in program_keywords:
        if keyword.lower() in text_lower:
            found.append(keyword)
    return list(set(found))[:10]  # Dedupe and limit


def extract_funding_signals(text: str) -> list[str]:
    """Extract signals about what the organization funds."""
    signals = []
    text_lower = text.lower()

    funding_patterns = [
        ("clean tech", "Funds clean technology"),
        ("cleantech", "Funds clean technology"),
        ("sme", "Targets SMEs"),
        ("small and medium", "Targets SMEs"),
        ("innovation", "Innovation-focused funding"),
        ("r&d", "Supports R&D activities"),
        ("research and development", "Supports R&D activities"),
        ("quebec", "Quebec-specific funding"),
        ("climate", "Climate-focused mandate"),
        ("startup", "Supports startups"),
        ("commercialization", "Supports commercialization"),
        ("prototype", "Funds prototyping"),
        ("greenhouse gas", "GHG reduction focus"),
        ("ghg", "GHG reduction focus"),
        ("decarbonization", "Decarbonization mandate"),
        ("net zero", "Net-zero aligned"),
        ("renewable", "Renewable energy focus"),
        ("export", "Export development support"),
    ]

    for keyword, signal in funding_patterns:
        if keyword in text_lower and signal not in signals:
            signals.append(signal)

    return signals[:6]  # Limit


def generate_application_tips(research: OrganizationResearch) -> list[str]:
    """Generate application tips based on organization type and funding signals."""
    tips = []

    org_type_lower = (research.org_type or "").lower()
    signals_lower = [s.lower() for s in research.funding_signals]

    # Org-type-specific tips
    if "federal" in org_type_lower:
        tips.append("Emphasize innovation and economic impact")
    elif "provincial" in org_type_lower or "quebec" in org_type_lower:
        tips.append("Highlight Quebec job creation and local supply chain")

    # Signal-driven tips
    if any("climate" in s or "ghg" in s or "decarbonization" in s or "net-zero" in s for s in signals_lower):
        tips.append("Quantify environmental impact and GHG reduction")

    # Generic best-practice tips always included
    tips.extend(
        [
            "Demonstrate clear milestones and deliverables",
            "Show co-funding or matching funds",
            "Provide letters of support from partners",
        ]
    )

    return tips[:5]  # Top 5


async def fetch_org_website(org_name: str) -> dict[str, str | None]:
    """Try to fetch organization website and extract info."""
    possible_urls = [
        f"https://www.{org_name.lower().replace(' ', '')}.com",
        f"https://{org_name.lower().replace(' ', '')}.com",
        f"https://www.{org_name.lower().replace(' ', '-')}.com",
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
        for url in possible_urls:
            try:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "lxml")

                    # Extract text for analysis
                    text = soup.get_text(separator=" ", strip=True)[:5000]

                    # Get description from meta
                    meta_desc = soup.find("meta", attrs={"name": "description"})
                    description = (
                        meta_desc.get("content")
                        if meta_desc and hasattr(meta_desc, "get")
                        else None
                    )

                    return {
                        "website": url,
                        "description": str(description) if description else None,
                        "text": text,
                    }
            except Exception:
                continue

    return {}


async def research_organization(
    org_name: str, use_cache: bool = True
) -> OrganizationResearch:
    """Research a funding organization and gather available information.

    Args:
        org_name: Name of the organization to research
        use_cache: Whether to use cached results

    Returns:
        OrganizationResearch with gathered information
    """
    # Check cache first
    if use_cache:
        cached = load_cached_research(org_name)
        if cached:
            return cached

    research = OrganizationResearch(name=org_name)

    # Try to fetch organization website
    try:
        website_data = await fetch_org_website(org_name)
        if website_data:
            research.website = website_data.get("website")
            research.description = website_data.get("description")

            text = website_data.get("text", "") or ""
            research.programs = extract_programs(text)
            research.funding_signals = extract_funding_signals(text)
    except Exception:
        pass  # Continue without website data

    # Generate application tips
    research.application_tips = generate_application_tips(research)

    # Cache the result
    save_cached_research(research)

    return research
