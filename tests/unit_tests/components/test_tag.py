import pytest

from app.components.tag import Tag, TagColor


class TestTag:
    def test_init_valid_text_and_color(self):
        tag = Tag("Active", TagColor.GREEN)

        assert tag.text == "Active"
        assert tag.color == TagColor.GREEN

    def test_init_empty_text_raises_error(self):
        with pytest.raises(ValueError, match="Text must be a non-empty string"):
            Tag("", TagColor.RED)

    def test_init_whitespace_text_raises_error(self):
        with pytest.raises(ValueError, match="Text must be a non-empty string"):
            Tag("   ", TagColor.BLUE)

    def test_init_none_text_raises_error(self):
        with pytest.raises(ValueError, match="Text must be a non-empty string"):
            Tag(None, TagColor.YELLOW)

    def test_init_non_string_text_raises_error(self):
        with pytest.raises(ValueError, match="Text must be a non-empty string"):
            Tag(123, TagColor.PURPLE)

    def test_init_invalid_color_raises_error(self):
        with pytest.raises(ValueError, match="Color must be a TagColor enum value"):
            Tag("Valid text", "invalid-color")

    def test_to_gov_params(self):
        tag = Tag("Complete", TagColor.GREEN)
        params = tag.to_govuk_params()

        assert params == {"text": "Complete", "classes": "govuk-tag--green"}

    def test_to_gov_params_all_colors(self):
        test_cases = [
            (TagColor.GREY, "govuk-tag--grey"),
            (TagColor.GREEN, "govuk-tag--green"),
            (TagColor.RED, "govuk-tag--red"),
            (TagColor.BLUE, "govuk-tag--blue"),
            (TagColor.YELLOW, "govuk-tag--yellow"),
        ]

        for color, expected_class in test_cases:
            tag = Tag("Test", color)
            params = tag.to_govuk_params()

            assert params["classes"] == expected_class
