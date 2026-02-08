"""Rendering to terminal, SVG, PNG, HTML."""

from .svg import render_template_svg
from .terminal import GITHUB_COLORS, render_template, render_template_to_string

__all__ = [
    "GITHUB_COLORS",
    "render_template",
    "render_template_svg",
    "render_template_to_string",
]
