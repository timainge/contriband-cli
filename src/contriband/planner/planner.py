"""Plan generation from templates."""

from datetime import date, timedelta

from contriband.templates.model import Template

from .model import DEFAULT_LEVEL_MAPPING, DayPlan, Plan

# Weekday constants (Python's date.weekday(): Monday=0, Sunday=6)
SUNDAY = 6
MONDAY = 0


def _get_week_start_offset(week_start: str) -> int:
    """Get the weekday offset for the given week start.

    Args:
        week_start: "SUNDAY" or "MONDAY"

    Returns:
        Python weekday value (0=Monday, 6=Sunday)
    """
    if week_start.upper() == "SUNDAY":
        return SUNDAY
    return MONDAY


def _align_to_week_start(d: date, week_start: str) -> date:
    """Align a date to the start of its week.

    Args:
        d: Date to align
        week_start: "SUNDAY" or "MONDAY"

    Returns:
        Date of the week's first day
    """
    target_weekday = _get_week_start_offset(week_start)

    if week_start.upper() == "SUNDAY":
        # For Sunday start: Sunday=0, Monday=1, ..., Saturday=6
        # Python weekday: Monday=0, ..., Sunday=6
        # Convert: (weekday + 1) % 7 gives Sunday=0
        days_since_start = (d.weekday() + 1) % 7
    else:
        # For Monday start: Monday=0, ..., Sunday=6 (matches Python)
        days_since_start = d.weekday()

    return d - timedelta(days=days_since_start)


def create_plan(
    template: Template,
    start_date: date,
    week_start: str = "SUNDAY",
    level_mapping: list[int] | None = None,
) -> Plan:
    """Generate a commit plan from a template.

    Args:
        template: Template to plan
        start_date: The date to start the plan (will be aligned to week start)
        week_start: Day the week starts ("SUNDAY" or "MONDAY")
        level_mapping: Mapping from levels (0-4) to commit counts

    Returns:
        Plan object with all daily commit plans
    """
    if level_mapping is None:
        level_mapping = DEFAULT_LEVEL_MAPPING.copy()

    week_start = week_start.upper()
    if week_start not in ("SUNDAY", "MONDAY"):
        raise ValueError(f"week_start must be 'SUNDAY' or 'MONDAY', got '{week_start}'")

    # Align start date to week boundary
    aligned_start = _align_to_week_start(start_date, week_start)

    days: list[DayPlan] = []

    # Iterate through template: columns are weeks, rows are days
    for col_idx in range(template.width):
        week_start_date = aligned_start + timedelta(weeks=col_idx)

        for row_idx in range(template.height):
            day_date = week_start_date + timedelta(days=row_idx)
            level = template.grid[row_idx][col_idx]

            # Map level to commit count
            commits = level_mapping[level] if level < len(level_mapping) else 0

            days.append(DayPlan(date=day_date, level=level, commits=commits))

    # Calculate end date
    end_date = days[-1].date if days else aligned_start

    return Plan(
        template_name=template.name,
        start_date=aligned_start,
        end_date=end_date,
        week_start=week_start,
        days=days,
        level_mapping=level_mapping,
    )
