"""Integration tests for commit execution."""

import subprocess
from datetime import date
from pathlib import Path

import pytest

from contriband.git import apply_plan, execute_commits
from contriband.git.apply import get_commit_timestamps
from contriband.planner import DayPlan, Plan


def init_git_repo(path: Path) -> None:
    """Initialize a git repo with initial commit."""
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    # Create initial commit
    (path / "init.txt").write_text("init")
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial commit"],
        cwd=path,
        check=True,
        capture_output=True,
    )


class TestGetCommitTimestamps:
    """Tests for timestamp spreading logic."""

    def test_single_commit_at_noon(self):
        """Single commit should be at noon UTC."""
        day = DayPlan(date=date(2024, 1, 7), level=1, commits=1)
        timestamps = get_commit_timestamps(day)

        assert len(timestamps) == 1
        assert timestamps[0].hour == 12
        assert timestamps[0].minute == 0

    def test_multiple_commits_spread(self):
        """Multiple commits should be spread 5 minutes apart."""
        day = DayPlan(date=date(2024, 1, 7), level=4, commits=3)
        timestamps = get_commit_timestamps(day)

        assert len(timestamps) == 3
        assert timestamps[0].hour == 12
        assert timestamps[0].minute == 0
        assert timestamps[1].minute == 5
        assert timestamps[2].minute == 10

    def test_custom_spacing(self):
        """Custom spacing should be respected."""
        day = DayPlan(date=date(2024, 1, 7), level=4, commits=3)
        timestamps = get_commit_timestamps(day, commit_spacing_minutes=10)

        assert len(timestamps) == 3
        assert timestamps[0].minute == 0
        assert timestamps[1].minute == 10
        assert timestamps[2].minute == 20

    def test_zero_commits_empty(self):
        """Zero commits should return empty list."""
        day = DayPlan(date=date(2024, 1, 7), level=0, commits=0)
        timestamps = get_commit_timestamps(day)

        assert timestamps == []


class TestExecuteCommits:
    """Integration tests for execute_commits function."""

    @pytest.fixture
    def git_repo(self, tmp_path: Path) -> Path:
        """Create a temporary git repository."""
        init_git_repo(tmp_path)
        return tmp_path

    def test_creates_commits(self, git_repo: Path):
        """Commits are created in the repository."""
        plan = Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 7),
            week_start="SUNDAY",
            days=[DayPlan(date=date(2024, 1, 7), level=2, commits=3)],
        )

        result = execute_commits(plan, git_repo)

        assert result.success is True
        assert result.commits_created == 3

    def test_creates_log_file(self, git_repo: Path):
        """contriband.log file is created with entries."""
        plan = Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 7),
            week_start="SUNDAY",
            days=[DayPlan(date=date(2024, 1, 7), level=2, commits=2)],
        )

        execute_commits(plan, git_repo)

        log_file = git_repo / "contriband.log"
        assert log_file.exists()
        content = log_file.read_text()
        assert "level=2 commit=1" in content
        assert "level=2 commit=2" in content

    def test_commits_have_correct_dates(self, git_repo: Path):
        """Commits have backdated timestamps."""
        plan = Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 7),
            week_start="SUNDAY",
            days=[DayPlan(date=date(2024, 1, 7), level=1, commits=1)],
        )

        execute_commits(plan, git_repo)

        # Check git log for the date
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ai"],
            cwd=git_repo,
            capture_output=True,
            text=True,
            check=True,
        )
        assert "2024-01-07" in result.stdout

    def test_commit_messages_formatted(self, git_repo: Path):
        """Commit messages follow expected format."""
        plan = Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 7),
            week_start="SUNDAY",
            days=[DayPlan(date=date(2024, 1, 7), level=4, commits=2)],
        )

        execute_commits(plan, git_repo)

        # Check commit messages
        result = subprocess.run(
            ["git", "log", "--format=%s", "-n", "2"],
            cwd=git_repo,
            capture_output=True,
            text=True,
            check=True,
        )
        messages = result.stdout.strip().split("\n")
        assert "contribart: pixel at 2024-01-07" in messages[0]
        assert "level 4" in messages[0]
        assert "commit 2/2" in messages[0]

    def test_multiple_days(self, git_repo: Path):
        """Multiple days create correct number of commits."""
        plan = Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 8),
            week_start="SUNDAY",
            days=[
                DayPlan(date=date(2024, 1, 7), level=1, commits=1),
                DayPlan(date=date(2024, 1, 8), level=2, commits=3),
            ],
        )

        result = execute_commits(plan, git_repo)

        assert result.success is True
        assert result.commits_created == 4

    def test_skips_zero_commit_days(self, git_repo: Path):
        """Days with 0 commits are skipped."""
        plan = Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 9),
            week_start="SUNDAY",
            days=[
                DayPlan(date=date(2024, 1, 7), level=4, commits=2),
                DayPlan(date=date(2024, 1, 8), level=0, commits=0),
                DayPlan(date=date(2024, 1, 9), level=1, commits=1),
            ],
        )

        result = execute_commits(plan, git_repo)

        assert result.success is True
        assert result.commits_created == 3


class TestApplyPlanIntegration:
    """Integration tests for full apply_plan flow."""

    @pytest.fixture
    def clean_repo(self, tmp_path: Path) -> Path:
        """Create a clean git repository."""
        init_git_repo(tmp_path)
        return tmp_path

    @pytest.fixture
    def dirty_repo(self, tmp_path: Path) -> Path:
        """Create a git repository with uncommitted changes."""
        init_git_repo(tmp_path)
        (tmp_path / "dirty.txt").write_text("uncommitted")
        return tmp_path

    def test_apply_to_clean_repo(self, clean_repo: Path):
        """Apply succeeds on clean repo."""
        plan = Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 7),
            week_start="SUNDAY",
            days=[DayPlan(date=date(2024, 1, 7), level=1, commits=2)],
        )

        result = apply_plan(plan, clean_repo, dry_run=False)

        assert result.success is True
        assert result.commits_created == 2

    def test_apply_to_dirty_repo_fails(self, dirty_repo: Path):
        """Apply fails on dirty repo without allow_dirty."""
        plan = Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 7),
            week_start="SUNDAY",
            days=[DayPlan(date=date(2024, 1, 7), level=1, commits=1)],
        )

        result = apply_plan(plan, dirty_repo, dry_run=False)

        assert result.success is False
        assert "uncommitted" in result.errors[0].lower()

    def test_apply_to_dirty_repo_with_allow_dirty(self, dirty_repo: Path):
        """Apply succeeds on dirty repo with allow_dirty=True."""
        plan = Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 7),
            week_start="SUNDAY",
            days=[DayPlan(date=date(2024, 1, 7), level=1, commits=1)],
        )

        result = apply_plan(plan, dirty_repo, dry_run=False, allow_dirty=True)

        assert result.success is True
        assert result.commits_created == 1

    def test_dry_run_does_not_create_commits(self, clean_repo: Path):
        """Dry run mode doesn't create any commits."""
        plan = Plan(
            template_name="test",
            start_date=date(2024, 1, 7),
            end_date=date(2024, 1, 7),
            week_start="SUNDAY",
            days=[DayPlan(date=date(2024, 1, 7), level=4, commits=12)],
        )

        # Count commits before
        before = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=clean_repo,
            capture_output=True,
            text=True,
            check=True,
        )
        before_count = int(before.stdout.strip())

        result = apply_plan(plan, clean_repo, dry_run=True)

        # Count commits after
        after = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=clean_repo,
            capture_output=True,
            text=True,
            check=True,
        )
        after_count = int(after.stdout.strip())

        assert result.dry_run is True
        assert result.commits_created == 12  # Reports what would be created
        assert before_count == after_count  # But no actual commits
