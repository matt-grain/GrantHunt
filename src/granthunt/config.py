from pathlib import Path

import yaml
from pydantic import BaseModel


class IndustryPrefs(BaseModel):
    preferred: list[str]
    avoid: list[str]


class TechFocus(BaseModel):
    must_have: list[str]
    nice_to_have: list[str]


class CompanySize(BaseModel):
    min: int
    preferred: str


class JobProfile(BaseModel):
    name: str
    location: str
    target_roles: list[str]
    company_size: CompanySize
    industries: IndustryPrefs
    tech_focus: TechFocus
    anti_patterns: list[str]
    work_arrangement: list[str]
    keywords_boost: list[str]
    keywords_avoid: list[str]


def get_project_root() -> Path:
    """Get the project root directory.

    Looks for job_profile.yaml in current directory or parent directories.
    """
    cwd = Path.cwd()

    # Check current directory and parents
    for directory in [cwd, *cwd.parents]:
        if (directory / "job_profile.yaml").exists():
            return directory
        if (directory / "pyproject.toml").exists():
            return directory

    return cwd


def load_profile(path: Path | None = None) -> JobProfile:
    """Load and validate job profile from YAML file.

    Args:
        path: Path to the YAML file. Defaults to job_profile.yaml in project root.

    Returns:
        Validated JobProfile model.

    Raises:
        FileNotFoundError: If the profile file does not exist.
    """
    if path is None:
        path = get_project_root() / "job_profile.yaml"

    if not path.exists():
        raise FileNotFoundError(
            f"Job profile not found at {path}. "
            "Please create a job_profile.yaml file with your preferences."
        )

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return JobProfile.model_validate(data)
