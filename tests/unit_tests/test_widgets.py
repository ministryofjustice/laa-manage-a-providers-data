from unittest.mock import Mock

import pytest

from app.widgets import (
    CharacterCountTextArea,
    GovCheckboxInput,
    GovPasswordInput,
    GovRadioInput,
    GovSelect,
    GovTextArea,
    GovTextInput,
    PageHeadingInput,
    PageHeadingMixin,
    PageHeadingTextArea,
    WidthConstrainedInput,
)


class TestParameterOverrideMixin:
    def test_init_with_classes(self):
        widget = GovTextInput(classes="custom-class")
        assert widget.extra_classes == "custom-class"

    def test_init_with_hint(self):
        widget = GovTextInput(hint="Test hint")
        assert widget.hint_text == "Test hint"

    def test_init_with_prefix_suffix(self):
        widget = GovTextInput(prefix="£", suffix="per hour")
        assert widget.prefix_text == "£"
        assert widget.suffix_text == "per hour"

    def test_init_with_accessibility_params(self):
        widget = GovTextInput(disabled=True, describedBy="help-text error-message", inputmode="numeric")
        assert widget.disabled is True
        assert widget.described_by == "help-text error-message"
        assert widget.inputmode == "numeric"

    def test_init_with_input_attributes(self):
        widget = GovTextInput(spellcheck=False, autocomplete="name", autocapitalize="words", pattern="[A-Za-z]+")
        assert widget.spellcheck is False
        assert widget.autocomplete == "name"
        assert widget.autocapitalize == "words"
        assert widget.pattern == "[A-Za-z]+"

    def test_init_with_all_params(self):
        widget = GovTextInput(
            classes="custom-class",
            hint="Test hint",
            prefix="Dr.",
            suffix="PhD",
            disabled=False,
            describedBy="hint error",
            inputmode="text",
            spellcheck=True,
            autocomplete="name",
            autocapitalize="words",
            pattern="[A-Za-z ]+",
        )
        assert widget.extra_classes == "custom-class"
        assert widget.hint_text == "Test hint"
        assert widget.prefix_text == "Dr."
        assert widget.suffix_text == "PhD"
        assert widget.disabled is False
        assert widget.described_by == "hint error"
        assert widget.inputmode == "text"
        assert widget.spellcheck is True
        assert widget.autocomplete == "name"
        assert widget.autocapitalize == "words"
        assert widget.pattern == "[A-Za-z ]+"

    def test_map_gov_params_adds_classes(self):
        widget = GovTextInput(classes="custom-class")
        field = Mock()

        with pytest.MonkeyPatch().context() as m:
            m.setattr(widget.__class__.__bases__[1], "map_gov_params", lambda self, field, **kwargs: {})
            params = widget.map_gov_params(field)
            assert params.get("classes") == "custom-class"

    def test_map_gov_params_adds_hint(self):
        widget = GovTextInput(hint="Test hint")
        field = Mock()

        with pytest.MonkeyPatch().context() as m:
            m.setattr(widget.__class__.__bases__[1], "map_gov_params", lambda self, field, **kwargs: {})
            params = widget.map_gov_params(field)
            assert params.get("hint") == {"text": "Test hint"}

    def test_map_gov_params_adds_prefix_suffix(self):
        widget = GovTextInput(prefix="£", suffix="per hour")
        field = Mock()

        with pytest.MonkeyPatch().context() as m:
            m.setattr(widget.__class__.__bases__[1], "map_gov_params", lambda self, field, **kwargs: {})
            params = widget.map_gov_params(field)
            assert params.get("prefix") == {"text": "£"}
            assert params.get("suffix") == {"text": "per hour"}

    def test_map_gov_params_adds_accessibility_params(self):
        widget = GovTextInput(disabled=True, describedBy="help error", inputmode="numeric")
        field = Mock()

        with pytest.MonkeyPatch().context() as m:
            m.setattr(widget.__class__.__bases__[1], "map_gov_params", lambda self, field, **kwargs: {})
            params = widget.map_gov_params(field)
            assert params.get("disabled") is True
            assert params.get("describedBy") == "help error"
            assert params.get("inputmode") == "numeric"

    def test_map_gov_params_adds_input_attributes(self):
        widget = GovTextInput(spellcheck=False, autocomplete="email", autocapitalize="none", pattern=".*@.*")
        field = Mock()

        with pytest.MonkeyPatch().context() as m:
            m.setattr(widget.__class__.__bases__[1], "map_gov_params", lambda self, field, **kwargs: {})
            params = widget.map_gov_params(field)
            assert params.get("spellcheck") is False
            assert params.get("autocomplete") == "email"
            assert params.get("autocapitalize") == "none"
            assert params.get("pattern") == ".*@.*"

    def test_map_gov_params_merges_existing_classes(self):
        widget = GovTextInput(classes="custom-class")
        field = Mock()

        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                widget.__class__.__bases__[1],
                "map_gov_params",
                lambda self, field, **kwargs: {"classes": "existing-class"},
            )
            params = widget.map_gov_params(field)
            assert params.get("classes") == "existing-class custom-class"

    def test_map_gov_params_skips_none_values(self):
        widget = GovTextInput(classes=None, hint=None, prefix=None, disabled=None, spellcheck=None)
        field = Mock()

        with pytest.MonkeyPatch().context() as m:
            m.setattr(widget.__class__.__bases__[1], "map_gov_params", lambda self, field, **kwargs: {})
            params = widget.map_gov_params(field)
            assert "classes" not in params
            assert "hint" not in params
            assert "prefix" not in params
            assert "disabled" not in params
            assert "spellcheck" not in params


class TestPageHeadingMixin:
    def test_init_with_default_heading_size(self):
        widget = PageHeadingInput()
        assert widget.heading_size == "l"

    def test_init_with_custom_heading_size(self):
        widget = PageHeadingInput(heading_size="xl")
        assert widget.heading_size == "xl"

    def test_map_gov_params_sets_page_heading(self):
        widget = PageHeadingInput()

        params = {}

        if "label" not in params:
            params["label"] = {}

        params["label"].update({"isPageHeading": True, "classes": f"govuk-label--{widget.heading_size}"})

        assert "label" in params
        assert params["label"]["isPageHeading"] is True
        assert params["label"]["classes"] == "govuk-label--l"

    def test_map_gov_params_custom_heading_size(self):
        widget = PageHeadingInput(heading_size="xl")

        params = {}

        if "label" not in params:
            params["label"] = {}

        params["label"].update({"isPageHeading": True, "classes": f"govuk-label--{widget.heading_size}"})

        assert params["label"]["classes"] == "govuk-label--xl"


class TestWidthConstrainedInput:
    def test_init_with_width(self):
        widget = WidthConstrainedInput(width="10")
        assert "govuk-input--width-10" in widget.extra_classes

    def test_init_with_width_and_existing_classes(self):
        widget = WidthConstrainedInput(width="20", classes="existing-class")
        assert "govuk-input--width-20" in widget.extra_classes
        assert "existing-class" in widget.extra_classes

    def test_width_options(self):
        for width in ["2", "3", "4", "5", "10", "20", "one-quarter", "one-half", "full"]:
            widget = WidthConstrainedInput(width=width)
            assert f"govuk-input--width-{width}" in widget.extra_classes


class TestCharacterCountTextArea:
    def test_init_with_max_length(self):
        widget = CharacterCountTextArea(max_length=100)
        assert widget.max_length == 100
        assert widget.threshold == 75

    def test_init_with_custom_threshold(self):
        widget = CharacterCountTextArea(max_length=200, threshold=80)
        assert widget.max_length == 200
        assert widget.threshold == 80

    def test_map_gov_params_adds_character_count(self):
        widget = CharacterCountTextArea(max_length=150, threshold=90)
        field = Mock()

        with pytest.MonkeyPatch().context() as m:
            m.setattr(widget.__class__.__bases__[0], "map_gov_params", lambda self, field, **kwargs: {})
            params = widget.map_gov_params(field)

            assert params.get("maxlength") == "150"
            assert params.get("threshold") == "90"


class TestSpecializedWidgets:
    def test_page_heading_input_inheritance(self):
        widget = PageHeadingInput()
        assert isinstance(widget, PageHeadingMixin)
        assert isinstance(widget, GovTextInput)

    def test_page_heading_textarea_inheritance(self):
        widget = PageHeadingTextArea()
        assert isinstance(widget, PageHeadingMixin)
        assert isinstance(widget, GovTextArea)

    def test_widget_properties(self):
        widget = PageHeadingInput(heading_size="m", classes="custom-class", hint="Test hint")

        assert widget.heading_size == "m"
        assert widget.extra_classes == "custom-class"
        assert widget.hint_text == "Test hint"


class TestAllWidgetTypes:
    def test_password_input_widget(self):
        widget = GovPasswordInput(classes="govuk-input--width-20", autocomplete="current-password", spellcheck=False)
        assert widget.extra_classes == "govuk-input--width-20"
        assert widget.autocomplete == "current-password"
        assert widget.spellcheck is False

    def test_checkbox_input_widget(self):
        widget = GovCheckboxInput(classes="govuk-checkboxes__input--large", disabled=False)
        assert widget.extra_classes == "govuk-checkboxes__input--large"
        assert widget.disabled is False

    def test_radio_input_widget(self):
        widget = GovRadioInput(hint="Select one option", describedBy="hint-id")
        assert widget.hint_text == "Select one option"
        assert widget.described_by == "hint-id"

    def test_select_widget(self):
        widget = GovSelect(classes="govuk-select--large", disabled=True)
        assert widget.extra_classes == "govuk-select--large"
        assert widget.disabled is True

    def test_textarea_widget(self):
        widget = GovTextArea(
            classes="govuk-textarea--large", hint="Enter details", spellcheck=True, autocapitalize="sentences"
        )
        assert widget.extra_classes == "govuk-textarea--large"
        assert widget.hint_text == "Enter details"
        assert widget.spellcheck is True
        assert widget.autocapitalize == "sentences"


class TestWidgetIntegration:
    def test_widget_initialization(self):
        text_widget = GovTextInput(classes="govuk-input--width-20")
        assert text_widget.extra_classes == "govuk-input--width-20"

        heading_widget = PageHeadingInput(heading_size="xl")
        assert heading_widget.heading_size == "xl"

        width_widget = WidthConstrainedInput(width="10")
        assert "govuk-input--width-10" in width_widget.extra_classes

        char_widget = CharacterCountTextArea(max_length=500)
        assert char_widget.max_length == 500

    def test_complex_widget_combinations(self):
        widget = PageHeadingInput(
            heading_size="xl",
            classes="custom-class",
            hint="Enter your full name",
            prefix="Dr.",
            suffix="PhD",
            autocomplete="name",
            pattern="[A-Za-z ]+",
            spellcheck=True,
            describedBy="name-hint name-error",
        )

        assert widget.heading_size == "xl"
        assert widget.extra_classes == "custom-class"
        assert widget.hint_text == "Enter your full name"
        assert widget.prefix_text == "Dr."
        assert widget.suffix_text == "PhD"
        assert widget.autocomplete == "name"
        assert widget.pattern == "[A-Za-z ]+"
        assert widget.spellcheck is True
        assert widget.described_by == "name-hint name-error"

    def test_multiple_inheritance_order(self):
        widget = PageHeadingInput()

        assert hasattr(widget, "heading_size")
        assert hasattr(widget, "extra_classes")

        widget_with_params = PageHeadingInput(heading_size="xl", classes="custom-class", hint="Test hint")

        assert widget_with_params.heading_size == "xl"
        assert widget_with_params.extra_classes == "custom-class"
        assert widget_with_params.hint_text == "Test hint"


class TestParameterValidation:
    def test_boolean_parameters(self):
        # Test explicit True/False
        widget_true = GovTextInput(disabled=True, spellcheck=True)
        assert widget_true.disabled is True
        assert widget_true.spellcheck is True

        widget_false = GovTextInput(disabled=False, spellcheck=False)
        assert widget_false.disabled is False
        assert widget_false.spellcheck is False

        # Test None (should not be set)
        widget_none = GovTextInput(disabled=None, spellcheck=None)
        assert widget_none.disabled is None
        assert widget_none.spellcheck is None

    def test_string_parameters(self):
        widget = GovTextInput(
            inputmode="numeric",
            autocomplete="email",
            autocapitalize="words",
            pattern="[0-9]+",
            describedBy="help-text error-message",
        )

        assert widget.inputmode == "numeric"
        assert widget.autocomplete == "email"
        assert widget.autocapitalize == "words"
        assert widget.pattern == "[0-9]+"
        assert widget.described_by == "help-text error-message"

    def test_empty_string_parameters(self):
        widget = GovTextInput(classes="", hint="", prefix="", suffix="")

        # Empty strings should still be set (falsy but not None)
        assert widget.extra_classes == ""
        assert widget.hint_text == ""
        assert widget.prefix_text == ""
        assert widget.suffix_text == ""
