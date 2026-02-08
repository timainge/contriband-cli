# Claude Code Instructions

You are working on **contriband**, a CLI tool to paint GitHub contribution grids.

## Project Overview

Create art on GitHub contribution graphs by generating backdated commits. The CLI separates planning from execution for safety.

## Key Principles

1. **Safety first**: Never auto-push, require explicit `--repo`, support dry-run
2. **Separation of concerns**: Templates -> Plans -> Apply (each step is independent)
3. **Shell out to git**: Use subprocess, not GitPython, for reliability with date env vars
4. **Do simplest thing first**: Avoid over-engineering. Build the minimal version, iterate.

## Architecture

```
src/contriband/
├── cli.py           # Typer CLI - all commands defined here
├── config.py        # TOML config loading (contriband.toml)
├── templates/       # Template loading (txt, toml)
├── fonts/           # 5x7 pixel font for text-to-template
├── planner/         # Convert templates to date-based plans
├── git/             # Execute commits via subprocess
└── render/          # Terminal (Rich) and SVG output
```

## Commands

```bash
pytest                          # Run tests
ruff check src/                 # Lint
contriband --help               # CLI usage
```

## Implementation Notes

- Templates: 7 rows (weekdays) x N columns (weeks), levels 0-4
- Level mapping: `[0, 1, 3, 7, 12]` commits per level
- Commit message format: `"contribart: pixel at {date}"` (legacy name, intentional)
- Log file: `contriband.log` in target repo
- Config search: `./contriband.toml` then `~/.config/contriband/config.toml`
