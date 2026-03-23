"""Job matching engine - score jobs against user profile."""

from __future__ import annotations

import re

from pydantic import BaseModel

from granthunt.config import JobProfile
from granthunt.scraper import JobPostingData


class MatchResult(BaseModel):
    """Result of matching a job against profile."""

    overall_score: float  # 0-100
    breakdown: dict[str, float]  # Per-category scores (0-100)
    red_flags: list[str]  # Detected anti-patterns
    highlights: list[str]  # Positive matches
    recommendation: str  # "Strong match", "Worth reviewing", "Likely skip"


# Role title variations for fuzzy matching
ROLE_VARIATIONS: dict[str, list[str]] = {
    "cto": ["chief technology officer", "chief tech officer", "cto"],
    "vp engineering": [
        "vp of engineering",
        "vice president engineering",
        "vp eng",
        "head of engineering",
    ],
    "technical lead": [
        "tech lead",
        "engineering lead",
        "lead engineer",
        "principal engineer",
    ],
    "architect": [
        "software architect",
        "solutions architect",
        "system architect",
        "principal architect",
    ],
}


def normalize_text(text: str) -> str:
    """Normalize text for matching."""
    return re.sub(r"[^\w\s]", " ", text.lower())


def role_score(title: str, profile: JobProfile) -> tuple[float, list[str]]:
    """Score how well the job title matches target roles.

    Returns:
        Tuple of (score 0-100, list of matched roles)
    """
    title_lower = normalize_text(title)
    highlights: list[str] = []

    for role in profile.target_roles:
        role_lower = role.lower()
        if role_lower in title_lower:
            highlights.append(f"Title matches '{role}'")
            return 100.0, highlights

        for base, variations in ROLE_VARIATIONS.items():
            if base in role_lower:
                for var in variations:
                    if var in title_lower:
                        highlights.append(f"Title matches '{role}' (via '{var}')")
                        return 90.0, highlights

    leadership_keywords = [
        "director",
        "head of",
        "lead",
        "senior",
        "principal",
        "chief",
        "vp",
        "manager",
    ]
    for kw in leadership_keywords:
        if kw in title_lower:
            highlights.append(f"Leadership role: '{kw}'")
            return 50.0, highlights

    return 20.0, []


def keyword_score(description: str, profile: JobProfile) -> tuple[float, list[str]]:
    """Score based on tech keywords match.

    Returns:
        Tuple of (score 0-100, list of matched keywords)
    """
    desc_lower = normalize_text(description)
    highlights: list[str] = []
    must_have_matches = 0
    nice_to_have_matches = 0

    for keyword in profile.tech_focus.must_have:
        if keyword.lower() in desc_lower:
            must_have_matches += 1
            highlights.append(f"Has '{keyword}'")

    for keyword in profile.tech_focus.nice_to_have:
        if keyword.lower() in desc_lower:
            nice_to_have_matches += 1

    for keyword in profile.keywords_boost:
        if keyword.lower() in desc_lower:
            highlights.append(f"Mentions '{keyword}'")

    must_have_ratio = must_have_matches / max(len(profile.tech_focus.must_have), 1)
    nice_to_have_ratio = nice_to_have_matches / max(
        len(profile.tech_focus.nice_to_have), 1
    )

    score = (must_have_ratio * 70) + (nice_to_have_ratio * 30)

    return score, highlights


def industry_score(
    description: str, company: str, profile: JobProfile
) -> tuple[float, list[str]]:
    """Score based on industry match.

    Returns:
        Tuple of (score 0-100, list of industry signals)
    """
    text_lower = normalize_text(description + " " + company)
    highlights: list[str] = []

    for industry in profile.industries.preferred:
        if industry.lower() in text_lower:
            highlights.append(f"Industry: {industry}")
            return 100.0, highlights

    for industry in profile.industries.avoid:
        if industry.lower() in text_lower:
            return 0.0, [f"Industry to avoid: {industry}"]

    return 50.0, []


def red_flag_score(description: str, profile: JobProfile) -> tuple[float, list[str]]:
    """Detect anti-patterns in job posting.

    Returns:
        Tuple of (score 0-100 where higher is better/fewer red flags, list of red flags)
    """
    desc_lower = normalize_text(description)
    red_flags: list[str] = []

    for pattern in profile.anti_patterns:
        if pattern.lower() in desc_lower:
            red_flags.append(f"Anti-pattern: '{pattern}'")

    for keyword in profile.keywords_avoid:
        if keyword.lower() in desc_lower:
            red_flags.append(f"Avoid keyword: '{keyword}'")

    common_red_flags = [
        ("rockstar", "Uses 'rockstar' language"),
        ("ninja", "Uses 'ninja' language"),
        ("fast-paced environment", "May indicate poor work-life balance"),
        ("wear many hats", "May lack focus/resources"),
        ("unlimited pto", "Often means less PTO in practice"),
    ]

    for trigger, message in common_red_flags:
        if trigger in desc_lower:
            red_flags.append(message)

    penalty_per_flag = 15
    score = max(0, 100 - len(red_flags) * penalty_per_flag)

    return score, red_flags


def score_job(job_data: JobPostingData, profile: JobProfile) -> MatchResult:
    """Score a job posting against the user's profile.

    Args:
        job_data: Scraped job posting data
        profile: User's job search profile

    Returns:
        Match result with overall score and breakdown
    """
    all_highlights: list[str] = []
    all_red_flags: list[str] = []

    role_sc, role_hl = role_score(job_data.title, profile)
    all_highlights.extend(role_hl)

    keyword_sc, keyword_hl = keyword_score(job_data.description, profile)
    all_highlights.extend(keyword_hl)

    industry_sc, industry_hl = industry_score(
        job_data.description, job_data.company, profile
    )
    if industry_sc == 0:
        all_red_flags.extend(industry_hl)
    else:
        all_highlights.extend(industry_hl)

    redflag_sc, redflag_list = red_flag_score(job_data.description, profile)
    all_red_flags.extend(redflag_list)

    weights = {
        "role": 0.30,
        "keywords": 0.25,
        "industry": 0.20,
        "red_flags": 0.25,
    }

    overall = (
        role_sc * weights["role"]
        + keyword_sc * weights["keywords"]
        + industry_sc * weights["industry"]
        + redflag_sc * weights["red_flags"]
    )

    if overall >= 70:
        recommendation = "Strong match"
    elif overall >= 50:
        recommendation = "Worth reviewing"
    else:
        recommendation = "Likely skip"

    return MatchResult(
        overall_score=round(overall, 1),
        breakdown={
            "Role match": round(role_sc, 1),
            "Tech keywords": round(keyword_sc, 1),
            "Industry": round(industry_sc, 1),
            "Red flags": round(redflag_sc, 1),
        },
        red_flags=all_red_flags[:5],
        highlights=all_highlights[:5],
        recommendation=recommendation,
    )
