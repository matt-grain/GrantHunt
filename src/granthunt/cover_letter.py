"""Cover letter generation module."""

from __future__ import annotations

import re
from pathlib import Path

from granthunt.config import JobProfile, load_profile
from granthunt.models import Job


def load_research(research_path: Path) -> dict[str, str]:
    """Load and parse research file for cover letter enhancement.

    Returns dict with:
    - company_overview: Brief description
    - why_company: "Why [Company]?" talking points
    - recent_news: Recent developments
    - tech_focus: Tech/AI initiatives
    """
    if not research_path.exists():
        return {}

    content = research_path.read_text(encoding="utf-8")
    result: dict[str, str] = {}

    # Extract company overview (first paragraph after "## Company Overview")
    overview_match = re.search(
        r"## Company Overview\s*\n+(.+?)(?=\n##|\n---|\Z)",
        content,
        re.DOTALL,
    )
    if overview_match:
        result["company_overview"] = overview_match.group(1).strip()[:500]

    # Extract "Why [Company]?" hooks - flexible matching
    why_match = re.search(
        r'(?:###?\s*"?Why .+?"? Hooks?|## Interview Talking Points.+?)\s*\n+(.+?)(?=\n###|\n##|\n---|\Z)',
        content,
        re.DOTALL | re.IGNORECASE,
    )
    if why_match:
        result["why_company"] = why_match.group(1).strip()

    # Extract recent news
    news_match = re.search(
        r"## Recent (?:News|Strategic|Developments).+?\n+(.+?)(?=\n##|\n---|\Z)",
        content,
        re.DOTALL,
    )
    if news_match:
        result["recent_news"] = news_match.group(1).strip()[:400]

    # Extract tech/AI focus
    tech_match = re.search(
        r"## Tech & Innovation\s*\n+(.+?)(?=\n##|\n---|\Z)",
        content,
        re.DOTALL,
    )
    if tech_match:
        result["tech_focus"] = tech_match.group(1).strip()[:400]

    return result


def get_resume_path() -> Path:
    """Get path to resume file."""
    cwd = Path.cwd()

    # Check common locations
    candidates = [
        cwd / "profile" / "resume_matthieu_boujonnier.md",
        cwd / "profile" / "resume.md",
        cwd / "resume.md",
    ]

    for path in candidates:
        if path.exists():
            return path

    msg = "Resume not found. Expected at profile/resume_matthieu_boujonnier.md"
    raise FileNotFoundError(msg)


def load_resume() -> str:
    """Load resume content."""
    path = get_resume_path()
    return path.read_text(encoding="utf-8")


def extract_key_requirements(job_description: str) -> list[str]:
    """Extract key requirements from job description."""
    requirements = []

    # Split into sentences/bullets
    lines = re.split(r"[.\n\u2022\-\*]", job_description)

    # Look for requirement-like phrases
    requirement_signals = [
        "experience",
        "required",
        "must have",
        "looking for",
        "ideal candidate",
        "qualifications",
        "skills",
        "proficient",
        "knowledge of",
        "ability to",
        "responsible for",
        "you will",
        "you have",
        "expertise",
    ]

    for line in lines:
        line = line.strip()
        if len(line) > 20 and len(line) < 300:
            line_lower = line.lower()
            for signal in requirement_signals:
                if signal in line_lower:
                    requirements.append(line)
                    break

    return requirements[:8]  # Top 8


def match_experience_to_requirements(
    requirements: list[str], _resume: str
) -> dict[str, str]:
    """Map job requirements to relevant experience from resume.

    Returns dict mapping requirement -> relevant experience snippet
    """
    matches = {}

    # Key experience areas to highlight
    experience_highlights = {
        "ai": (
            "Led AI transformation using Claude to refactor entire platform - "
            "reduced engineering team from 6 to 2 developers, "
            "cut deployment cycles from 2 months to 2 weeks"
        ),
        "ml": (
            "Led Analytics and AI Corporate team, "
            "building edge-to-cloud platforms for industrial analytics"
        ),
        "machine learning": (
            "Delivered ML solutions for Oil & Gas, Datacenters, Buildings"
        ),
        "architecture": (
            "25 years architecting systems across IoT, cloud, and enterprise"
        ),
        "leadership": (
            "CTO & Co-Founder, led all technology decisions "
            "from founding through two funding rounds"
        ),
        "team": (
            "Deep expertise bridging technical architecture with business outcomes"
        ),
        "product": "AI-first product development: smaller teams, faster delivery",
        "cloud": (
            "Architected full-stack platform: Next.js frontend, "
            "FastAPI backend, Azure PaaS"
        ),
        "scale": "Lead Architect for AI Hub infrastructure with Microsoft",
        "startup": "Co-founded and built from scratch a climate tech platform",
    }

    for req in requirements:
        req_lower = req.lower()
        for keyword, highlight in experience_highlights.items():
            if keyword in req_lower:
                matches[req] = highlight
                break

    return matches


def generate_cover_letter_prompt(
    job: Job,
    profile: JobProfile,
    resume: str,
    research: dict[str, str] | None = None,
) -> str:
    """Generate a prompt/draft for cover letter.

    This creates a structured draft that can be refined.

    Args:
        job: Job to apply for
        profile: User's job profile
        resume: Resume content
        research: Optional research dict from load_research()
    """
    requirements = extract_key_requirements(job.raw_description or "")
    matches = match_experience_to_requirements(requirements, resume)
    research = research or {}

    # Build the "Why Company" section from research
    why_section = _build_why_section(job.company, research)

    # Build the cover letter draft
    letter = f"""# Cover Letter Draft

**Position:** {job.title}
**Company:** {job.company}
**Applicant:** {profile.name}

---

## Opening

Dear Hiring Team,

I am writing to express my interest in the {job.title} position at {job.company}. \
With 25 years of experience architecting systems across IoT, cloud, and enterprise - \
and a recent focus on AI-first product development - \
I am excited about the opportunity to contribute to your team.

## Why {job.company}

{why_section}

## Key Qualifications

"""

    # Add matched experience
    if matches:
        for req, experience in list(matches.items())[:3]:
            letter += f"**Relevant to: {req[:100]}...**\n"
            letter += f"- {experience}\n\n"
    else:
        letter += """- Led AI transformation that reduced engineering team from 6 to 2 \
while cutting deployment cycles from 2 months to 2 weeks
- 25 years of architecture experience across Industrial, Telecoms, Healthcare, \
and Energy sectors
- Deep expertise bridging technical architecture with business outcomes at all levels

"""

    letter += f"""## The AI Transformation Story

At Grain Ecosystem, I made a bold bet: refactoring our entire platform using \
AI-assisted development. The results speak for themselves - deployment cycles \
dropped from 2 months to 2 weeks, and bug resolution time went from 3 weeks to days. \
This wasn't just about cutting costs; it was about building better, faster, and leaner.

I've learned that AI-generated code is only as good as the architecture behind it. \
My decades of experience designing systems - from embedded IoT to enterprise cloud - \
is what turns AI from a code generator into a true force multiplier.

## Closing

I would welcome the opportunity to discuss how my experience in technical leadership \
and AI-first development can contribute to {job.company}'s goals. \
I am available for an interview at your convenience.

Best regards,
{profile.name}
{profile.location}

---

*Note: This is a draft. Review and personalize before sending.*
"""

    return letter


def _build_why_section(company: str, research: dict[str, str]) -> str:
    """Build the 'Why Company' section from research data."""
    if not research:
        return "[Personalize this section based on company research]"

    parts = []

    # Add company context if available
    if "company_overview" in research:
        # Extract first sentence or two
        overview = research["company_overview"]
        first_sentences = ". ".join(overview.split(". ")[:2]) + "."
        parts.append(
            f"{company}'s position as {first_sentences[:200]} "
            "aligns well with my experience."
        )

    # Add specific "Why" hooks from research
    if "why_company" in research:
        why_text = research["why_company"]
        # Extract hook titles - try multiple formats
        # Format 1: **Hook Title**
        hooks = re.findall(r"\*\*(.+?)\*\*", why_text)[:3]
        # Format 2: ### N. Hook Title
        if not hooks:
            hooks = re.findall(r"###?\s*\d+\.\s*(.+?)(?:\n|$)", why_text)[:3]
        # Format 3: N. **Hook Title**
        if not hooks:
            hooks = re.findall(r"\d+\.\s*\*\*(.+?)\*\*", why_text)[:3]

        if hooks:
            parts.append("\nWhat draws me to this opportunity:\n")
            for hook in hooks:
                # Clean up the hook title
                hook = hook.strip().rstrip(":")
                parts.append(f"- **{hook}**")

    # Add tech/AI angle if available
    if "tech_focus" in research:
        tech = research["tech_focus"]
        if "ai" in tech.lower() or "data" in tech.lower():
            parts.append(
                "\nYour investment in AI and data capabilities resonates with my "
                "recent work leading AI transformation at Grain Ecosystem."
            )

    if parts:
        return "\n".join(parts)

    return "[Personalize this section based on company research]"


def generate_cover_letter(
    job: Job,
    output_path: Path | None = None,
    research_path: Path | None = None,
) -> str:
    """Generate a cover letter for a job application.

    Args:
        job: The job to apply for (must have raw_description)
        output_path: Optional path to save the letter
        research_path: Optional path to research.md for personalization

    Returns:
        The cover letter content as markdown
    """
    profile = load_profile()
    resume = load_resume()

    # Load research if provided
    research = load_research(research_path) if research_path else None

    letter = generate_cover_letter_prompt(job, profile, resume, research)

    if output_path:
        output_path.write_text(letter, encoding="utf-8")

    return letter
