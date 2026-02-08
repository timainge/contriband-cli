"""SVG rendering for templates."""

from __future__ import annotations

from contriband.templates.model import Template

# GitHub contribution grid colors (dark theme) - same as terminal.py
GITHUB_COLORS: dict[int, str] = {
    0: "#161b22",  # Empty/gray
    1: "#0e4429",  # Light green
    2: "#006d32",  # Medium green
    3: "#26a641",  # Bright green
    4: "#39d353",  # Brightest green
}

# Default styling
DEFAULT_CELL_SIZE = 12
DEFAULT_GAP = 3
DEFAULT_CORNER_RADIUS = 2
BACKGROUND_COLOR = "#0d1117"  # GitHub dark background


def render_template_svg(
    template: Template,
    cell_size: int = DEFAULT_CELL_SIZE,
    gap: int = DEFAULT_GAP,
    corner_radius: int = DEFAULT_CORNER_RADIUS,
    show_background: bool = True,
) -> str:
    """Render template to SVG string.

    Args:
        template: Template to render
        cell_size: Size of each cell in pixels
        gap: Gap between cells in pixels
        corner_radius: Corner radius for rounded rectangles
        show_background: Whether to show background rectangle

    Returns:
        SVG string
    """
    # Calculate dimensions
    width = template.width * (cell_size + gap) - gap
    height = template.height * (cell_size + gap) - gap

    # Add padding
    padding = gap * 2
    svg_width = width + padding * 2
    svg_height = height + padding * 2

    # Build SVG
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">',
    ]

    # Background
    if show_background:
        lines.append(
            f'  <rect width="{svg_width}" height="{svg_height}" fill="{BACKGROUND_COLOR}" rx="{corner_radius * 2}"/>'
        )

    # Render cells
    for row_idx, row in enumerate(template.grid):
        for col_idx, level in enumerate(row):
            x = padding + col_idx * (cell_size + gap)
            y = padding + row_idx * (cell_size + gap)
            color = GITHUB_COLORS.get(level, GITHUB_COLORS[0])

            lines.append(
                f'  <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
                f'fill="{color}" rx="{corner_radius}"/>'
            )

    lines.append("</svg>")

    return "\n".join(lines)
