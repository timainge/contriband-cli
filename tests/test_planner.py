"""Tests for plan generation."""

import csv
import json
from datetime import date
from pathlib import Path

import pytest

from contriband.planner import (
    DEFAULT_LEVEL_MAPPING,
    DayPlan,
    Plan,
    create_plan,
    export_plan_csv,
    export_plan_json,
)
from contriband.templates import Template


class TestDayPlan:
    """Tests for DayPlan dataclass."""

    def test_create_day_plan(self):
        """Create a simple day plan."""
        day = DayPlan(date=date(2024, 1, 7), level=4, commits=12)
        assert day.date == date(2024, 1, 7)
        assert day.level == 4
        assert day.commits == 12


class TestPlan:
    """Tests for Plan dataclass."""

    def test_total_commits(self):
        """Total commits should sum all day commits."""
        plan = Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 9),
            week_start="SUNDAY",
            days=[
                DayPlan(date=date(2024, 1, 7), level=4, commits=12),
                DayPlan(date=date(2024, 1, 8), level=2, commits=3),
                DayPlan(date=date(2024, 1, 9), level=0, commits=0),
            ],
        )
        assert plan.total_commits == 15

    def test_total_days(self):
        """Total days should count days with commits > 0."""
        plan = Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 9),
            week_start="SUNDAY",
            days=[
                DayPlan(date=date(2024, 1, 7), level=4, commits=12),
                DayPlan(date=date(2024, 1, 8), level=2, commits=3),
                DayPlan(date=date(2024, 1, 9), level=0, commits=0),
            ],
        )
        assert plan.total_days == 2


class TestCreatePlan:
    """Tests for create_plan function."""

    @pytest.fixture
    def simple_template(self) -> Template:
        """Create a simple 2-column template."""
        return Template(
            name="test",
            grid=[[4, 0] for _ in range(7)],  # First column all 4s, second all 0s
            width=2,
        )

    def test_creates_plan_with_correct_dates(self, simple_template: Template):
        """Plan should have correct start and end dates."""
        plan = create_plan(simple_template, date(2024, 1, 7))

        assert plan.start_date == date(2024, 1, 7)  # Sunday
        # 2 columns = 2 weeks = 14 days, starting Jan 7 ends Jan 20
        assert plan.end_date == date(2024, 1, 20)

    def test_aligns_to_sunday(self, simple_template: Template):
        """Start date should align to Sunday when week_start is SUNDAY."""
        # Jan 10, 2024 is Wednesday
        plan = create_plan(simple_template, date(2024, 1, 10), week_start="SUNDAY")

        # Should align back to Jan 7 (Sunday)
        assert plan.start_date == date(2024, 1, 7)

    def test_aligns_to_monday(self, simple_template: Template):
        """Start date should align to Monday when week_start is MONDAY."""
        # Jan 10, 2024 is Wednesday
        plan = create_plan(simple_template, date(2024, 1, 10), week_start="MONDAY")

        # Should align back to Jan 8 (Monday)
        assert plan.start_date == date(2024, 1, 8)

    def test_applies_level_mapping(self, simple_template: Template):
        """Commits should use level mapping."""
        plan = create_plan(simple_template, date(2024, 1, 7))

        # First week: all level 4 = 12 commits each
        first_week = plan.days[:7]
        for day in first_week:
            assert day.level == 4
            assert day.commits == 12

        # Second week: all level 0 = 0 commits each
        second_week = plan.days[7:]
        for day in second_week:
            assert day.level == 0
            assert day.commits == 0

    def test_custom_level_mapping(self, simple_template: Template):
        """Custom level mapping should be used."""
        custom_mapping = [0, 2, 4, 6, 8]
        plan = create_plan(
            simple_template, date(2024, 1, 7), level_mapping=custom_mapping
        )

        # Level 4 should map to 8 commits
        assert plan.days[0].commits == 8

    def test_invalid_week_start_raises(self, simple_template: Template):
        """Invalid week_start should raise ValueError."""
        with pytest.raises(ValueError, match="'SUNDAY' or 'MONDAY'"):
            create_plan(simple_template, date(2024, 1, 7), week_start="FRIDAY")

    def test_generates_correct_number_of_days(self, simple_template: Template):
        """Should generate 7 days per column."""
        plan = create_plan(simple_template, date(2024, 1, 7))

        # 2 columns * 7 rows = 14 days
        assert len(plan.days) == 14


class TestExportPlanJson:
    """Tests for JSON export."""

    def test_exports_valid_json(self, tmp_path: Path):
        """Exported file should be valid JSON."""
        plan = Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 8),
            week_start="SUNDAY",
            days=[
                DayPlan(date=date(2024, 1, 7), level=4, commits=12),
            ],
        )

        json_path = tmp_path / "plan.json"
        export_plan_json(plan, json_path)

        data = json.loads(json_path.read_text())
        assert data["template"] == "test"
        assert data["start_date"] == "2024-01-07"
        assert data["total_commits"] == 12
        assert len(data["days"]) == 1

    def test_creates_parent_directories(self, tmp_path: Path):
        """Should create parent directories if needed."""
        plan = Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 7),
            week_start="SUNDAY",
            days=[],
        )

        json_path = tmp_path / "nested" / "dir" / "plan.json"
        export_plan_json(plan, json_path)

        assert json_path.exists()


class TestExportPlanCsv:
    """Tests for CSV export."""

    def test_exports_valid_csv(self, tmp_path: Path):
        """Exported file should be valid CSV."""
        plan = Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 8),
            week_start="SUNDAY",
            days=[
                DayPlan(date=date(2024, 1, 7), level=4, commits=12),
                DayPlan(date=date(2024, 1, 8), level=2, commits=3),
            ],
        )

        csv_path = tmp_path / "plan.csv"
        export_plan_csv(plan, csv_path)

        with csv_path.open() as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["date"] == "2024-01-07"
        assert rows[0]["level"] == "4"
        assert rows[0]["commits"] == "12"

    def test_csv_has_header(self, tmp_path: Path):
        """CSV should have header row."""
        plan = Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 7),
            week_start="SUNDAY",
            days=[],
        )

        csv_path = tmp_path / "plan.csv"
        export_plan_csv(plan, csv_path)

        lines = csv_path.read_text().strip().split("\n")
        assert lines[0] == "date,level,commits"
