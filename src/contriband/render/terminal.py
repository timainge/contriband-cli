"""Terminal rendering using Rich."""

from rich.console import Console
from rich.style import Style
from rich.text import Text

from contriband.templates.model import Template

# GitHub contribution grid colors (dark theme)
GITHUB_COLORS: dict[int, str] = {
    0: "#161b22",  # Empty/gray
    1: "#0e4429",  # Light green
    2: "#006d32",  # Medium green
    3: "#26a641",  # Bright green
    4: "#39d353",  # Brightest green
}

# Weekday labels (Sunday first, matching GitHub's display)
WEEKDAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

# Block character for rendering
BLOCK_CHAR = "██"


def get_level_style(level: int) -> Style:
    """Return Rich Style for a given intensity level.

    Args:
        level: Intensity level (0-4)

    Returns:
        Rich Style with appropriate foreground color
    """
    color = GITHUB_COLORS.get(level, GITHUB_COLORS[0])
    return Style(color=color)


def render_template(
    template: Template,
    show_labels: bool = True,
    console: Console | None = None,
) -> None:
    """Render a template to the terminal using Rich.

    Args:
        template: Template to render
        show_labels: Whether to show weekday labels
        console: Rich Console to use (creates new one if None)
    """
    if console is None:
        console = Console()

    # Print header
    console.print(
        f"Template: [bold]{template.name}[/bold] "
        f"({template.width} columns x {template.height} rows)"
    )
    console.print()

    # Render each row
    for row_idx, row in enumerate(template.grid):
        line = Text()

        # Add weekday label
        if show_labels:
            label = WEEKDAY_LABELS[row_idx % 7]
            line.append(f"{label} ", style="dim")

        # Add colored blocks for each cell
        for level in row:
            style = get_level_style(level)
            line.append(BLOCK_CHAR, style=style)

        console.print(line)


def render_template_to_string(
    template: Template,
    show_labels: bool = True,
) -> str:
    """Render a template to a string (for testing).

    Args:
        template: Template to render
        show_labels: Whether to show weekday labels

    Returns:
        Rendered string output
    """
    console = Console(force_terminal=True, record=True)
    render_template(template, show_labels=show_labels, console=console)
    return console.export_text()
