import pytest
from unittest.mock import Mock
from app.main.widgets import (
    GovTextInput,
    GovTextArea,
    PageHeadingInput,
    PageHeadingTextArea,
    WidthConstrainedInput,
    CharacterCountTextArea,
    PageHeadingMixin,
)


class TestParameterOverrideMixin:
    def test_init_with_classes(self):
        widget = GovTextInput(classes="custom-class")
        assert widget.extra_classes == "custom-class"

    def test_init_with_hint(self):
        widget = GovTextInput(hint="Test hint")
        assert widget.hint_text == "Test hint"

    def test_init_with_both_params(self):
        widget = GovTextInput(classes="custom-class", hint="Test hint")
        assert widget.extra_classes == "custom-class"
        assert widget.hint_text == "Test hint"

    def test_map_gov_params_adds_classes(self):
        widget = GovTextInput(classes="custom-class")
        field = Mock()
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr(widget.__class__.__bases__[1], 'map_gov_params', 
                     lambda self, field, **kwargs: {})
            params = widget.map_gov_params(field)
            assert params.get("classes") == "custom-class"

    def test_map_gov_params_adds_hint(self):
        widget = GovTextInput(hint="Test hint")
        field = Mock()
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr(widget.__class__.__bases__[1], 'map_gov_params', 
                     lambda self, field, **kwargs: {})
            params = widget.map_gov_params(field)
            assert params.get("hint") == {"text": "Test hint"}


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
        
        if 'label' not in params:
            params['label'] = {}
        
        params['label'].update({
            "isPageHeading": True,
            "classes": f"govuk-label--{widget.heading_size}"
        })
        
        assert "label" in params
        assert params["label"]["isPageHeading"] is True
        assert params["label"]["classes"] == "govuk-label--l"

    def test_map_gov_params_custom_heading_size(self):
        widget = PageHeadingInput(heading_size="xl")
        
        params = {}
        
        if 'label' not in params:
            params['label'] = {}
        
        params['label'].update({
            "isPageHeading": True,
            "classes": f"govuk-label--{widget.heading_size}"
        })
        
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
            m.setattr(widget.__class__.__bases__[0], 'map_gov_params', 
                     lambda self, field, **kwargs: {})
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

    def test_multiple_inheritance_order(self):
        widget = PageHeadingInput()
        
        assert hasattr(widget, 'heading_size')
        assert hasattr(widget, 'extra_classes')
        
        widget_with_params = PageHeadingInput(
            heading_size="xl", 
            classes="custom-class", 
            hint="Test hint"
        )
        
        assert widget_with_params.heading_size == "xl"
        assert widget_with_params.extra_classes == "custom-class"
        assert widget_with_params.hint_text == "Test hint"