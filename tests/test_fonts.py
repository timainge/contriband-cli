"""Tests for font rendering."""

import pytest

from contriband.fonts import (
    FONT_5X7,
    FontError,
    get_char_pattern,
    render_text,
    template_to_txt,
)
from contriband.fonts.pixel import FALLBACK_CHAR


class TestFontData:
    """Tests for font data structure."""

    def test_all_chars_have_7_rows(self):
        """All font characters must have exactly 7 rows."""
        for char, pattern in FONT_5X7.items():
            assert len(pattern) == 7, f"Character '{char}' has {len(pattern)} rows, expected 7"

    def test_all_chars_have_5_cols(self):
        """All font characters must have exactly 5 columns."""
        for char, pattern in FONT_5X7.items():
            for row_idx, row in enumerate(pattern):
                assert len(row) == 5, f"Character '{char}' row {row_idx} has {len(row)} cols"

    def test_uppercase_letters_exist(self):
        """Font contains all uppercase letters A-Z."""
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            assert letter in FONT_5X7, f"Missing letter: {letter}"

    def test_digits_exist(self):
        """Font contains all digits 0-9."""
        for digit in "0123456789":
            assert digit in FONT_5X7, f"Missing digit: {digit}"

    def test_common_punctuation_exists(self):
        """Font contains common punctuation."""
        for punct in " !?.,:-+":
            assert punct in FONT_5X7, f"Missing punctuation: {punct}"

    def test_fallback_char_is_7x5(self):
        """Fallback character has correct dimensions."""
        assert len(FALLBACK_CHAR) == 7
        assert all(len(row) == 5 for row in FALLBACK_CHAR)


class TestGetCharPattern:
    """Tests for get_char_pattern function."""

    def test_get_known_char(self):
        """Known characters return their pattern."""
        pattern = get_char_pattern("A")
        assert pattern == FONT_5X7["A"]

    def test_lowercase_converted_to_upper(self):
        """Lowercase letters are converted to uppercase."""
        assert get_char_pattern("a") == get_char_pattern("A")

    def test_unknown_char_returns_fallback(self):
        """Unknown characters return the fallback pattern."""
        pattern = get_char_pattern("@")  # Not in font
        assert pattern == FALLBACK_CHAR

    def test_space_character(self):
        """Space character returns empty pattern."""
        pattern = get_char_pattern(" ")
        assert pattern == FONT_5X7[" "]
        # Space should be all dots (empty)
        assert all(row == "....." for row in pattern)


class TestRenderText:
    """Tests for render_text function."""

    def test_empty_text_raises_error(self):
        """Empty text raises FontError."""
        with pytest.raises(FontError, match="cannot be empty"):
            render_text("")

    def test_single_char_dimensions(self):
        """Single character renders to 7x5 grid."""
        template = render_text("A")
        assert template.height == 7
        assert template.width == 5
        assert len(template.grid) == 7
        assert all(len(row) == 5 for row in template.grid)

    def test_two_chars_with_spacing(self):
        """Two characters have correct width with spacing."""
        template = render_text("HI", spacing=1)
        # H (5) + spacing (1) + I (5) = 11
        assert template.width == 11

    def test_custom_spacing(self):
        """Custom spacing affects width."""
        template_s1 = render_text("HI", spacing=1)
        template_s2 = render_text("HI", spacing=2)
        template_s3 = render_text("HI", spacing=3)

        assert template_s1.width == 11  # 5 + 1 + 5
        assert template_s2.width == 12  # 5 + 2 + 5
        assert template_s3.width == 13  # 5 + 3 + 5

    def test_zero_spacing(self):
        """Zero spacing puts characters adjacent."""
        template = render_text("HI", spacing=0)
        assert template.width == 10  # 5 + 0 + 5

    def test_grid_values_are_0_or_4(self):
        """Grid values are either 0 (empty) or 4 (filled)."""
        template = render_text("HELLO")
        for row in template.grid:
            for cell in row:
                assert cell in (0, 4), f"Unexpected cell value: {cell}"

    def test_template_name_includes_text(self):
        """Template name is derived from text."""
        template = render_text("TEST")
        assert "TEST" in template.name

    def test_long_text_name_truncated(self):
        """Long text is truncated in template name."""
        template = render_text("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        assert len(template.name) < 30  # name should be truncated

    def test_lowercase_renders_as_uppercase(self):
        """Lowercase text renders same as uppercase."""
        lower = render_text("hello")
        upper = render_text("HELLO")
        assert lower.grid == upper.grid

    def test_known_pattern_renders_correctly(self):
        """Letter H renders with expected pattern."""
        template = render_text("H")
        # H pattern should have filled columns on left and right
        # and filled middle row
        # Row 0: #...# -> [4,0,0,0,4]
        assert template.grid[0] == [4, 0, 0, 0, 4]
        # Row 3 (middle): ##### -> [4,4,4,4,4]
        assert template.grid[3] == [4, 4, 4, 4, 4]


class TestTemplateToTxt:
    """Tests for template_to_txt function."""

    def test_converts_single_char(self):
        """Single character converts to 7-line string."""
        template = render_text("I")
        txt = template_to_txt(template)
        lines = txt.split("\n")
        assert len(lines) == 7

    def test_level_4_becomes_hash(self):
        """Level 4 cells become # in output."""
        template = render_text("I")
        txt = template_to_txt(template)
        # "I" has # in top row
        assert "#" in txt

    def test_level_0_becomes_dot(self):
        """Level 0 cells become . in output."""
        template = render_text("I")
        txt = template_to_txt(template)
        assert "." in txt

    def test_roundtrip_dimensions(self):
        """Template -> TXT preserves dimensions."""
        template = render_text("HELLO")
        txt = template_to_txt(template)
        lines = txt.split("\n")
        assert len(lines) == 7
        assert all(len(line) == template.width for line in lines)


class TestRenderTextIntegration:
    """Integration tests for text rendering."""

    def test_hello_world(self):
        """Can render HELLO WORLD."""
        template = render_text("HELLO WORLD")
        assert template.height == 7
        assert template.width > 50  # Long text

    def test_digits_render(self):
        """Can render digits."""
        template = render_text("2024")
        assert template.height == 7

    def test_punctuation_renders(self):
        """Can render punctuation."""
        template = render_text("HI!")
        assert template.height == 7

    def test_unknown_char_uses_fallback(self):
        """Unknown characters render with fallback (box)."""
        template = render_text("@")  # Not in font
        assert template.height == 7
        assert template.width == 5
        # Fallback is a box - top row should be all filled
        assert template.grid[0] == [4, 4, 4, 4, 4]
