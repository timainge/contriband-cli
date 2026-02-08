# Contributing to contriband-cli

Thanks for your interest. Here's how to get involved.

Before starting work on a PR, please [open an issue](https://github.com/timainge/contriband-cli/issues) to discuss what you have in mind. This helps avoid duplicated effort and makes sure the change fits the project direction.

## Fonts

The easiest way to contribute is by adding new font glyphs. Glyphs live in `src/contriband/fonts/` as 7-row pixel arrays with intensity levels 0-4.

When adding a glyph:
- Keep it within 7 rows (matching the contribution graph)
- Use all intensity levels where it makes sense
- Name it clearly

## Planned Features

The following features are stubbed out or partially wired but not yet implemented:

- **Image-to-template conversion** — load an image and convert it to a 7-row contribution grid template. A good starting point would be a command like `contriband image photo.png --output template.toml` that resizes, grayscales, and quantises an image to intensity levels 0-4 using Pillow.

If you're interested in tackling one of these or have ideas for other features, open an issue and let's discuss.

## Development

```bash
pip install -e ".[dev]"
pre-commit install      # Set up pre-commit hooks
pytest                  # Run tests
ruff check src/         # Lint
```

## Pull requests

- Keep changes focused — one feature or fix per PR
- Pre-commit hooks run `ruff` and `pytest` automatically before each commit
- Describe what you changed and why
