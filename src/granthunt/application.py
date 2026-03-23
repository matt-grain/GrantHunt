"""Grant application materials generator - LOI, executive summary, eligibility checklist."""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from granthunt.config import GrantProfile, load_profile
from granthunt.models import Grant


def load_research(research_path: Path) -> dict[str, str]:
    """Load and parse a grant research file into labelled sections.

    Returns dict with any of:
    - organization_overview: Brief funder description
    - programs: Program descriptions and scope
    - application_tips: Reviewer guidance / tips
    - eligibility: Stated eligibility criteria
    """
    if not research_path.exists():
        return {}

    content = research_path.read_text(encoding="utf-8")
    result: dict[str, str] = {}

    overview_match = re.search(
        r"## Organization Overview\s*\n+(.+?)(?=\n##|\n---|\Z)",
        content,
        re.DOTALL,
    )
    if overview_match:
        result["organization_overview"] = overview_match.group(1).strip()[:600]

    programs_match = re.search(
        r"## Programs\s*\n+(.+?)(?=\n##|\n---|\Z)",
        content,
        re.DOTALL,
    )
    if programs_match:
        result["programs"] = programs_match.group(1).strip()[:600]

    tips_match = re.search(
        r"## Application Tips\s*\n+(.+?)(?=\n##|\n---|\Z)",
        content,
        re.DOTALL,
    )
    if tips_match:
        result["application_tips"] = tips_match.group(1).strip()[:600]

    eligibility_match = re.search(
        r"## Eligibility\s*\n+(.+?)(?=\n##|\n---|\Z)",
        content,
        re.DOTALL,
    )
    if eligibility_match:
        result["eligibility"] = eligibility_match.group(1).strip()[:600]

    return result


def generate_loi(
    grant: Grant,
    output_path: Path | None = None,
    research_path: Path | None = None,
) -> str:
    """Generate a Letter of Intent for a grant application.

    Args:
        grant: The grant to apply for.
        output_path: Optional path to save the LOI as a markdown file.
        research_path: Optional path to a research markdown file for personalization.

    Returns:
        The LOI content as a markdown string.
    """
    profile = load_profile()
    research = load_research(research_path) if research_path else None
    loi = generate_loi_draft(grant, profile, research)

    if output_path:
        output_path.write_text(loi, encoding="utf-8")

    return loi


def generate_loi_draft(
    grant: Grant,
    profile: GrantProfile,
    research: dict[str, str] | None = None,
) -> str:
    """Generate a Letter of Intent markdown document.

    Args:
        grant: The grant to apply for.
        profile: The applicant's GrantProfile.
        research: Optional research dict from load_research().

    Returns:
        Full LOI as a markdown string.
    """
    research = research or {}
    today = date.today().strftime("%B %d, %Y")
    startup = profile.startup

    # Build alignment section from research or fall back to a placeholder
    if research.get("programs"):
        alignment_body = (
            f"{grant.organization}'s programs focus on:\n\n"
            f"{research['programs']}\n\n"
            f"{startup.name}'s work in {startup.industry} directly addresses these "
            "objectives through its core platform and planned R&D activities."
        )
    elif research.get("organization_overview"):
        alignment_body = (
            f"{research['organization_overview']}\n\n"
            f"{startup.name} is well-positioned to advance these priorities through "
            "its work in the climate technology sector."
        )
    else:
        alignment_body = (
            f"[Describe how {startup.name}'s activities align with "
            f"{grant.organization}'s mandate and this program's objectives.]"
        )

    # Build funding placeholder using grant amount range when available
    if grant.amount_min and grant.amount_max:
        budget_line = (
            f"Total requested: ${grant.amount_min:,.0f}–${grant.amount_max:,.0f} | "
            "Matching funds: [TBD] | Project timeline: [TBD]"
        )
    elif grant.amount_max:
        budget_line = (
            f"Total requested: up to ${grant.amount_max:,.0f} | "
            "Matching funds: [TBD] | Project timeline: [TBD]"
        )
    else:
        budget_line = (
            "Total requested: [TBD] | Matching funds: [TBD] | Project timeline: [TBD]"
        )

    loi = f"""# Letter of Intent

**Grant Program:** {grant.title}
**Funding Organization:** {grant.organization}
**Applicant:** {startup.name}
**Date:** {today}

---

## Project Summary

{startup.name} is a {startup.stage}-stage {startup.industry} company based in \
{startup.location}. {startup.description}

This Letter of Intent outlines our intent to apply for funding under the \
{grant.title} program administered by {grant.organization}. The proposed project \
will advance our core mission and deliver measurable environmental and economic impact.

## Alignment with Grant Objectives

{alignment_body}

## Expected Outcomes & Impact

- **Environmental impact:** Reduction in greenhouse gas emissions through deployment \
of {startup.name}'s technology; measurable contribution to Canada's climate targets.
- **Economic impact:** Creation of high-value jobs in the clean technology sector; \
projected revenue growth supporting long-term commercial viability.
- **Innovation contribution:** Advancement of proprietary technology with potential \
for licensing, replication, and export to international markets.

## Budget Summary

{budget_line}

## About {startup.name}

- **Industry:** {startup.industry}
- **Stage:** {startup.stage}
- **Location:** {startup.location}\
{f"{chr(10)}- **Founded:** {startup.founded_year}" if startup.founded_year else ""}\
{f"{chr(10)}- **Team size:** {startup.employees} employees" if startup.employees else ""}\
{f"{chr(10)}- **Website:** {startup.website}" if startup.website else ""}

---

*Draft generated by GrantHunt. Review and personalize before submitting.*
"""
    return loi


def generate_executive_summary(grant: Grant, profile: GrantProfile) -> str:
    """Generate a one-page executive summary for a grant application.

    Covers: problem, solution, market, team, and funding ask.

    Args:
        grant: The grant being applied for.
        profile: The applicant's GrantProfile.

    Returns:
        Executive summary as a markdown string.
    """
    startup = profile.startup

    # Build funding ask line
    if grant.amount_min and grant.amount_max:
        ask = f"${grant.amount_min:,.0f}–${grant.amount_max:,.0f}"
    elif grant.amount_max:
        ask = f"up to ${grant.amount_max:,.0f}"
    else:
        ask = "[requested amount]"

    summary = f"""# Executive Summary

**Applicant:** {startup.name}
**Grant Program:** {grant.title} — {grant.organization}

---

## The Problem

Climate change demands rapid deployment of clean technology. [Describe the specific \
market gap or environmental problem that {startup.name} addresses — quantify the \
scale where possible.]

## Our Solution

{startup.description}

[Elaborate on how the technology works, what differentiates it from existing \
approaches, and its current development stage ({startup.stage}).]

## Market Opportunity

The global market for {startup.industry} solutions is growing rapidly, driven by \
regulatory pressure, corporate sustainability commitments, and investor demand. \
[Insert specific market size and growth rate data.]

## Team

{startup.name} is led by an experienced team combining deep domain expertise in \
{startup.industry} with proven commercial execution. [List key team members, \
relevant credentials, and any advisory board members.]

## Funding Ask

We are requesting {ask} to [describe the specific use of funds: R&D milestones, \
equipment, hiring, pilots, etc.]. This investment will enable [describe the key \
outcomes unlocked by the funding].

---

*Draft generated by GrantHunt. Review and personalize before submitting.*
"""
    return summary


def generate_eligibility_checklist(grant: Grant, profile: GrantProfile) -> str:
    """Generate a markdown eligibility checklist for a grant application.

    Covers common Canadian grant requirements. Items are pre-ticked where the
    profile already provides confirming information.

    Args:
        grant: The grant being applied for.
        profile: The applicant's GrantProfile.

    Returns:
        Eligibility checklist as a markdown string.
    """
    startup = profile.startup

    # Determine ticks we can infer from profile data
    is_canadian = any(
        kw in startup.location.lower()
        for kw in ("canada", "québec", "quebec", "ontario", "bc", "alberta")
    )
    is_sme = (startup.employees or 0) < 500 if startup.employees else None
    is_quebec = any(
        kw in startup.location.lower() for kw in ("québec", "quebec", "montréal", "montreal")
    )
    does_rd = any(
        act.lower() in ("r&d", "research", "development", "research and development")
        for act in profile.eligibility.activities
    )

    def tick(condition: bool | None) -> str:
        if condition is True:
            return "x"
        return " "

    checklist = f"""# Eligibility Checklist

**Grant Program:** {grant.title}
**Funding Organization:** {grant.organization}
**Applicant:** {startup.name}

Review each item and confirm before submitting.

---

## Corporate Eligibility

- [{tick(is_canadian)}] Canadian company (incorporated in Canada)
- [{tick(is_quebec)}] Incorporated in Quebec *(if required by this program)*
- [{tick(is_sme)}] SME — fewer than 500 full-time employees
- [ ] For-profit corporation *(verify program allows non-profits if applicable)*
- [ ] Company is in good standing (no outstanding government debts)

## Project Eligibility

- [{tick(does_rd)}] Project involves eligible R&D or innovation activities
- [ ] Project not already fully funded by another government program
- [ ] Project aligns with program's thematic focus \
({", ".join(profile.eligibility.sectors[:3]) if profile.eligibility.sectors else "climate tech"})
- [ ] Project has a defined start and end date
- [ ] Project activities will occur primarily in Canada

## Financial Requirements

- [ ] Project budget prepared and documented
- [ ] Matching funds identified *(if cost-sharing is required)*
- [ ] Audited financial statements available *(if required)*
- [ ] Bank account in company name

## Application Package

- [ ] Completed application form
- [ ] Project description / technical proposal
- [ ] Budget breakdown by eligible expense category
- [ ] Letters of support from partners or customers
- [ ] Corporate documents (articles of incorporation, business number)
- [ ] Team CVs / bios for key project personnel
- [ ] Intellectual property statement *(if required)*

## Certifications (if applicable)

{chr(10).join(f"- [ ] {cert}" for cert in profile.eligibility.certifications) if profile.eligibility.certifications else "- [ ] No specific certifications required by this program — confirm."}

---

*Checklist generated by GrantHunt. Verify requirements against the official program guide.*
"""
    return checklist
