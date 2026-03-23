"""Grant matching engine - score grants against startup profile."""

from __future__ import annotations

import re

from pydantic import BaseModel

from granthunt.config import GrantProfile
from granthunt.scraper import GrantPostingData


class MatchResult(BaseModel):
    """Result of matching a grant against profile."""

    overall_score: float  # 0-100
    breakdown: dict[str, float]  # Per-category scores (0-100)
    red_flags: list[str]  # Detected disqualifying signals
    highlights: list[str]  # Positive matches
    recommendation: str  # "Strong match", "Worth reviewing", "Likely skip"


# Sector synonym groups for fuzzy matching against grant descriptions
SECTOR_VARIATIONS: dict[str, list[str]] = {
    "clean tech": ["cleantech", "clean technology", "green tech", "greentech"],
    "climate": [
        "climate change",
        "decarbonization",
        "emissions reduction",
        "ghg",
        "greenhouse gas",
        "net zero",
        "carbon neutral",
    ],
    "energy": [
        "renewable energy",
        "clean energy",
        "solar",
        "wind energy",
        "energy storage",
        "energy efficiency",
        "energy transition",
    ],
    "agriculture": [
        "agri-food",
        "agrifood",
        "agtech",
        "ag tech",
        "sustainable agriculture",
        "precision agriculture",
    ],
    "transportation": [
        "electric vehicles",
        "ev",
        "sustainable mobility",
        "clean transportation",
        "electrification",
    ],
    "waste": [
        "circular economy",
        "waste management",
        "recycling",
        "zero waste",
        "biomass",
        "bioeconomy",
    ],
    "water": [
        "water management",
        "water treatment",
        "water conservation",
        "hydrology",
    ],
    "biodiversity": [
        "nature-based solutions",
        "ecosystem",
        "conservation",
        "habitat restoration",
    ],
}


def normalize_text(text: str) -> str:
    """Normalize text for matching."""
    return re.sub(r"[^\w\s]", " ", text.lower())


def sector_score(description: str, profile: GrantProfile) -> tuple[float, list[str]]:
    """Score how well the grant's sector coverage matches the startup's sectors.

    Returns:
        Tuple of (score 0-100, list of matched sector highlights)
    """
    desc_lower = normalize_text(description)
    highlights: list[str] = []

    for sector in profile.eligibility.sectors:
        sector_lower = sector.lower()

        # Exact sector mention
        if sector_lower in desc_lower:
            highlights.append(f"Sector match: '{sector}'")
            return 100.0, highlights

        # Check via synonym groups
        for base, variations in SECTOR_VARIATIONS.items():
            if base in sector_lower or sector_lower in base:
                for variant in variations:
                    if variant in desc_lower:
                        highlights.append(f"Sector match: '{sector}' (via '{variant}')")
                        return 100.0, highlights
                # Base key itself may appear in description
                if base in desc_lower:
                    highlights.append(f"Sector match: '{sector}' (via '{base}')")
                    return 100.0, highlights

        # Check if any synonym group partially overlaps with the sector term
        for base, variations in SECTOR_VARIATIONS.items():
            for variant in variations:
                if variant in desc_lower:
                    highlights.append(f"Related sector: '{variant}'")
                    return 50.0, highlights

    return 20.0, []


def eligibility_score(
    description: str, profile: GrantProfile
) -> tuple[float, list[str]]:
    """Score based on how many eligibility criteria the grant matches.

    Checks for activity alignment (R&D, innovation, etc.), SME/startup mentions,
    and Quebec/Canada regional eligibility.

    Returns:
        Tuple of (score 0-100, list of matched eligibility highlights)
    """
    desc_lower = normalize_text(description)
    highlights: list[str] = []
    criteria_met = 0
    criteria_total = 0

    # Activity matching
    for activity in profile.eligibility.activities:
        criteria_total += 1
        activity_lower = activity.lower()
        if activity_lower in desc_lower:
            criteria_met += 1
            highlights.append(f"Activity eligible: '{activity}'")

    # SME / startup eligibility signals (always checked)
    sme_signals = [
        ("sme", "Eligible for SMEs"),
        ("small and medium", "Eligible for SMEs"),
        ("startup", "Eligible for startups"),
        ("start-up", "Eligible for startups"),
        ("early-stage", "Eligible for early-stage companies"),
        ("early stage", "Eligible for early-stage companies"),
    ]
    criteria_total += 1
    for signal, message in sme_signals:
        if signal in desc_lower:
            criteria_met += 1
            highlights.append(message)
            break

    # Regional eligibility: Quebec / Canada
    regional_signals = [
        ("quebec", "Quebec-eligible"),
        ("québec", "Quebec-eligible"),
        ("canada", "Canada-eligible"),
        ("canadian", "Canada-eligible"),
    ]
    criteria_total += 1
    for signal, message in regional_signals:
        if signal in desc_lower:
            criteria_met += 1
            highlights.append(message)
            break

    # Certification bonus (if profile lists certifications like ISO, B-Corp, etc.)
    for cert in profile.eligibility.certifications:
        criteria_total += 1
        if cert.lower() in desc_lower:
            criteria_met += 1
            highlights.append(f"Certification recognized: '{cert}'")

    if criteria_total == 0:
        return 50.0, highlights

    score = (criteria_met / criteria_total) * 100
    return round(score, 1), highlights


def funding_fit_score(
    description: str, amount_range: str | None, profile: GrantProfile
) -> tuple[float, list[str]]:
    """Score based on funding amount and grant type alignment.

    Returns:
        Tuple of (score 0-100, list of funding fit highlights)
    """
    desc_lower = normalize_text(description)
    highlights: list[str] = []
    score = 50.0  # Default: unknown, neutral

    # Grant type matching
    if profile.funding_prefs.types:
        type_signals: dict[str, list[str]] = {
            "grant": ["grant", "contribution", "non-repayable", "subsidy"],
            "tax_credit": ["tax credit", "sr&ed", "sred", "cctb", "tax incentive"],
            "loan": ["loan", "repayable", "interest-free loan", "financing"],
            "equity": ["equity", "investment", "venture", "co-investment"],
        }
        for pref_type in profile.funding_prefs.types:
            signals = type_signals.get(pref_type.lower(), [pref_type.lower()])
            for signal in signals:
                if signal in desc_lower:
                    highlights.append(f"Grant type match: '{pref_type}'")
                    score = max(score, 70.0)
                    break

    # Amount range check — parse first number found in amount_range string
    if amount_range:
        amount_lower = normalize_text(amount_range)
        # Extract leading numeric value (handles "$500,000", "500 000", etc.)
        match = re.search(r"[\d]+(?:[,\s][\d]+)*", amount_lower)
        if match:
            raw = re.sub(r"[,\s]", "", match.group())
            try:
                amount = float(raw)
                min_ok = (
                    profile.funding_prefs.min_amount is None
                    or amount >= profile.funding_prefs.min_amount
                )
                max_ok = (
                    profile.funding_prefs.max_amount is None
                    or amount <= profile.funding_prefs.max_amount
                )
                if min_ok and max_ok:
                    highlights.append(f"Amount within target range: {amount_range}")
                    score = 100.0
                else:
                    score = 0.0
                    if not min_ok:
                        highlights.append(
                            f"Amount {amount_range} below minimum"
                            f" ${profile.funding_prefs.min_amount:,.0f}"
                        )
                    if not max_ok:
                        highlights.append(
                            f"Amount {amount_range} above maximum"
                            f" ${profile.funding_prefs.max_amount:,.0f}"
                        )
            except ValueError:
                pass  # Unparseable amount — leave score neutral

    return score, highlights


def keyword_score(description: str, profile: GrantProfile) -> tuple[float, list[str]]:
    """Score based on boost/avoid keyword matches in the grant description.

    Returns:
        Tuple of (score 0-100, list of matched keyword highlights)
    """
    desc_lower = normalize_text(description)
    highlights: list[str] = []
    boost_matches = 0

    for keyword in profile.keywords_boost:
        if keyword.lower() in desc_lower:
            boost_matches += 1
            highlights.append(f"Keyword match: '{keyword}'")

    avoid_hits = sum(
        1 for kw in profile.keywords_avoid if kw.lower() in desc_lower
    )

    if not profile.keywords_boost:
        boost_ratio = 1.0
    else:
        boost_ratio = boost_matches / len(profile.keywords_boost)

    # Boost keywords drive score up; avoid keywords pull it down
    score = boost_ratio * 100
    score = max(0.0, score - avoid_hits * 15)

    return round(score, 1), highlights


def red_flag_score(
    description: str, profile: GrantProfile
) -> tuple[float, list[str]]:
    """Detect disqualifying signals in the grant description.

    Returns:
        Tuple of (score 0-100 where higher means fewer red flags, list of red flags)
    """
    desc_lower = normalize_text(description)
    red_flags: list[str] = []

    for keyword in profile.keywords_avoid:
        if keyword.lower() in desc_lower:
            red_flags.append(f"Avoid keyword: '{keyword}'")

    common_red_flags = [
        ("large enterprise only", "Restricted to large enterprises"),
        ("minimum revenue 10", "Requires minimum $10M revenue"),
        ("minimum revenue of 10", "Requires minimum $10M revenue"),
        ("publicly traded", "Restricted to publicly traded companies"),
        ("250 employees", "Requires 250+ employees"),
        ("500 employees", "Requires 500+ employees"),
        ("must have 250", "Requires 250+ employees"),
        ("not eligible.*startup", "Startups explicitly excluded"),
        ("for-profit only", "Excludes non-profits (verify fit)"),
        ("canadian citizens only", "May exclude incorporated entities"),
    ]

    for trigger, message in common_red_flags:
        if re.search(trigger, desc_lower):
            red_flags.append(message)

    penalty_per_flag = 15
    score = max(0.0, 100.0 - len(red_flags) * penalty_per_flag)

    return score, red_flags


def score_grant(grant_data: GrantPostingData, profile: GrantProfile) -> MatchResult:
    """Score a grant posting against the startup's profile.

    Args:
        grant_data: Scraped grant posting data
        profile: Startup's grant search profile

    Returns:
        Match result with overall score and breakdown
    """
    all_highlights: list[str] = []
    all_red_flags: list[str] = []

    full_text = " ".join(
        filter(
            None,
            [
                grant_data.description,
                grant_data.eligibility_text,
                grant_data.program,
            ],
        )
    )

    sector_sc, sector_hl = sector_score(full_text, profile)
    all_highlights.extend(sector_hl)

    eligibility_sc, eligibility_hl = eligibility_score(full_text, profile)
    all_highlights.extend(eligibility_hl)

    funding_sc, funding_hl = funding_fit_score(
        full_text, grant_data.amount_range, profile
    )
    all_highlights.extend(funding_hl)

    keyword_sc, keyword_hl = keyword_score(full_text, profile)
    all_highlights.extend(keyword_hl)

    redflag_sc, redflag_list = red_flag_score(full_text, profile)
    all_red_flags.extend(redflag_list)

    weights = {
        "sector": 0.30,
        "eligibility": 0.25,
        "funding_fit": 0.20,
        "keywords": 0.15,
        "red_flags": 0.10,
    }

    overall = (
        sector_sc * weights["sector"]
        + eligibility_sc * weights["eligibility"]
        + funding_sc * weights["funding_fit"]
        + keyword_sc * weights["keywords"]
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
            "Sector match": round(sector_sc, 1),
            "Eligibility": round(eligibility_sc, 1),
            "Funding fit": round(funding_sc, 1),
            "Keywords": round(keyword_sc, 1),
            "Red flags": round(redflag_sc, 1),
        },
        red_flags=all_red_flags[:5],
        highlights=all_highlights[:5],
        recommendation=recommendation,
    )
