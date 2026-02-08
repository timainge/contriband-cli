"""Tests for git runner utilities."""

import subprocess
from pathlib import Path

import pytest

from contriband.git import GitError, check_repo_status, run_git


class TestRunGit:
    """Tests for run_git function."""

    def test_run_simple_command(self, tmp_path: Path):
        """Run a simple git command."""
        # Initialize a git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        output = run_git(["status", "--porcelain"], cwd=tmp_path)
        assert output == ""  # Clean repo

    def test_run_with_output(self, tmp_path: Path):
        """Command output is returned."""
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        # Need a commit to have a branch
        (tmp_path / "test.txt").write_text("test")
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        output = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=tmp_path)
        # Could be main, master, or other default branch
        assert output in ("main", "master")

    def test_run_with_env(self, tmp_path: Path):
        """Environment variables are passed to git."""
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Create a file and commit
        (tmp_path / "test.txt").write_text("test")
        run_git(["add", "test.txt"], cwd=tmp_path)

        # Commit with custom date via env
        env = {
            "GIT_AUTHOR_DATE": "2024-01-07T12:00:00+0000",
            "GIT_COMMITTER_DATE": "2024-01-07T12:00:00+0000",
        }
        run_git(["commit", "-m", "test commit"], cwd=tmp_path, env=env)

        # Verify the date was used
        log = run_git(["log", "-1", "--format=%ai"], cwd=tmp_path)
        assert "2024-01-07" in log

    def test_invalid_command_raises(self, tmp_path: Path):
        """Invalid git command raises GitError."""
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        with pytest.raises(GitError, match="failed"):
            run_git(["invalid-command"], cwd=tmp_path)


class TestCheckRepoStatus:
    """Tests for check_repo_status function."""

    def test_valid_clean_repo(self, tmp_path: Path):
        """Valid repo with no changes."""
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        # Need at least one commit for branch to exist
        (tmp_path / "init.txt").write_text("init")
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        status = check_repo_status(tmp_path)

        assert status.is_valid is True
        assert status.is_clean is True
        assert status.current_branch in ("main", "master")
        assert len(status.errors) == 0

    def test_dirty_repo(self, tmp_path: Path):
        """Repo with uncommitted changes."""
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        # Create initial commit
        (tmp_path / "init.txt").write_text("init")
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

        # Create uncommitted change
        (tmp_path / "dirty.txt").write_text("dirty")

        status = check_repo_status(tmp_path)

        assert status.is_valid is True
        assert status.is_clean is False
        assert "uncommitted" in status.errors[0].lower()

    def test_nonexistent_path(self, tmp_path: Path):
        """Non-existent path returns invalid status."""
        status = check_repo_status(tmp_path / "nonexistent")

        assert status.is_valid is False
        assert "does not exist" in status.errors[0]

    def test_not_a_repo(self, tmp_path: Path):
        """Non-repo directory returns invalid status."""
        status = check_repo_status(tmp_path)

        assert status.is_valid is False
        assert "Not a git repository" in status.errors[0]
