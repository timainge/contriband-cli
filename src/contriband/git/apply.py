"""Apply commit plans to repositories."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

from contriband.planner.model import DayPlan, Plan

from .runner import GitError, RepoStatus, check_repo_status, run_git


@dataclass
class ApplyResult:
    """Result of applying a plan.

    Attributes:
        commits_created: Number of commits created
        dry_run: Whether this was a dry run
        errors: List of error messages
    """

    commits_created: int = 0
    dry_run: bool = False
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Whether the apply was successful (no errors)."""
        return len(self.errors) == 0


def apply_plan(
    plan: Plan,
    repo_path: Path,
    dry_run: bool = False,
    allow_dirty: bool = False,
) -> ApplyResult:
    """Apply a commit plan to a repository.

    Args:
        plan: The plan to apply
        repo_path: Path to the target git repository
        dry_run: If True, only simulate without creating commits
        allow_dirty: If True, allow applying to dirty working tree

    Returns:
        ApplyResult with commit count and any errors
    """
    result = ApplyResult(dry_run=dry_run)

    # Validate repo path
    if not repo_path.exists():
        result.errors.append(f"Repository path does not exist: {repo_path}")
        return result

    git_dir = repo_path / ".git"
    if not git_dir.exists():
        result.errors.append(f"Not a git repository: {repo_path}")
        return result

    if dry_run:
        # In dry-run mode, just count what would be created
        result.commits_created = plan.total_commits
        return result

    # Check repo status
    status = check_repo_status(repo_path)
    if not status.is_valid:
        result.errors.extend(status.errors)
        return result

    if not status.is_clean and not allow_dirty:
        result.errors.append(
            "Working tree has uncommitted changes. Use --allow-dirty to override."
        )
        return result

    # Execute commits
    return execute_commits(plan, repo_path)


def get_commit_timestamps(day: DayPlan, commit_spacing_minutes: int = 5) -> list[datetime]:
    """Generate timestamps for commits on a given day.

    Spreads commits across the day starting at 12:00:00 UTC,
    with configurable spacing between commits.

    Args:
        day: DayPlan with date and commit count
        commit_spacing_minutes: Minutes between each commit

    Returns:
        List of datetime objects for each commit
    """
    if day.commits == 0:
        return []

    # Start at noon UTC
    base_time = datetime(
        day.date.year,
        day.date.month,
        day.date.day,
        12,
        0,
        0,
        tzinfo=timezone.utc,
    )

    timestamps = []
    for i in range(day.commits):
        timestamp = base_time + timedelta(minutes=i * commit_spacing_minutes)
        timestamps.append(timestamp)

    return timestamps


def execute_commits(plan: Plan, repo_path: Path) -> ApplyResult:
    """Execute actual commits for a plan.

    Creates backdated commits by:
    1. Appending a line to contriband.log
    2. Staging the file
    3. Committing with GIT_AUTHOR_DATE and GIT_COMMITTER_DATE

    Args:
        plan: The plan to execute
        repo_path: Path to the target git repository

    Returns:
        ApplyResult with commit count and any errors
    """
    result = ApplyResult(dry_run=False)
    log_file = repo_path / "contriband.log"

    # Process each day with commits
    for day in plan.days:
        if day.commits == 0:
            continue

        timestamps = get_commit_timestamps(day)

        for i, timestamp in enumerate(timestamps, start=1):
            # Format timestamp for git (ISO 8601)
            timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%S%z")

            # Log entry format: 2024-01-07T12:00:00Z pixel level=4 commit=1
            log_entry = (
                f"{timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')} "
                f"pixel level={day.level} commit={i}\n"
            )

            # Append to log file
            with open(log_file, "a") as f:
                f.write(log_entry)

            # Stage the file
            try:
                run_git(["add", "contriband.log"], cwd=repo_path)
            except GitError as e:
                result.errors.append(f"Failed to stage: {e}")
                return result

            # Commit with backdated timestamp
            commit_msg = (
                f"contribart: pixel at {day.date} (level {day.level}, commit {i}/{day.commits})"
            )
            env = {
                "GIT_AUTHOR_DATE": timestamp_str,
                "GIT_COMMITTER_DATE": timestamp_str,
            }

            try:
                run_git(["commit", "-m", commit_msg], cwd=repo_path, env=env)
                result.commits_created += 1
            except GitError as e:
                result.errors.append(f"Failed to commit: {e}")
                return result

    return result


def get_dry_run_summary(plan: Plan, repo_path: Path) -> str:
    """Generate a human-readable dry-run summary.

    Args:
        plan: The plan to summarize
        repo_path: Target repository path

    Returns:
        Formatted summary string
    """
    lines = [
        f"Dry run for: {plan.template_name}",
        f"Repository: {repo_path}",
        f"Date range: {plan.start_date} to {plan.end_date}",
        "",
        f"Would create {plan.total_commits} commits:",
    ]

    # Show first 10 days with commits
    days_with_commits = [d for d in plan.days if d.commits > 0]
    shown = 0
    for day in days_with_commits[:10]:
        lines.append(f"  {day.date}: {day.commits} commits (level {day.level})")
        shown += 1

    if len(days_with_commits) > 10:
        lines.append(f"  ... [{len(days_with_commits) - shown} more days]")

    lines.append("")
    lines.append("No changes made (dry run).")

    return "\n".join(lines)
