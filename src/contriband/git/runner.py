"""Git command runner utilities."""

import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RepoStatus:
    """Status of a git repository.

    Attributes:
        is_valid: Whether the path is a valid git repository
        is_clean: Whether the working tree has no uncommitted changes
        current_branch: Name of the current branch
        errors: List of error messages if any checks failed
    """

    is_valid: bool = False
    is_clean: bool = False
    current_branch: str = ""
    errors: list[str] = field(default_factory=list)


class GitError(Exception):
    """Error running a git command."""

    pass


def run_git(
    args: list[str],
    cwd: Path,
    env: dict[str, str] | None = None,
) -> str:
    """Run a git command and return output.

    Args:
        args: Git command arguments (without 'git' prefix)
        cwd: Working directory for the command
        env: Optional environment variables to add

    Returns:
        Command stdout as string

    Raises:
        GitError: If the command fails
    """
    import os

    cmd = ["git"] + args

    # Merge environment
    full_env = os.environ.copy()
    if env:
        full_env.update(env)

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=full_env,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        raise GitError(f"git {args[0]} failed: {error_msg}") from e


def check_repo_status(repo_path: Path) -> RepoStatus:
    """Check if repo is valid and clean.

    Args:
        repo_path: Path to check

    Returns:
        RepoStatus with validity and cleanliness info
    """
    status = RepoStatus()

    # Check path exists
    if not repo_path.exists():
        status.errors.append(f"Path does not exist: {repo_path}")
        return status

    # Check it's a git repo
    git_dir = repo_path / ".git"
    if not git_dir.exists():
        status.errors.append(f"Not a git repository: {repo_path}")
        return status

    status.is_valid = True

    # Get current branch
    try:
        status.current_branch = run_git(
            ["rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path,
        )
    except GitError as e:
        status.errors.append(str(e))
        return status

    # Check working tree status
    try:
        output = run_git(["status", "--porcelain"], cwd=repo_path)
        status.is_clean = output == ""
        if not status.is_clean:
            status.errors.append("Working tree has uncommitted changes")
    except GitError as e:
        status.errors.append(str(e))

    return status
