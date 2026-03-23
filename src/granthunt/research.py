"""Company research module - gather information about potential employers."""

from __future__ import annotations

import json
import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel


class CompanyResearch(BaseModel):
    """Research data about a company."""

    name: str
    website: str | None = None
    industry: str | None = None
    size: str | None = None
    description: str | None = None
    tech_stack: list[str] = []
    culture_signals: list[str] = []
    interview_prep: list[str] = []  # Suggested questions to ask


# Cache directory for research results
CACHE_DIR = Path.cwd() / ".jobhunt_cache"


def get_cache_path(company_name: str) -> Path:
    """Get cache file path for a company."""
    safe_name = re.sub(r"[^\w\s-]", "", company_name.lower()).replace(" ", "_")
    return CACHE_DIR / f"{safe_name}.json"


def load_cached_research(company_name: str) -> CompanyResearch | None:
    """Load cached research if available."""
    cache_path = get_cache_path(company_name)
    if cache_path.exists():
        try:
            data = json.loads(cache_path.read_text())
            return CompanyResearch.model_validate(data)
        except Exception:
            return None
    return None


def save_cached_research(research: CompanyResearch) -> None:
    """Save research to cache."""
    CACHE_DIR.mkdir(exist_ok=True)
    cache_path = get_cache_path(research.name)
    cache_path.write_text(research.model_dump_json(indent=2))


def extract_tech_stack(text: str) -> list[str]:
    """Extract technology mentions from text."""
    tech_keywords = [
        "Python",
        "JavaScript",
        "TypeScript",
        "React",
        "Node.js",
        "AWS",
        "Azure",
        "GCP",
        "Kubernetes",
        "Docker",
        "PostgreSQL",
        "MongoDB",
        "Redis",
        "GraphQL",
        "REST API",
        "Microservices",
        "Machine Learning",
        "AI",
        "LLM",
        "FastAPI",
        "Django",
        "Flask",
        "Next.js",
        "Vue",
        "Angular",
        "Go",
        "Rust",
        "Java",
        "C#",
        ".NET",
        "Terraform",
        "CI/CD",
        "GitHub Actions",
        "Jenkins",
    ]
    found = []
    text_lower = text.lower()
    for tech in tech_keywords:
        if tech.lower() in text_lower:
            found.append(tech)
    return list(set(found))[:10]  # Dedupe and limit


def extract_culture_signals(text: str) -> list[str]:
    """Extract culture-related signals from text."""
    signals = []
    text_lower = text.lower()

    culture_patterns = [
        ("remote", "Offers remote work"),
        ("hybrid", "Hybrid work model"),
        ("flexible", "Flexible work arrangements"),
        ("diversity", "Values diversity & inclusion"),
        ("equity", "Focus on equity"),
        ("work-life balance", "Emphasizes work-life balance"),
        ("learning", "Learning & development opportunities"),
        ("growth", "Career growth focus"),
        ("startup", "Startup environment"),
        ("enterprise", "Enterprise scale"),
        ("agile", "Agile methodology"),
        ("innovation", "Innovation-focused"),
    ]

    for keyword, signal in culture_patterns:
        if keyword in text_lower and signal not in signals:
            signals.append(signal)

    return signals[:6]  # Limit


def generate_interview_questions(research: CompanyResearch) -> list[str]:
    """Generate interview questions based on research."""
    questions = []

    # Tech stack questions
    if research.tech_stack:
        tech_list = ", ".join(research.tech_stack[:3])
        questions.append(
            f"I saw you use {tech_list}. How does your team approach architecture decisions?"
        )

    # Culture questions
    if "Offers remote work" in research.culture_signals:
        questions.append(
            "How does the team stay connected and collaborate in a remote/hybrid setting?"
        )

    if "Startup environment" in research.culture_signals:
        questions.append(
            "What's the current stage of the company and runway situation?"
        )

    # Generic good questions
    questions.extend(
        [
            "What does success look like in this role after 90 days?",
            "What are the biggest technical challenges the team is facing?",
            "How do you approach technical debt vs. new feature development?",
            "What's the team structure and who would I be working with closely?",
        ]
    )

    return questions[:5]  # Top 5


async def fetch_company_website(company_name: str) -> dict[str, str | None]:
    """Try to fetch company website and extract info."""
    # Search for company website (simplified - just construct common patterns)
    possible_urls = [
        f"https://www.{company_name.lower().replace(' ', '')}.com",
        f"https://{company_name.lower().replace(' ', '')}.com",
        f"https://www.{company_name.lower().replace(' ', '-')}.com",
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


async def research_company(
    company_name: str, use_cache: bool = True
) -> CompanyResearch:
    """Research a company and gather available information.

    Args:
        company_name: Name of the company to research
        use_cache: Whether to use cached results

    Returns:
        CompanyResearch with gathered information
    """
    # Check cache first
    if use_cache:
        cached = load_cached_research(company_name)
        if cached:
            return cached

    research = CompanyResearch(name=company_name)

    # Try to fetch company website
    try:
        website_data = await fetch_company_website(company_name)
        if website_data:
            research.website = website_data.get("website")
            research.description = website_data.get("description")

            text = website_data.get("text", "") or ""
            research.tech_stack = extract_tech_stack(text)
            research.culture_signals = extract_culture_signals(text)
    except Exception:
        pass  # Continue without website data

    # Generate interview questions
    research.interview_prep = generate_interview_questions(research)

    # Cache the result
    save_cached_research(research)

    return research
