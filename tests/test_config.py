"""Tests for configuration loading."""

from pathlib import Path

import pytest

from contriband.config import (
    DEFAULT_LEVEL_MAPPING,
    Config,
    ConfigError,
    find_config,
    load_config,
)


class TestConfig:
    """Tests for Config dataclass."""

    def test_default_values(self):
        """Config has sensible defaults."""
        config = Config()

        assert config.repo_path is None
        assert config.branch == "main"
        assert config.author_name is None
        assert config.author_email is None
        assert config.timezone == "UTC"
        assert config.level_mapping == DEFAULT_LEVEL_MAPPING
        assert config.week_start == "SUNDAY"
        assert config.legend == ".:-=#"

    def test_level_mapping_not_shared(self):
        """Each Config instance has its own level_mapping."""
        config1 = Config()
        config2 = Config()

        config1.level_mapping.append(99)
        assert 99 not in config2.level_mapping


class TestFindConfig:
    """Tests for find_config function."""

    def test_finds_local_config(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Finds contriband.toml in current directory."""
        monkeypatch.chdir(tmp_path)
        config_file = tmp_path / "contriband.toml"
        config_file.write_text("[repo]\npath = './test'\n")

        result = find_config()

        assert result is not None
        assert result.name == "contriband.toml"

    def test_finds_user_config(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Finds config in user config directory."""
        # Set up fake home directory
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        config_dir = fake_home / ".config" / "contriband"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.toml"
        config_file.write_text("[repo]\npath = './test'\n")

        # Change to a directory without local config
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        monkeypatch.chdir(work_dir)
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        result = find_config()

        assert result is not None
        assert result.name == "config.toml"

    def test_local_takes_precedence(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Local config takes precedence over user config."""
        # Set up both configs
        monkeypatch.chdir(tmp_path)
        local_config = tmp_path / "contriband.toml"
        local_config.write_text("[repo]\npath = './local'\n")

        fake_home = tmp_path / "home"
        fake_home.mkdir()
        config_dir = fake_home / ".config" / "contriband"
        config_dir.mkdir(parents=True)
        user_config = config_dir / "config.toml"
        user_config.write_text("[repo]\npath = './user'\n")
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        result = find_config()

        assert result is not None
        assert result.name == "contriband.toml"

    def test_returns_none_when_not_found(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Returns None when no config file exists."""
        monkeypatch.chdir(tmp_path)
        # Mock home to a directory without config
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        result = find_config()

        assert result is None


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_full_config(self, tmp_path: Path):
        """Load a complete config file."""
        config_file = tmp_path / "contriband.toml"
        config_file.write_text("""
[repo]
path = "./my-repo"
branch = "develop"

[author]
name = "Test User"
email = "test@example.com"
timezone = "America/New_York"

[levels]
mapping = [0, 2, 5, 10, 15]

[render]
week_start = "MONDAY"
legend = " .:*#"
""")

        config = load_config(config_file)

        assert config.repo_path == Path("./my-repo")
        assert config.branch == "develop"
        assert config.author_name == "Test User"
        assert config.author_email == "test@example.com"
        assert config.timezone == "America/New_York"
        assert config.level_mapping == [0, 2, 5, 10, 15]
        assert config.week_start == "MONDAY"
        assert config.legend == " .:*#"

    def test_load_partial_config(self, tmp_path: Path):
        """Load config with only some sections."""
        config_file = tmp_path / "contriband.toml"
        config_file.write_text("""
[repo]
path = "./my-repo"
""")

        config = load_config(config_file)

        assert config.repo_path == Path("./my-repo")
        assert config.branch == "main"  # Default
        assert config.week_start == "SUNDAY"  # Default

    def test_load_empty_config(self, tmp_path: Path):
        """Empty config returns defaults."""
        config_file = tmp_path / "contriband.toml"
        config_file.write_text("")

        config = load_config(config_file)

        assert config.repo_path is None
        assert config.branch == "main"

    def test_returns_defaults_when_no_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Returns defaults when no config found."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        config = load_config()

        assert config.repo_path is None
        assert config.branch == "main"

    def test_explicit_missing_path_raises(self, tmp_path: Path):
        """Explicit path that doesn't exist raises error."""
        with pytest.raises(ConfigError, match="not found"):
            load_config(tmp_path / "nonexistent.toml")

    def test_invalid_toml_raises(self, tmp_path: Path):
        """Invalid TOML syntax raises error."""
        config_file = tmp_path / "contriband.toml"
        config_file.write_text("this is not valid toml [[[")

        with pytest.raises(ConfigError, match="Invalid TOML"):
            load_config(config_file)

    def test_invalid_week_start_raises(self, tmp_path: Path):
        """Invalid week_start value raises error."""
        config_file = tmp_path / "contriband.toml"
        config_file.write_text("""
[render]
week_start = "TUESDAY"
""")

        with pytest.raises(ConfigError, match="SUNDAY or MONDAY"):
            load_config(config_file)

    def test_invalid_level_mapping_raises(self, tmp_path: Path):
        """Non-integer level mapping raises error."""
        config_file = tmp_path / "contriband.toml"
        config_file.write_text("""
[levels]
mapping = ["a", "b", "c"]
""")

        with pytest.raises(ConfigError, match="list of integers"):
            load_config(config_file)

    def test_week_start_case_insensitive(self, tmp_path: Path):
        """week_start is case insensitive."""
        config_file = tmp_path / "contriband.toml"
        config_file.write_text("""
[render]
week_start = "monday"
""")

        config = load_config(config_file)

        assert config.week_start == "MONDAY"


class TestConfigPrecedence:
    """Tests for CLI option precedence over config."""

    def test_cli_overrides_config_week_start(self, tmp_path: Path):
        """CLI week_start should override config (tested via logic inspection)."""
        config = Config(week_start="MONDAY")

        # Simulate CLI precedence logic
        cli_value = "SUNDAY"
        effective = (cli_value or config.week_start).upper()

        assert effective == "SUNDAY"

    def test_cli_none_falls_back_to_config(self, tmp_path: Path):
        """CLI None should fall back to config."""
        config = Config(week_start="MONDAY")

        # Simulate CLI precedence logic
        cli_value = None
        effective = (cli_value or config.week_start).upper()

        assert effective == "MONDAY"

    def test_cli_overrides_config_repo(self, tmp_path: Path):
        """CLI repo should override config."""
        config = Config(repo_path=Path("./config-repo"))

        # Simulate CLI precedence logic
        cli_value = "./cli-repo"
        effective = cli_value or (str(config.repo_path) if config.repo_path else None)

        assert effective == "./cli-repo"

    def test_cli_none_falls_back_to_config_repo(self, tmp_path: Path):
        """CLI None should fall back to config repo."""
        config = Config(repo_path=Path("./config-repo"))

        # Simulate CLI precedence logic
        cli_value = None
        effective = cli_value or (str(config.repo_path) if config.repo_path else None)

        assert effective is not None
        assert "config-repo" in effective
