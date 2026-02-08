"""Tests for plan loading and apply functionality."""

import json
from datetime import date
from pathlib import Path

import pytest

from contriband.git import ApplyResult, apply_plan, get_dry_run_summary
from contriband.planner import DayPlan, Plan, PlanLoadError, load_plan


class TestLoadPlan:
    """Tests for load_plan function."""

    def test_load_valid_plan(self, tmp_path: Path):
        """Load a valid plan JSON file."""
        plan_data = {
            "template": "test",
            "start_date": "2024-01-07",
            "end_date": "2024-01-08",
            "week_start": "SUNDAY",
            "level_mapping": [0, 1, 3, 7, 12],
            "days": [
                {"date": "2024-01-07", "level": 4, "commits": 12},
                {"date": "2024-01-08", "level": 2, "commits": 3},
            ],
        }

        plan_file = tmp_path / "plan.json"
        plan_file.write_text(json.dumps(plan_data))

        plan = load_plan(plan_file)

        assert plan.template_name == "test"
        assert plan.start_date == date(2024, 1, 7)
        assert plan.end_date == date(2024, 1, 8)
        assert len(plan.days) == 2
        assert plan.days[0].commits == 12

    def test_load_missing_file_raises(self):
        """Missing file should raise PlanLoadError."""
        with pytest.raises(PlanLoadError, match="not found"):
            load_plan(Path("/nonexistent/plan.json"))

    def test_load_invalid_json_raises(self, tmp_path: Path):
        """Invalid JSON should raise PlanLoadError."""
        plan_file = tmp_path / "plan.json"
        plan_file.write_text("not valid json")

        with pytest.raises(PlanLoadError, match="Failed to read"):
            load_plan(plan_file)

    def test_load_missing_required_fields_raises(self, tmp_path: Path):
        """Missing required fields should raise PlanLoadError."""
        plan_data = {"template": "test"}  # Missing start_date, end_date

        plan_file = tmp_path / "plan.json"
        plan_file.write_text(json.dumps(plan_data))

        with pytest.raises(PlanLoadError, match="Invalid plan format"):
            load_plan(plan_file)

    def test_load_from_string_path(self, tmp_path: Path):
        """Accept string path as well as Path."""
        plan_data = {
            "template": "test",
            "start_date": "2024-01-07",
            "end_date": "2024-01-07",
            "days": [],
        }

        plan_file = tmp_path / "plan.json"
        plan_file.write_text(json.dumps(plan_data))

        plan = load_plan(str(plan_file))
        assert plan.template_name == "test"


class TestApplyResult:
    """Tests for ApplyResult dataclass."""

    def test_success_with_no_errors(self):
        """Success should be True when no errors."""
        result = ApplyResult(commits_created=10, dry_run=False)
        assert result.success is True

    def test_failure_with_errors(self):
        """Success should be False when errors exist."""
        result = ApplyResult(commits_created=0, errors=["Something went wrong"])
        assert result.success is False


class TestApplyPlan:
    """Tests for apply_plan function."""

    @pytest.fixture
    def simple_plan(self) -> Plan:
        """Create a simple test plan."""
        return Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 8),
            week_start="SUNDAY",
            days=[
                DayPlan(date=date(2024, 1, 7), level=4, commits=12),
                DayPlan(date=date(2024, 1, 8), level=2, commits=3),
            ],
        )

    def test_dry_run_returns_commit_count(self, simple_plan: Plan, tmp_path: Path):
        """Dry run should return total commits without creating them."""
        # Create a git repo
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        result = apply_plan(simple_plan, tmp_path, dry_run=True)

        assert result.dry_run is True
        assert result.commits_created == 15  # 12 + 3
        assert result.success is True

    def test_invalid_repo_path_returns_error(self, simple_plan: Plan, tmp_path: Path):
        """Non-existent repo path should return error."""
        result = apply_plan(simple_plan, tmp_path / "nonexistent", dry_run=True)

        assert result.success is False
        assert "does not exist" in result.errors[0]

    def test_not_a_git_repo_returns_error(self, simple_plan: Plan, tmp_path: Path):
        """Path without .git should return error."""
        result = apply_plan(simple_plan, tmp_path, dry_run=True)

        assert result.success is False
        assert "Not a git repository" in result.errors[0]


class TestGetDryRunSummary:
    """Tests for get_dry_run_summary function."""

    def test_includes_template_name(self):
        """Summary should include template name."""
        plan = Plan(
            template_name="my_template",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 7),
            week_start="SUNDAY",
            days=[],
        )

        summary = get_dry_run_summary(plan, Path("/repo"))
        assert "my_template" in summary

    def test_includes_date_range(self):
        """Summary should include date range."""
        plan = Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 2, 17),
            week_start="SUNDAY",
            days=[],
        )

        summary = get_dry_run_summary(plan, Path("/repo"))
        assert "2024-01-07" in summary
        assert "2024-02-17" in summary

    def test_includes_commit_count(self):
        """Summary should include total commit count."""
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

        summary = get_dry_run_summary(plan, Path("/repo"))
        assert "15 commits" in summary

    def test_shows_dry_run_notice(self):
        """Summary should indicate no changes were made."""
        plan = Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 7),
            week_start="SUNDAY",
            days=[],
        )

        summary = get_dry_run_summary(plan, Path("/repo"))
        assert "No changes made" in summary
        assert "dry run" in summary.lower()
