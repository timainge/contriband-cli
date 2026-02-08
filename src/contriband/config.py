"""Configuration file loading for contriband."""

from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[import-not-found]

DEFAULT_LEVEL_MAPPING = [0, 1, 3, 7, 12]


class ConfigError(Exception):
    """Error loading or parsing config file."""

    pass


@dataclass
class Config:
    """Configuration settings for contriband.

    Attributes:
        repo_path: Default target repository path
        branch: Default branch name
        author_name: Git author name
        author_email: Git author email
        timezone: Timezone for commit timestamps
        level_mapping: Mapping of levels to commit counts
        week_start: Day to start weeks (SUNDAY or MONDAY)
        legend: Character legend for templates
    """

    repo_path: Path | None = None
    branch: str = "main"
    author_name: str | None = None
    author_email: str | None = None
    timezone: str = "UTC"
    level_mapping: list[int] = field(default_factory=lambda: DEFAULT_LEVEL_MAPPING.copy())
    week_start: str = "SUNDAY"
    legend: str = ".:-=#"


def find_config() -> Path | None:
    """Find config file in standard locations.

    Search order:
    1. ./contriband.toml (current directory)
    2. ~/.config/contriband/config.toml

    Returns:
        Path to config file if found, None otherwise
    """
    # Check current directory
    local_config = Path("contriband.toml")
    if local_config.exists():
        return local_config

    # Check user config directory
    user_config = Path.home() / ".config" / "contriband" / "config.toml"
    if user_config.exists():
        return user_config

    return None


def load_config(path: Path | None = None) -> Config:
    """Load config from TOML file.

    Args:
        path: Explicit path to config file, or None to auto-discover

    Returns:
        Config object with loaded settings

    Raises:
        ConfigError: If config file exists but cannot be parsed
    """
    config = Config()

    # Find config file
    config_path = path or find_config()
    if config_path is None:
        return config  # Return defaults

    if not config_path.exists():
        if path is not None:
            # Explicit path was given but doesn't exist
            raise ConfigError(f"Config file not found: {config_path}")
        return config  # Auto-discovered path doesn't exist

    # Load TOML
    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"Invalid TOML in {config_path}: {e}") from e

    # Parse sections
    if "repo" in data:
        repo = data["repo"]
        if "path" in repo:
            config.repo_path = Path(repo["path"])
        if "branch" in repo:
            config.branch = repo["branch"]

    if "author" in data:
        author = data["author"]
        if "name" in author:
            config.author_name = author["name"]
        if "email" in author:
            config.author_email = author["email"]
        if "timezone" in author:
            config.timezone = author["timezone"]

    if "levels" in data:
        levels = data["levels"]
        if "mapping" in levels:
            mapping = levels["mapping"]
            if not isinstance(mapping, list) or not all(isinstance(x, int) for x in mapping):
                raise ConfigError("levels.mapping must be a list of integers")
            config.level_mapping = mapping

    if "render" in data:
        render = data["render"]
        if "week_start" in render:
            week_start = render["week_start"].upper()
            if week_start not in ("SUNDAY", "MONDAY"):
                raise ConfigError(f"render.week_start must be SUNDAY or MONDAY, got {week_start}")
            config.week_start = week_start
        if "legend" in render:
            config.legend = render["legend"]

    return config
