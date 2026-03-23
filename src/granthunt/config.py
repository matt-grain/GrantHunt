from pathlib import Path

import yaml
from pydantic import BaseModel


class StartupInfo(BaseModel):
    name: str
    description: str
    industry: str
    stage: str  # seed, pre-seed, series-a, growth
    location: str
    founded_year: int | None = None
    employees: int | None = None
    website: str | None = None


class EligibilityCriteria(BaseModel):
    sectors: list[str]
    activities: list[str]
    certifications: list[str] = []


class FundingPrefs(BaseModel):
    min_amount: float | None = None
    max_amount: float | None = None
    types: list[str]  # grant, tax_credit, loan, equity


class GrantProfile(BaseModel):
    startup: StartupInfo
    eligibility: EligibilityCriteria
    funding_prefs: FundingPrefs
    keywords_boost: list[str]
    keywords_avoid: list[str]


def get_project_root() -> Path:
    """Get the project root directory.

    Looks for grant_profile.yaml in current directory or parent directories.
    """
    cwd = Path.cwd()

    for directory in [cwd, *cwd.parents]:
        if (directory / "grant_profile.yaml").exists():
            return directory
        if (directory / "pyproject.toml").exists():
            return directory

    return cwd


def load_profile(path: Path | None = None) -> GrantProfile:
    """Load and validate grant profile from YAML file.

    Args:
        path: Path to the YAML file. Defaults to grant_profile.yaml in project root.

    Returns:
        Validated GrantProfile model.

    Raises:
        FileNotFoundError: If the profile file does not exist.
    """
    if path is None:
        path = get_project_root() / "grant_profile.yaml"

    if not path.exists():
        raise FileNotFoundError(
            f"Grant profile not found at {path}. "
            "Please create a grant_profile.yaml file with your startup's information."
        )

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return GrantProfile.model_validate(data)
