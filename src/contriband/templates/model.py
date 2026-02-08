"""Data models for templates."""

from dataclasses import dataclass, field

# Default character-to-level mapping
DEFAULT_LEGEND: dict[str, int] = {
    ".": 0,
    " ": 0,
    "-": 1,
    ":": 2,
    "=": 3,
    "#": 4,
}


@dataclass
class Template:
    """A contribution grid template.

    Attributes:
        name: Template identifier (usually filename without extension)
        grid: 2D list of intensity levels (7 rows x W columns, values 0-4)
        width: Number of columns (weeks)
        height: Number of rows (always 7 for weekdays)
        legend: Character-to-level mapping used for parsing
    """

    name: str
    grid: list[list[int]]
    width: int
    height: int = 7
    legend: dict[str, int] = field(default_factory=lambda: DEFAULT_LEGEND.copy())

    def __post_init__(self) -> None:
        """Validate template dimensions."""
        if len(self.grid) != self.height:
            raise ValueError(f"Grid must have {self.height} rows, got {len(self.grid)}")
        if self.grid and len(self.grid[0]) != self.width:
            raise ValueError(f"Grid width mismatch: expected {self.width}, got {len(self.grid[0])}")
