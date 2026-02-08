"""Tests for SVG rendering."""

import pytest

from contriband.render.svg import (
    DEFAULT_CELL_SIZE,
    DEFAULT_CORNER_RADIUS,
    DEFAULT_GAP,
    GITHUB_COLORS,
    render_template_svg,
)
from contriband.templates.model import Template


def make_template(grid: list[list[int]], name: str = "test") -> Template:
    """Helper to create a Template for testing."""
    return Template(
        name=name,
        grid=grid,
        width=len(grid[0]) if grid else 0,
        height=len(grid),
    )


class TestRenderTemplateSvg:
    """Tests for render_template_svg function."""

    def test_returns_string(self):
        """Returns a string."""
        grid = [[0] * 3 for _ in range(7)]
        template = make_template(grid)
        result = render_template_svg(template)
        assert isinstance(result, str)

    def test_valid_svg_structure(self):
        """Output is valid SVG structure."""
        grid = [[0] * 3 for _ in range(7)]
        template = make_template(grid)
        result = render_template_svg(template)

        assert result.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
        assert result.endswith("</svg>")

    def test_contains_viewbox(self):
        """SVG contains viewBox attribute."""
        grid = [[0] * 3 for _ in range(7)]
        template = make_template(grid)
        result = render_template_svg(template)

        assert 'viewBox="0 0' in result

    def test_cell_count_matches_grid(self):
        """Number of cell rects matches grid size."""
        grid = [[0, 4, 0], [4, 0, 4], [0, 4, 0], [4, 0, 4], [0, 4, 0], [4, 0, 4], [0, 4, 0]]
        template = make_template(grid)
        result = render_template_svg(template)

        # Count rects (excluding background rect)
        # Background has larger rx value
        cell_rects = result.count(f'rx="{DEFAULT_CORNER_RADIUS}"')
        expected_cells = 7 * 3  # 7 rows x 3 columns
        assert cell_rects == expected_cells

    def test_uses_github_colors(self):
        """Cells use GitHub contribution colors."""
        # Grid with all levels
        grid = [[0, 1, 2, 3, 4] for _ in range(7)]
        template = make_template(grid)
        result = render_template_svg(template)

        for level, color in GITHUB_COLORS.items():
            assert color in result, f"Missing color for level {level}"

    def test_custom_cell_size(self):
        """Custom cell size affects dimensions."""
        grid = [[0] * 3 for _ in range(7)]
        template = make_template(grid)

        result_small = render_template_svg(template, cell_size=10)
        result_large = render_template_svg(template, cell_size=20)

        # Large should have bigger dimensions
        assert 'width="10"' in result_small
        assert 'width="20"' in result_large

    def test_background_can_be_disabled(self):
        """Background rectangle can be disabled."""
        grid = [[0] * 3 for _ in range(7)]
        template = make_template(grid)

        with_bg = render_template_svg(template, show_background=True)
        without_bg = render_template_svg(template, show_background=False)

        # Background rect has larger corner radius
        assert f'rx="{DEFAULT_CORNER_RADIUS * 2}"' in with_bg
        assert f'rx="{DEFAULT_CORNER_RADIUS * 2}"' not in without_bg

    def test_dimensions_scale_with_grid(self):
        """SVG dimensions scale with grid size."""
        small_grid = [[0] * 5 for _ in range(7)]
        large_grid = [[0] * 20 for _ in range(7)]

        small_template = make_template(small_grid)
        large_template = make_template(large_grid)

        small_svg = render_template_svg(small_template)
        large_svg = render_template_svg(large_template)

        # Extract width from viewBox
        import re

        small_match = re.search(r'width="(\d+)"', small_svg)
        large_match = re.search(r'width="(\d+)"', large_svg)

        assert small_match and large_match
        assert int(large_match.group(1)) > int(small_match.group(1))

    def test_level_0_uses_empty_color(self):
        """Level 0 cells use the empty/gray color."""
        grid = [[0] * 3 for _ in range(7)]
        template = make_template(grid)
        result = render_template_svg(template)

        assert GITHUB_COLORS[0] in result

    def test_level_4_uses_brightest_color(self):
        """Level 4 cells use the brightest green color."""
        grid = [[4] * 3 for _ in range(7)]
        template = make_template(grid)
        result = render_template_svg(template)

        assert GITHUB_COLORS[4] in result


class TestSvgIntegration:
    """Integration tests for SVG rendering."""

    def test_single_column(self):
        """Can render a single-column template."""
        grid = [[0], [1], [2], [3], [4], [3], [2]]
        template = make_template(grid)
        result = render_template_svg(template)

        assert "</svg>" in result

    def test_wide_template(self):
        """Can render a wide template."""
        grid = [[i % 5 for i in range(52)] for _ in range(7)]  # Full year
        template = make_template(grid)
        result = render_template_svg(template)

        assert "</svg>" in result
        # Should have 52 * 7 = 364 cells
        cell_count = result.count(f'rx="{DEFAULT_CORNER_RADIUS}"/')
        # Each cell rect ends with rx="2"/>

    def test_all_zeros(self):
        """Can render an all-empty template."""
        grid = [[0] * 10 for _ in range(7)]
        template = make_template(grid)
        result = render_template_svg(template)

        assert "</svg>" in result
        # All cells should be empty color
        assert GITHUB_COLORS[0] in result

    def test_all_fours(self):
        """Can render an all-filled template."""
        grid = [[4] * 10 for _ in range(7)]
        template = make_template(grid)
        result = render_template_svg(template)

        assert "</svg>" in result
        # All cells should be brightest color
        assert GITHUB_COLORS[4] in result
