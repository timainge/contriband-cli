"""Tests for template loading and parsing."""

from pathlib import Path

import pytest

from contriband.templates.errors import TemplateError
from contriband.templates.loader import load_template, parse_toml_template, parse_txt_template
from contriband.templates.model import DEFAULT_LEGEND, Template


class TestParseTemplate:
    """Tests for parse_txt_template."""

    def test_parse_simple_template(self):
        """Parse a basic 7-row template."""
        content = """\
##..##
##..##
######
##..##
##..##
##..##
......"""
        template = parse_txt_template(content)

        assert template.height == 7
        assert template.width == 6
        assert len(template.grid) == 7
        assert all(len(row) == 6 for row in template.grid)

    def test_parse_levels_correctly(self):
        """Verify character-to-level mapping."""
        content = """\
.#
.#
.#
.#
.#
.#
.#"""
        template = parse_txt_template(content)

        # First column should be all 0s, second column all 4s
        for row in template.grid:
            assert row[0] == 0
            assert row[1] == 4

    def test_parse_all_legend_characters(self):
        """Test all default legend characters."""
        content = """\
.-:=#
.-:=#
.-:=#
.-:=#
.-:=#
.-:=#
.-:=#"""
        template = parse_txt_template(content)

        for row in template.grid:
            assert row == [0, 1, 2, 3, 4]

    def test_pad_shorter_lines(self):
        """Shorter lines should be padded with level 0."""
        content = """\
###
##
#
###
##
#
###"""
        template = parse_txt_template(content)

        assert template.width == 3
        assert template.grid[0] == [4, 4, 4]
        assert template.grid[1] == [4, 4, 0]
        assert template.grid[2] == [4, 0, 0]

    def test_empty_template_raises(self):
        """Empty content should raise TemplateError."""
        with pytest.raises(TemplateError, match="empty"):
            parse_txt_template("")

    def test_wrong_row_count_raises(self):
        """Templates with != 7 rows should raise."""
        content = """\
##
##
##"""
        with pytest.raises(TemplateError, match="7 rows"):
            parse_txt_template(content)

    def test_unknown_character_warns(self):
        """Unknown characters should warn and default to level 0."""
        content = """\
#X#
...
...
...
...
...
..."""
        with pytest.warns(UserWarning, match="Unknown character 'X'"):
            template = parse_txt_template(content)

        assert template.grid[0][1] == 0

    def test_custom_legend(self):
        """Custom legend should override default."""
        content = """\
AB
AB
AB
AB
AB
AB
AB"""
        legend = {"A": 1, "B": 3}
        template = parse_txt_template(content, legend=legend)

        for row in template.grid:
            assert row == [1, 3]

    def test_template_name(self):
        """Template should have provided name."""
        content = """\
#
#
#
#
#
#
#"""
        template = parse_txt_template(content, name="test")
        assert template.name == "test"


class TestLoadTemplate:
    """Tests for load_template from file."""

    def test_load_existing_file(self, tmp_path: Path):
        """Load a template from an existing file."""
        template_file = tmp_path / "test.txt"
        template_file.write_text("""\
##..##
##..##
######
##..##
##..##
##..##
......""")

        template = load_template(template_file)

        assert template.name == "test"
        assert template.width == 6
        assert template.height == 7

    def test_load_missing_file_raises(self):
        """Missing file should raise TemplateError."""
        with pytest.raises(TemplateError, match="not found"):
            load_template(Path("/nonexistent/path.txt"))

    def test_load_from_string_path(self, tmp_path: Path):
        """Accept string path as well as Path."""
        template_file = tmp_path / "test.txt"
        template_file.write_text("""\
#
#
#
#
#
#
#""")

        template = load_template(str(template_file))
        assert template.name == "test"


class TestTemplateModel:
    """Tests for Template dataclass."""

    def test_template_validation(self):
        """Template should validate dimensions."""
        # Valid template
        Template(
            name="test",
            grid=[[0] * 5 for _ in range(7)],
            width=5,
        )

    def test_invalid_row_count(self):
        """Wrong number of rows should raise."""
        with pytest.raises(ValueError, match="7 rows"):
            Template(
                name="test",
                grid=[[0] * 5 for _ in range(3)],
                width=5,
            )

    def test_invalid_width(self):
        """Mismatched width should raise."""
        with pytest.raises(ValueError, match="width mismatch"):
            Template(
                name="test",
                grid=[[0] * 5 for _ in range(7)],
                width=10,
            )

    def test_default_legend(self):
        """Template should have default legend."""
        template = Template(
            name="test",
            grid=[[0] * 5 for _ in range(7)],
            width=5,
        )
        assert template.legend == DEFAULT_LEGEND


class TestParseTomlTemplate:
    """Tests for parse_toml_template."""

    def test_parse_minimal_toml(self):
        """Parse TOML with only required grid section."""
        content = '''
[grid]
data = """
##..##
##..##
######
##..##
##..##
##..##
......
"""
'''
        template = parse_toml_template(content)

        assert template.height == 7
        assert template.width == 6
        assert template.name == "unnamed"

    def test_parse_full_toml(self):
        """Parse TOML with all sections."""
        content = '''
[template]
name = "my-art"
description = "A test template"

[legend]
chars = " .:#"

[grid]
data = """
##..##
##..##
######
##..##
##..##
##..##
......
"""
'''
        template = parse_toml_template(content)

        assert template.name == "my-art"
        assert template.width == 6

    def test_custom_legend_chars(self):
        """Custom legend chars map position to level."""
        content = '''
[legend]
chars = "AB"

[grid]
data = """
AB
AB
AB
AB
AB
AB
AB
"""
'''
        template = parse_toml_template(content)

        # A=level 0, B=level 1
        for row in template.grid:
            assert row == [0, 1]

    def test_default_legend_when_missing(self):
        """Missing legend section uses default (.:-=#)."""
        content = '''
[grid]
data = """
.:-=#
.:-=#
.:-=#
.:-=#
.:-=#
.:-=#
.:-=#
"""
'''
        template = parse_toml_template(content)

        # Default legend: . = 0, : = 1, - = 2, = = 3, # = 4
        for row in template.grid:
            assert row == [0, 1, 2, 3, 4]

    def test_missing_grid_raises(self):
        """Missing grid section should raise TemplateError."""
        content = '''
[template]
name = "test"
'''
        with pytest.raises(TemplateError, match="Missing.*grid"):
            parse_toml_template(content)

    def test_invalid_toml_raises(self):
        """Invalid TOML syntax should raise TemplateError."""
        content = "this is not valid toml [[["

        with pytest.raises(TemplateError, match="Invalid TOML"):
            parse_toml_template(content)

    def test_wrong_row_count_raises(self):
        """Grid with != 7 rows should raise."""
        content = '''
[grid]
data = """
##
##
##
"""
'''
        with pytest.raises(TemplateError, match="7 rows"):
            parse_toml_template(content)

    def test_name_from_parameter(self):
        """Name parameter is used when not in TOML."""
        content = '''
[grid]
data = """
#
#
#
#
#
#
#
"""
'''
        template = parse_toml_template(content, name="custom-name")
        assert template.name == "custom-name"

    def test_toml_name_overrides_parameter(self):
        """Name in TOML takes precedence over parameter."""
        content = '''
[template]
name = "from-toml"

[grid]
data = """
#
#
#
#
#
#
#
"""
'''
        template = parse_toml_template(content, name="from-param")
        assert template.name == "from-toml"


class TestLoadTomlTemplate:
    """Tests for loading TOML templates via load_template."""

    def test_load_toml_file(self, tmp_path: Path):
        """load_template detects .toml extension."""
        template_file = tmp_path / "test.toml"
        template_file.write_text('''
[grid]
data = """
##..##
##..##
######
##..##
##..##
##..##
......
"""
''')

        template = load_template(template_file)

        assert template.name == "test"
        assert template.width == 6

    def test_load_toml_with_custom_legend(self, tmp_path: Path):
        """TOML with custom legend loads correctly."""
        template_file = tmp_path / "custom.toml"
        template_file.write_text('''
[legend]
chars = ".X"

[grid]
data = """
XX..XX
XX..XX
XXXXXX
XX..XX
XX..XX
XX..XX
......
"""
''')

        template = load_template(template_file)

        # X=level 1, .=level 0
        assert template.grid[0] == [1, 1, 0, 0, 1, 1]
        assert template.grid[6] == [0, 0, 0, 0, 0, 0]

    def test_txt_still_works(self, tmp_path: Path):
        """TXT files still load correctly."""
        template_file = tmp_path / "test.txt"
        template_file.write_text("""\
##..##
##..##
######
##..##
##..##
##..##
......""")

        template = load_template(template_file)

        assert template.name == "test"
        assert template.width == 6
