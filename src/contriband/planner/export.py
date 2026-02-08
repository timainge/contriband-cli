"""Export plans to JSON and CSV formats."""

import csv
import json
from pathlib import Path

from .model import Plan


def export_plan_json(plan: Plan, path: Path) -> None:
    """Export plan to JSON file.

    Args:
        plan: Plan to export
        path: Output file path
    """
    data = {
        "template": plan.template_name,
        "start_date": plan.start_date.isoformat(),
        "end_date": plan.end_date.isoformat(),
        "week_start": plan.week_start,
        "total_commits": plan.total_commits,
        "total_days": plan.total_days,
        "level_mapping": plan.level_mapping,
        "days": [
            {
                "date": day.date.isoformat(),
                "level": day.level,
                "commits": day.commits,
            }
            for day in plan.days
        ],
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def export_plan_csv(plan: Plan, path: Path) -> None:
    """Export plan to CSV file.

    Args:
        plan: Plan to export
        path: Output file path
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "level", "commits"])

        for day in plan.days:
            writer.writerow([day.date.isoformat(), day.level, day.commits])


def plan_to_dict(plan: Plan) -> dict:
    """Convert plan to dictionary (for JSON serialization).

    Args:
        plan: Plan to convert

    Returns:
        Dictionary representation
    """
    return {
        "template": plan.template_name,
        "start_date": plan.start_date.isoformat(),
        "end_date": plan.end_date.isoformat(),
        "week_start": plan.week_start,
        "total_commits": plan.total_commits,
        "total_days": plan.total_days,
        "level_mapping": plan.level_mapping,
        "days": [
            {
                "date": day.date.isoformat(),
                "level": day.level,
                "commits": day.commits,
            }
            for day in plan.days
        ],
    }
