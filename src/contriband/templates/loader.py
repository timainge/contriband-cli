"""Template loading and parsing."""

import warnings
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[import-not-found]

from .errors import TemplateError
from .model import DEFAULT_LEGEND, Template

EXPECTED_ROWS = 7


def load_template(path: Path | str) -> Template:
    """Load a template from a file (auto-detects .txt or .toml).

    Args:
        path: Path to the template file

    Returns:
        Parsed Template object

    Raises:
        TemplateError: If file cannot be read or parsed
    """
    path = Path(path)

    if not path.exists():
        raise TemplateError(f"Template file not found: {path}")

    try:
        content = path.read_text()
    except OSError as e:
        raise TemplateError(f"Failed to read template file: {e}") from e

    # Detect format by extension
    if path.suffix.lower() == ".toml":
        template = parse_toml_template(content, name=path.stem)
    else:
        template = parse_txt_template(content, name=path.stem)

    return template


def parse_toml_template(
    content: str,
    name: str = "unnamed",
) -> Template:
    """Parse TOML template content into a Template.

    Args:
        content: Raw TOML content
        name: Default template name (used if not specified in file)

    Returns:
        Parsed Template object

    Raises:
        TemplateError: If TOML is invalid or missing required sections
    """
    try:
        data = tomllib.loads(content)
    except tomllib.TOMLDecodeError as e:
        raise TemplateError(f"Invalid TOML: {e}") from e

    # Get template metadata
    template_section = data.get("template", {})
    template_name = template_section.get("name", name)

    # Get legend (optional)
    legend_section = data.get("legend", {})
    legend_chars = legend_section.get("chars", ".:-=#")

    # Build legend dict from chars string (position = level)
    legend: dict[str, int] = {}
    for level, char in enumerate(legend_chars):
        legend[char] = level
    # Always include space as level 0
    if " " not in legend:
        legend[" "] = 0

    # Get grid data (required)
    grid_section = data.get("grid", {})
    grid_data = grid_section.get("data")

    if grid_data is None:
        raise TemplateError("Missing [grid] section with 'data' field")

    # Parse grid using existing logic
    return _parse_grid_content(grid_data, legend, template_name)


def _parse_grid_content(
    content: str,
    legend: dict[str, int],
    name: str,
) -> Template:
    """Parse grid content string into a Template.

    Args:
        content: Grid content (7 lines)
        legend: Character-to-level mapping
        name: Template name

    Returns:
        Parsed Template object

    Raises:
        TemplateError: If content is invalid
    """
    # Split and filter empty lines
    lines = [line for line in content.strip().split("\n") if line.strip()]

    if not lines:
        raise TemplateError("Grid data is empty")

    if len(lines) != EXPECTED_ROWS:
        raise TemplateError(
            f"Grid must have exactly {EXPECTED_ROWS} rows (one per weekday), "
            f"got {len(lines)}"
        )

    # Find max width
    max_width = max(len(line) for line in lines)

    if max_width == 0:
        raise TemplateError("Grid has no content (all lines are empty)")

    # Parse each line into levels
    grid: list[list[int]] = []
    for row_idx, line in enumerate(lines):
        row: list[int] = []
        for col_idx, char in enumerate(line):
            if char in legend:
                row.append(legend[char])
            else:
                warnings.warn(
                    f"Unknown character '{char}' at row {row_idx + 1}, col {col_idx + 1}; "
                    "treating as level 0",
                    stacklevel=3,
                )
                row.append(0)

        # Pad shorter lines with level 0
        while len(row) < max_width:
            row.append(0)

        grid.append(row)

    return Template(
        name=name,
        grid=grid,
        width=max_width,
        height=EXPECTED_ROWS,
        legend=legend,
    )


def parse_txt_template(
    content: str,
    legend: dict[str, int] | None = None,
    name: str = "unnamed",
) -> Template:
    """Parse ASCII template content into a Template.

    Args:
        content: Raw text content with 7 lines representing weekdays
        legend: Character-to-level mapping (uses DEFAULT_LEGEND if None)
        name: Template name

    Returns:
        Parsed Template object

    Raises:
        TemplateError: If content is empty or has wrong number of rows
    """
    if legend is None:
        legend = DEFAULT_LEGEND.copy()

    lines = content.strip().split("\n")

    if not lines or (len(lines) == 1 and not lines[0]):
        raise TemplateError("Template is empty")

    if len(lines) != EXPECTED_ROWS:
        raise TemplateError(
            f"Template must have exactly {EXPECTED_ROWS} rows (one per weekday), "
            f"got {len(lines)}"
        )

    # Find max width
    max_width = max(len(line) for line in lines)

    if max_width == 0:
        raise TemplateError("Template has no content (all lines are empty)")

    # Parse each line into levels
    grid: list[list[int]] = []
    for row_idx, line in enumerate(lines):
        row: list[int] = []
        for col_idx, char in enumerate(line):
            if char in legend:
                row.append(legend[char])
            else:
                warnings.warn(
                    f"Unknown character '{char}' at row {row_idx + 1}, col {col_idx + 1}; "
                    "treating as level 0",
                    stacklevel=2,
                )
                row.append(0)

        # Pad shorter lines with level 0
        while len(row) < max_width:
            row.append(0)

        grid.append(row)

    return Template(
        name=name,
        grid=grid,
        width=max_width,
        height=EXPECTED_ROWS,
        legend=legend,
    )
