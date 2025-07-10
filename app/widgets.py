"""
Custom widget classes that extend govuk_frontend_wtf widgets to support parameter overrides.

This module provides enhanced GOV.UK widgets with type hints and parameter override capabilities.
All widgets support initialization-time parameter customization for better developer experience.
"""

from typing import Any, TypedDict
from govuk_frontend_wtf.wtforms_widgets import (
    GovTextInput as BaseGovTextInput,
    GovPasswordInput as BaseGovPasswordInput,
    GovCheckboxInput as BaseGovCheckboxInput,
    GovCheckboxesInput as BaseGovCheckboxesInput,
    GovRadioInput as BaseGovRadioInput,
    GovDateInput as BaseGovDateInput,
    GovFileInput as BaseGovFileInput,
    GovSubmitInput as BaseGovSubmitInput,
    GovTextArea as BaseGovTextArea,
    GovCharacterCount as BaseGovCharacterCount,
    GovSelect as BaseGovSelect,
)


class LabelParams(TypedDict, total=False):
    text: str
    isPageHeading: bool
    classes: str


class FieldsetParams(TypedDict, total=False):
    legend: dict[str, Any]


class HintParams(TypedDict, total=False):
    text: str


class GovUKParams(TypedDict, total=False):
    """GOV.UK widget parameters with proper type hints."""
    label: LabelParams
    fieldset: FieldsetParams
    hint: HintParams
    classes: str
    attributes: dict[str, Any]


class ParameterOverrideMixin:
    """
    Mixin class that provides direct parameter access for GOV.UK widgets.
    
    Allows widgets to accept common parameters directly without nested dicts.
    """
    
    def __init__(
        self,
        *,
        classes: str | None = None,
        hint: str | None = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize with common GOV.UK parameters.
        
        Args:
            classes: CSS classes to add
            hint: Hint text to display
            **kwargs: Additional parameters passed to parent widget
        """
        self.extra_classes = classes
        self.hint_text = hint
        super().__init__(**kwargs)
    
    def map_gov_params(self, field: Any, **kwargs: Any) -> dict[str, Any]:
        """Add extra classes and hint text to default parameters."""
        params = super().map_gov_params(field, **kwargs)
        
        if self.extra_classes:
            if 'classes' in params:
                params['classes'] = f"{params['classes']} {self.extra_classes}"
            else:
                params['classes'] = self.extra_classes
        
        if self.hint_text:
            params['hint'] = {'text': self.hint_text}
        
        return params


class GovTextInput(ParameterOverrideMixin, BaseGovTextInput):
    """
    Text input widget with parameter override support.
    
    Example usage:
        StringField("Name", widget=GovTextInput(
            classes="govuk-input--width-20",
            hint="Enter your full name"
        ))
    """
    pass


class GovPasswordInput(ParameterOverrideMixin, BaseGovPasswordInput):
    """
    Password input widget with parameter override support.
    
    Example usage:
        PasswordField("Password", widget=GovPasswordInput(
            classes="govuk-input--width-20"
        ))
    """
    pass


class GovCheckboxInput(ParameterOverrideMixin, BaseGovCheckboxInput):
    """
    Single checkbox widget with parameter override support.
    
    Example usage:
        BooleanField("Agree", widget=GovCheckboxInput(
            classes="govuk-checkboxes__input--large"
        ))
    """
    pass


class GovCheckboxesInput(ParameterOverrideMixin, BaseGovCheckboxesInput):
    """
    Multiple checkboxes widget with parameter override support.
    
    Example usage:
        SelectMultipleField("Options", widget=GovCheckboxesInput(
            hint="Choose all that apply"
        ))
    """
    pass


class GovRadioInput(ParameterOverrideMixin, BaseGovRadioInput):
    """
    Radio buttons widget with parameter override support.
    
    Example usage:
        RadioField("Choice", widget=GovRadioInput(
            hint="Select one option"
        ))
    """
    pass


class GovDateInput(ParameterOverrideMixin, BaseGovDateInput):
    """
    Date input widget with parameter override support.
    
    Example usage:
        DateField("Birth Date", widget=GovDateInput(
            hint="For example, 31 3 1980"
        ))
    """
    pass


class GovFileInput(ParameterOverrideMixin, BaseGovFileInput):
    """
    File upload widget with parameter override support.
    
    Example usage:
        FileField("Upload", widget=GovFileInput(
            multiple=True,
            classes="govuk-file-upload--drag-drop"
        ))
    """
    pass


class GovSubmitInput(ParameterOverrideMixin, BaseGovSubmitInput):
    """
    Submit button widget with parameter override support.
    
    Example usage:
        SubmitField("Submit", widget=GovSubmitInput(
            classes="govuk-button--secondary"
        ))
    """
    pass


class GovTextArea(ParameterOverrideMixin, BaseGovTextArea):
    """
    Textarea widget with parameter override support.
    
    Example usage:
        TextAreaField("Description", widget=GovTextArea(
            classes="govuk-textarea--large",
            hint="Provide as much detail as possible"
        ))
    """
    pass


class GovCharacterCount(ParameterOverrideMixin, BaseGovCharacterCount):
    """
    Character count textarea widget with parameter override support.
    
    Example usage:
        TextAreaField("Description", widget=GovCharacterCount(
            classes="govuk-textarea--large"
        ))
    """
    pass


class GovSelect(ParameterOverrideMixin, BaseGovSelect):
    """
    Select dropdown widget with parameter override support.
    
    Example usage:
        SelectField("Country", widget=GovSelect(
            classes="govuk-select--large"
        ))
    """
    pass


class PageHeadingMixin:
    """Mixin to make any widget render its label as a page heading."""
    
    def __init__(self, heading_size: str = "l", **kwargs: Any) -> None:
        """
        Initialize with page heading configuration.
        
        Args:
            heading_size: Size of the heading ('s', 'm', 'l', 'xl')
            **kwargs: Additional parameters passed to parent
        """
        self.heading_size = heading_size
        super().__init__(**kwargs)
    
    def map_gov_params(self, field: Any, **kwargs: Any) -> dict[str, Any]:
        """Configure label as page heading."""
        params = super().map_gov_params(field, **kwargs)
        
        if 'label' not in params:
            params['label'] = {}
        
        params['label'].update({
            "isPageHeading": True,
            "classes": f"govuk-label--{self.heading_size}"
        })
        
        return params


class PageHeadingInput(PageHeadingMixin, GovTextInput):
    """Text input configured as a page heading."""
    pass


class PageHeadingTextArea(PageHeadingMixin, GovTextArea):
    """Textarea configured as a page heading.""" 
    pass


class PageHeadingSelect(PageHeadingMixin, GovSelect):
    """Select dropdown configured as a page heading."""
    pass


class WidthConstrainedInput(GovTextInput):
    """Text input with constrained width."""
    
    def __init__(self, width: str, **kwargs: Any) -> None:
        """
        Initialize width-constrained input.
        
        Args:
            width: Width constraint ('2', '3', '4', '5', '10', '20', 'one-quarter', 'one-third', 'one-half', 'two-thirds', 'three-quarters', 'full')
            **kwargs: Additional parameters passed to parent
        """
        width_class = f"govuk-input--width-{width}"
        existing_classes = kwargs.get('classes', '')
        
        if existing_classes:
            kwargs['classes'] = f"{existing_classes} {width_class}"
        else:
            kwargs['classes'] = width_class
            
        super().__init__(**kwargs)


class CharacterCountTextArea(GovCharacterCount):
    """Character count textarea with predefined limits."""
    
    def __init__(self, max_length: int, threshold: int = 75, **kwargs: Any) -> None:
        """
        Initialize character count textarea.
        
        Args:
            max_length: Maximum number of characters
            threshold: Percentage threshold for warning (default: 75)
            **kwargs: Additional parameters passed to parent
        """
        self.max_length = max_length
        self.threshold = threshold
        super().__init__(**kwargs)
    
    def map_gov_params(self, field: Any, **kwargs: Any) -> dict[str, Any]:
        """Add character count configuration."""
        params = super().map_gov_params(field, **kwargs)
        params.update({
            "maxlength": str(self.max_length),
            "threshold": str(self.threshold)
        })
        return params


__all__ = [
    'LabelParams',
    'FieldsetParams', 
    'HintParams',
    'GovUKParams',
    
    'GovTextInput',
    'GovPasswordInput',
    'GovCheckboxInput',
    'GovCheckboxesInput',
    'GovRadioInput',
    'GovDateInput',
    'GovFileInput',
    'GovSubmitInput',
    'GovTextArea',
    'GovCharacterCount',
    'GovSelect',
    
    'PageHeadingMixin',
    'PageHeadingInput',
    'PageHeadingTextArea', 
    'PageHeadingSelect',
    'WidthConstrainedInput',
    'CharacterCountTextArea',
]
