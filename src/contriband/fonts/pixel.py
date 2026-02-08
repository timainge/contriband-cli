"""5x7 pixel font for text-to-template rendering."""

from __future__ import annotations

from contriband.templates.model import DEFAULT_LEGEND, Template

# 5x7 pixel font data: each character maps to 7 rows of 5-character patterns
# '#' = filled pixel, '.' = empty pixel
FONT_5X7: dict[str, list[str]] = {
    "A": [
        ".###.",
        "#...#",
        "#...#",
        "#####",
        "#...#",
        "#...#",
        "#...#",
    ],
    "B": [
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#...#",
        "#...#",
        "####.",
    ],
    "C": [
        ".###.",
        "#...#",
        "#....",
        "#....",
        "#....",
        "#...#",
        ".###.",
    ],
    "D": [
        "####.",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "####.",
    ],
    "E": [
        "#####",
        "#....",
        "#....",
        "####.",
        "#....",
        "#....",
        "#####",
    ],
    "F": [
        "#####",
        "#....",
        "#....",
        "####.",
        "#....",
        "#....",
        "#....",
    ],
    "G": [
        ".###.",
        "#...#",
        "#....",
        "#.###",
        "#...#",
        "#...#",
        ".###.",
    ],
    "H": [
        "#...#",
        "#...#",
        "#...#",
        "#####",
        "#...#",
        "#...#",
        "#...#",
    ],
    "I": [
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "#####",
    ],
    "J": [
        "..###",
        "...#.",
        "...#.",
        "...#.",
        "#..#.",
        "#..#.",
        ".##..",
    ],
    "K": [
        "#...#",
        "#..#.",
        "#.#..",
        "##...",
        "#.#..",
        "#..#.",
        "#...#",
    ],
    "L": [
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#####",
    ],
    "M": [
        "#...#",
        "##.##",
        "#.#.#",
        "#.#.#",
        "#...#",
        "#...#",
        "#...#",
    ],
    "N": [
        "#...#",
        "##..#",
        "#.#.#",
        "#..##",
        "#...#",
        "#...#",
        "#...#",
    ],
    "O": [
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
    ],
    "P": [
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#....",
        "#....",
        "#....",
    ],
    "Q": [
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        "#.#.#",
        "#..#.",
        ".##.#",
    ],
    "R": [
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#.#..",
        "#..#.",
        "#...#",
    ],
    "S": [
        ".####",
        "#....",
        "#....",
        ".###.",
        "....#",
        "....#",
        "####.",
    ],
    "T": [
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ],
    "U": [
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
    ],
    "V": [
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
    ],
    "W": [
        "#...#",
        "#...#",
        "#...#",
        "#.#.#",
        "#.#.#",
        "##.##",
        "#...#",
    ],
    "X": [
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
        ".#.#.",
        "#...#",
        "#...#",
    ],
    "Y": [
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ],
    "Z": [
        "#####",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        "#....",
        "#####",
    ],
    # Digits
    "0": [
        ".###.",
        "#...#",
        "#..##",
        "#.#.#",
        "##..#",
        "#...#",
        ".###.",
    ],
    "1": [
        "..#..",
        ".##..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        ".###.",
    ],
    "2": [
        ".###.",
        "#...#",
        "....#",
        "..##.",
        ".#...",
        "#....",
        "#####",
    ],
    "3": [
        ".###.",
        "#...#",
        "....#",
        "..##.",
        "....#",
        "#...#",
        ".###.",
    ],
    "4": [
        "...#.",
        "..##.",
        ".#.#.",
        "#..#.",
        "#####",
        "...#.",
        "...#.",
    ],
    "5": [
        "#####",
        "#....",
        "####.",
        "....#",
        "....#",
        "#...#",
        ".###.",
    ],
    "6": [
        ".###.",
        "#....",
        "#....",
        "####.",
        "#...#",
        "#...#",
        ".###.",
    ],
    "7": [
        "#####",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        ".#...",
        ".#...",
    ],
    "8": [
        ".###.",
        "#...#",
        "#...#",
        ".###.",
        "#...#",
        "#...#",
        ".###.",
    ],
    "9": [
        ".###.",
        "#...#",
        "#...#",
        ".####",
        "....#",
        "....#",
        ".###.",
    ],
    # Punctuation
    " ": [
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
    ],
    "!": [
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        ".....",
        "..#..",
    ],
    "?": [
        ".###.",
        "#...#",
        "....#",
        "..##.",
        "..#..",
        ".....",
        "..#..",
    ],
    ".": [
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        "..#..",
    ],
    ",": [
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        "..#..",
        ".#...",
    ],
    "-": [
        ".....",
        ".....",
        ".....",
        "#####",
        ".....",
        ".....",
        ".....",
    ],
    "+": [
        ".....",
        "..#..",
        "..#..",
        "#####",
        "..#..",
        "..#..",
        ".....",
    ],
    ":": [
        ".....",
        "..#..",
        ".....",
        ".....",
        ".....",
        "..#..",
        ".....",
    ],
    "'": [
        "..#..",
        "..#..",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
    ],
    "/": [
        "....#",
        "...#.",
        "...#.",
        "..#..",
        ".#...",
        ".#...",
        "#....",
    ],
    "#": [
        ".#.#.",
        ".#.#.",
        "#####",
        ".#.#.",
        "#####",
        ".#.#.",
        ".#.#.",
    ],
    "*": [
        ".....",
        "#.#.#",
        ".###.",
        "#####",
        ".###.",
        "#.#.#",
        ".....",
    ],
    "<": [
        "...#.",
        "..#..",
        ".#...",
        "#....",
        ".#...",
        "..#..",
        "...#.",
    ],
    ">": [
        ".#...",
        "..#..",
        "...#.",
        "....#",
        "...#.",
        "..#..",
        ".#...",
    ],
}

# Character used for unknown/unsupported characters (box)
FALLBACK_CHAR: list[str] = [
    "#####",
    "#...#",
    "#...#",
    "#...#",
    "#...#",
    "#...#",
    "#####",
]


class FontError(Exception):
    """Error during font rendering."""


def get_char_pattern(char: str) -> list[str]:
    """Get the 5x7 pattern for a character.

    Args:
        char: Single character to look up

    Returns:
        List of 7 strings, each 5 characters wide

    Note:
        Unknown characters return the fallback pattern (box outline)
    """
    return FONT_5X7.get(char.upper(), FALLBACK_CHAR)


def render_text(text: str, spacing: int = 1) -> Template:
    """Render text string to a Template using pixel font.

    Args:
        text: Text string to render (A-Z, 0-9, punctuation supported)
        spacing: Number of empty columns between characters (default 1)

    Returns:
        Template with the rendered text as a 7-row grid

    Raises:
        FontError: If text is empty
    """
    if not text:
        raise FontError("Text cannot be empty")

    # Build the grid by combining character patterns
    grid: list[list[int]] = [[] for _ in range(7)]

    for i, char in enumerate(text):
        pattern = get_char_pattern(char)

        # Add spacing between characters (not before first)
        if i > 0:
            for _ in range(spacing):
                for row_idx in range(7):
                    grid[row_idx].append(0)

        # Add character pattern columns
        for row_idx, row_pattern in enumerate(pattern):
            for pixel in row_pattern:
                # '#' = level 4 (full intensity), '.' = level 0 (empty)
                grid[row_idx].append(4 if pixel == "#" else 0)

    width = len(grid[0]) if grid[0] else 0

    return Template(
        name=f"text-{text[:20]}",  # Truncate long names
        grid=grid,
        width=width,
        height=7,
        legend=DEFAULT_LEGEND.copy(),
    )


def template_to_txt(template: Template) -> str:
    """Convert a Template to TXT format string.

    Args:
        template: Template to convert

    Returns:
        String in TXT template format (7 lines of chars)
    """
    # Reverse legend: level -> char
    level_to_char = {v: k for k, v in template.legend.items() if k != " "}
    # Ensure we have mappings for all levels
    level_to_char.setdefault(0, ".")
    level_to_char.setdefault(4, "#")

    lines = []
    for row in template.grid:
        line = "".join(level_to_char.get(level, ".") for level in row)
        lines.append(line)

    return "\n".join(lines)
