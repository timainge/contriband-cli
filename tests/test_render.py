"""Tests for terminal rendering."""

import pytest

from contriband.render.terminal import (
    GITHUB_COLORS,
    WEEKDAY_LABELS,
    get_level_style,
    render_template_to_string,
)
from contriband.templates import Template


class TestGetLevelStyle:
    """Tests for get_level_style."""

    def test_returns_style_for_each_level(self):
        """Each level 0-4 should return a valid style."""
        for level in range(5):
            style = get_level_style(level)
            assert style is not None
            assert style.color is not None

    def test_unknown_level_defaults_to_zero(self):
        """Unknown levels should default to level 0 color."""
        style_unknown = get_level_style(99)
        style_zero = get_level_style(0)
        assert style_unknown.color == style_zero.color


class TestGitHubColors:
    """Tests for color palette."""

    def test_all_levels_have_colors(self):
        """Levels 0-4 should all have defined colors."""
        for level in range(5):
            assert level in GITHUB_COLORS
            assert GITHUB_COLORS[level].startswith("#")

    def test_colors_are_valid_hex(self):
        """All colors should be valid hex codes."""
        for color in GITHUB_COLORS.values():
            assert len(color) == 7
            assert color.startswith("#")
            # Should be valid hex
            int(color[1:], 16)


class TestWeekdayLabels:
    """Tests for weekday labels."""

    def test_seven_days(self):
        """Should have exactly 7 weekday labels."""
        assert len(WEEKDAY_LABELS) == 7

    def test_starts_with_sunday(self):
        """Labels should start with Sunday (GitHub style)."""
        assert WEEKDAY_LABELS[0] == "Sun"
        assert WEEKDAY_LABELS[6] == "Sat"


class TestRenderTemplate:
    """Tests for render_template."""

    @pytest.fixture
    def simple_template(self) -> Template:
        """Create a simple test template."""
        return Template(
            name="test",
            grid=[[4, 0] for _ in range(7)],
            width=2,
        )

    def test_includes_template_name(self, simple_template: Template):
        """Output should include template name."""
        output = render_template_to_string(simple_template)
        assert "test" in output

    def test_includes_dimensions(self, simple_template: Template):
        """Output should include grid dimensions."""
        output = render_template_to_string(simple_template)
        assert "2 columns" in output
        assert "7 rows" in output

    def test_includes_weekday_labels(self, simple_template: Template):
        """Output should include weekday labels when enabled."""
        output = render_template_to_string(simple_template, show_labels=True)
        assert "Sun" in output
        assert "Sat" in output

    def test_excludes_labels_when_disabled(self, simple_template: Template):
        """Output should not include weekday labels when disabled."""
        output = render_template_to_string(simple_template, show_labels=False)
        # Labels shouldn't appear at start of lines
        lines = output.strip().split("\n")
        # Skip header lines, check grid lines don't start with weekday
        grid_lines = [l for l in lines if "██" in l]
        for line in grid_lines:
            assert not line.strip().startswith("Sun")
            assert not line.strip().startswith("Mon")

    def test_renders_all_rows(self, simple_template: Template):
        """Should render all 7 rows."""
        output = render_template_to_string(simple_template)
        # Count lines with block characters
        block_lines = [l for l in output.split("\n") if "██" in l]
        assert len(block_lines) == 7
