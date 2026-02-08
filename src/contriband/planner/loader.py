"""Load plans from JSON files."""

import json
from datetime import date
from pathlib import Path

from .model import DEFAULT_LEVEL_MAPPING, DayPlan, Plan


class PlanLoadError(Exception):
    """Raised when plan loading fails."""


def load_plan(path: Path | str) -> Plan:
    """Load a plan from a JSON file.

    Args:
        path: Path to the JSON plan file

    Returns:
        Parsed Plan object

    Raises:
        PlanLoadError: If file cannot be read or parsed
    """
    path = Path(path)

    if not path.exists():
        raise PlanLoadError(f"Plan file not found: {path}")

    try:
        content = path.read_text()
        data = json.loads(content)
    except (OSError, json.JSONDecodeError) as e:
        raise PlanLoadError(f"Failed to read plan file: {e}") from e

    return parse_plan_json(data)


def parse_plan_json(data: dict) -> Plan:
    """Parse a plan from JSON data.

    Args:
        data: Dictionary from JSON

    Returns:
        Plan object

    Raises:
        PlanLoadError: If required fields are missing or invalid
    """
    try:
        days = [
            DayPlan(
                date=date.fromisoformat(day["date"]),
                level=day["level"],
                commits=day["commits"],
            )
            for day in data.get("days", [])
        ]

        return Plan(
            template_name=data.get("template", "unknown"),
            start_date=date.fromisoformat(data["start_date"]),
            end_date=date.fromisoformat(data["end_date"]),
            week_start=data.get("week_start", "SUNDAY"),
            days=days,
            level_mapping=data.get("level_mapping", DEFAULT_LEVEL_MAPPING.copy()),
        )
    except (KeyError, ValueError, TypeError) as e:
        raise PlanLoadError(f"Invalid plan format: {e}") from e
