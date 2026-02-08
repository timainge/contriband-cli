"""Data models for commit plans."""

from dataclasses import dataclass, field
from datetime import date

# Default level-to-commits mapping
DEFAULT_LEVEL_MAPPING: list[int] = [0, 1, 3, 7, 12]


@dataclass
class DayPlan:
    """A single day's commit plan.

    Attributes:
        date: The date for commits
        level: Intensity level (0-4)
        commits: Number of commits to create
    """

    date: date
    level: int
    commits: int


@dataclass
class Plan:
    """A complete commit plan for a template.

    Attributes:
        template_name: Name of the source template
        start_date: First date in the plan
        end_date: Last date in the plan
        week_start: Day the week starts ("SUNDAY" or "MONDAY")
        days: List of daily commit plans
        level_mapping: Mapping from levels to commit counts
    """

    template_name: str
    start_date: date
    end_date: date
    week_start: str
    days: list[DayPlan]
    level_mapping: list[int] = field(default_factory=lambda: DEFAULT_LEVEL_MAPPING.copy())

    @property
    def total_commits(self) -> int:
        """Total number of commits in the plan."""
        return sum(day.commits for day in self.days)

    @property
    def total_days(self) -> int:
        """Total number of days with commits."""
        return len([day for day in self.days if day.commits > 0])
