# contriband

CLI tool to paint GitHub contribution grids. Create art on your contribution graph by generating backdated commits.

## Install

```bash
pip install -e .
```

For image-to-template support:

```bash
pip install -e ".[images]"
```

## Quick Start

```bash
# Render text as a template
contriband text "HELLO" --output hello.toml

# Preview in terminal
contriband show hello.toml

# Generate a commit plan
contriband plan hello.toml --repo /path/to/repo

# Apply commits (dry-run first)
contriband apply plan.json --dry-run
contriband apply plan.json
```

## Commands

| Command | Description |
|---------|-------------|
| `text` | Convert text to a pixel template using built-in 5x7 font |
| `show` | Render a template in the terminal (Rich) or as SVG |
| `plan` | Generate a date-based commit plan from a template |
| `apply` | Execute commits from a plan file |
| `config` | Show current configuration |

## Template Format

Templates are 7 rows (weekdays, Sunday=top) by N columns (weeks). Each cell is an intensity level 0-4.

**Text format** (`.txt`):
```
0 0 1 1 0
0 1 0 0 1
0 1 0 0 0
0 1 0 0 0
0 1 0 0 1
0 0 1 1 0
0 0 0 0 0
```

**TOML format** (`.toml`):
```toml
[meta]
anchor_date = "2025-02-02"
columns = 52
rows = 7

[grid]
row0 = [0, 0, 1, 1, 0]
row1 = [0, 1, 0, 0, 1]
# ...
```

## Configuration

Config is loaded from `./contriband.toml` or `~/.config/contriband/config.toml`.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src/
```
