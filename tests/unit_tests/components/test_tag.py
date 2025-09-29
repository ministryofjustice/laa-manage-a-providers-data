import pytest

from app.components.tag import Tag, TagType


class TestTag:
    def test_init_valid_tag_type(self):
        tag = Tag(TagType.INACTIVE)

        assert tag.tag_type == TagType.INACTIVE

    def test_init_invalid_tag_type_raises_error(self):
        with pytest.raises(ValueError, match="tag_type must be a TagType enum value"):
            Tag("invalid-type")

    def test_init_none_tag_type_raises_error(self):
        with pytest.raises(ValueError, match="tag_type must be a TagType enum value"):
            Tag(None)

    def test_init_non_tag_type_raises_error(self):
        with pytest.raises(ValueError, match="tag_type must be a TagType enum value"):
            Tag(123)

    def test_to_gov_params_inactive(self):
        tag = Tag(TagType.INACTIVE)
        params = tag.to_gov_params()

        assert params == {"text": "Inactive", "class": "govuk-tag--grey"}

    def test_to_gov_params_on_hold(self):
        tag = Tag(TagType.ON_HOLD)
        params = tag.to_gov_params()

        assert params == {"text": "On hold", "class": "govuk-tag--yellow"}

    def test_to_gov_params_firm_intervened(self):
        tag = Tag(TagType.FIRM_INTERVENED)
        params = tag.to_gov_params()

        assert params == {"text": "Firm intervened", "class": "govuk-tag--pink"}

    def test_to_gov_params_all_tag_types(self):
        test_cases = [
            (TagType.INACTIVE, "Inactive", "govuk-tag--grey"),
            (TagType.ON_HOLD, "On hold", "govuk-tag--yellow"),
            (TagType.FIRM_INTERVENED, "Firm intervened", "govuk-tag--pink"),
        ]

        for tag_type, expected_text, expected_class in test_cases:
            tag = Tag(tag_type)
            params = tag.to_gov_params()

            assert params["text"] == expected_text
            assert params["class"] == expected_class

    def test_multiple_tags(self):
        tags = [Tag(TagType.INACTIVE), Tag(TagType.ON_HOLD), Tag(TagType.FIRM_INTERVENED)]

        # Test that each tag maintains its correct properties
        assert len(tags) == 3

        params_list = [tag.to_gov_params() for tag in tags]

        expected_params = [
            {"text": "Inactive", "class": "govuk-tag--grey"},
            {"text": "On hold", "class": "govuk-tag--yellow"},
            {"text": "Firm intervened", "class": "govuk-tag--pink"},
        ]

        assert params_list == expected_params

        # Test individual tag properties
        assert tags[0].tag_type == TagType.INACTIVE
        assert tags[1].tag_type == TagType.ON_HOLD
        assert tags[2].tag_type == TagType.FIRM_INTERVENED
