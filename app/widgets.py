"""
Custom widget classes that extend govuk_frontend_wtf widgets to support parameter overrides.

This module provides enhanced GOV.UK widgets with type hints and parameter override capabilities.
All widgets support initialization-time parameter customization for better developer experience.
"""

from typing import Any, TypedDict

from govuk_frontend_wtf.wtforms_widgets import GovCharacterCount as BaseGovCharacterCount
from govuk_frontend_wtf.wtforms_widgets import GovCheckboxesInput as BaseGovCheckboxesInput
from govuk_frontend_wtf.wtforms_widgets import GovCheckboxInput as BaseGovCheckboxInput
from govuk_frontend_wtf.wtforms_widgets import GovDateInput as BaseGovDateInput
from govuk_frontend_wtf.wtforms_widgets import GovFileInput as BaseGovFileInput
from govuk_frontend_wtf.wtforms_widgets import GovPasswordInput as BaseGovPasswordInput
from govuk_frontend_wtf.wtforms_widgets import GovRadioInput as BaseGovRadioInput
from govuk_frontend_wtf.wtforms_widgets import GovSelect as BaseGovSelect
from govuk_frontend_wtf.wtforms_widgets import GovSubmitInput as BaseGovSubmitInput
from govuk_frontend_wtf.wtforms_widgets import GovTextArea as BaseGovTextArea
from govuk_frontend_wtf.wtforms_widgets import GovTextInput as BaseGovTextInput
from markupsafe import Markup

from app.components.tables import RadioDataTable, TableStructure


class LabelParams(TypedDict, total=False):
    text: str
    html: str
    for_: str  # Maps to 'for' attribute
    isPageHeading: bool
    classes: str
    attributes: dict[str, Any]


class HintParams(TypedDict, total=False):
    text: str
    html: str
    id: str
    classes: str
    attributes: dict[str, Any]


class ErrorMessageParams(TypedDict, total=False):
    text: str
    html: str
    id: str
    classes: str
    attributes: dict[str, Any]


class PrefixParams(TypedDict, total=False):
    text: str
    html: str
    classes: str
    attributes: dict[str, Any]


class SuffixParams(TypedDict, total=False):
    text: str
    html: str
    classes: str
    attributes: dict[str, Any]


class BeforeAfterInputParams(TypedDict, total=False):
    text: str
    html: str


class FormGroupParams(TypedDict, total=False):
    classes: str
    attributes: dict[str, Any]
    beforeInput: BeforeAfterInputParams
    afterInput: BeforeAfterInputParams


class InputWrapperParams(TypedDict, total=False):
    classes: str
    attributes: dict[str, Any]


class FieldsetParams(TypedDict, total=False):
    legend: dict[str, Any]
    classes: str
    attributes: dict[str, Any]


class GovUKParams(TypedDict, total=False):
    """GOV.UK widget parameters with proper type hints."""

    id: str
    name: str
    type: str
    inputmode: str
    value: str
    disabled: bool
    describedBy: str
    label: LabelParams
    hint: HintParams
    errorMessage: ErrorMessageParams
    prefix: PrefixParams
    suffix: SuffixParams
    formGroup: FormGroupParams
    classes: str
    autocomplete: str
    pattern: str
    spellcheck: bool
    autocapitalize: str
    inputWrapper: InputWrapperParams
    attributes: dict[str, Any]
    fieldset: FieldsetParams  # For radios/checkboxes


class ParameterOverrideMixin:
    """
    Mixin class that provides direct parameter access for GOV.UK widgets.

    Allows widgets to accept common parameters directly without nested dicts.
    """

    def __init__(
        self,
        *,
        classes: str | None = None,
        heading_class: str | None = None,
        form_group_classes: str | None = None,
        hint: str | None = None,
        prefix: str | None = None,
        suffix: str | None = None,
        disabled: bool | None = None,
        describedBy: str | None = None,
        inputmode: str | None = None,
        spellcheck: bool | None = None,
        autocomplete: str | None = None,
        autocapitalize: str | None = None,
        pattern: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize with common GOV.UK parameters.

        Args:
            classes: CSS classes to add
            heading_class: Overrides the title of an input
            hint: Hint text to display
            prefix: Prefix text or HTML
            suffix: Suffix text or HTML
            disabled: Whether the input is disabled
            describedBy: Space-separated list of element IDs for aria-describedby
            inputmode: Input mode for mobile keyboards
            spellcheck: Enable/disable spellcheck
            autocomplete: Autocomplete attribute value
            autocapitalize: Text capitalization behavior
            pattern: Regular expression pattern for validation
            **kwargs: Additional parameters passed to parent widget
        """
        self.extra_classes = classes
        self.hint_text = hint
        self.prefix_text = prefix
        self.suffix_text = suffix
        self.disabled = disabled
        self.described_by = describedBy
        self.inputmode = inputmode
        self.spellcheck = spellcheck
        self.autocomplete = autocomplete
        self.autocapitalize = autocapitalize
        self.pattern = pattern
        self.heading_class = heading_class
        self.form_group_classes = form_group_classes
        super().__init__(**kwargs)

    def map_gov_params(self, field: Any, **kwargs: Any) -> dict[str, Any]:
        """Add all configured parameters to the widget params."""
        params = super().map_gov_params(field, **kwargs)

        if self.extra_classes:
            if "classes" in params:
                params["classes"] = f"{params['classes']} {self.extra_classes}"
            else:
                params["classes"] = self.extra_classes

        if self.hint_text:
            params["hint"] = {"text": self.hint_text}

        if self.prefix_text:
            params["prefix"] = {"text": self.prefix_text}

        if self.suffix_text:
            params["suffix"] = {"text": self.suffix_text}

        if self.disabled is not None:
            params["disabled"] = self.disabled

        if self.described_by:
            params["describedBy"] = self.described_by

        if self.inputmode:
            params["inputmode"] = self.inputmode

        if self.spellcheck is not None:
            params["spellcheck"] = self.spellcheck

        if self.autocomplete:
            params["autocomplete"] = self.autocomplete

        if self.pattern:
            params["pattern"] = self.pattern

        if self.autocapitalize:
            params["autocapitalize"] = self.autocapitalize

        if self.heading_class:
            if "fieldset" in params:
                params["fieldset"]["legend"]["classes"] = self.heading_class
            else:
                params["label"]["classes"] = self.heading_class

        if self.form_group_classes:
            if "formGroup" in params:
                params["formGroup"]["classes"] = self.form_group_classes
            else:
                params["formGroup"] = {"classes": self.form_group_classes}

        return params


class GovTextInput(ParameterOverrideMixin, BaseGovTextInput):
    """
    Text input widget with parameter override support.

    Example usage:
        StringField("Name", widget=GovTextInput(
            classes="govuk-input--width-20",
            hint="Enter your full name",
            prefix="Dr.",
            autocomplete="name",
            pattern="[A-Za-z ]+",
            describedBy="name-hint"
        ))
    """

    pass


class GovPasswordInput(ParameterOverrideMixin, BaseGovPasswordInput):
    """
    Password input widget with parameter override support.

    Example usage:
        PasswordField("Password", widget=GovPasswordInput(
            classes="govuk-input--width-20",
            autocomplete="current-password",
            spellcheck=False
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
            classes="govuk-file-upload",
            hint="Select a file to upload",
            disabled=False
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
            hint="Provide as much detail as possible",
            spellcheck=True,
            describedBy="description-hint"
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

        if "label" not in params:
            params["label"] = {}

        params["label"].update({"isPageHeading": True, "classes": f"govuk-label--{self.heading_size}"})

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
        existing_classes = kwargs.get("classes", "")

        if existing_classes:
            kwargs["classes"] = f"{existing_classes} {width_class}"
        else:
            kwargs["classes"] = width_class

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
        params.update({"maxlength": str(self.max_length), "threshold": str(self.threshold)})
        return params


class GovUKTableRadioWidget:
    """Widget that renders GovUK table with radio buttons for use in base form templates."""

    def __init__(self, structure: list[TableStructure], radio_value_key: str = "id"):
        """
        Initialize the widget.

        Args:
            structure: Table structure definition
            radio_value_key: Key in row data to use as radio button value
        """
        self.structure = structure
        self.radio_value_key = radio_value_key

    def __call__(self, field, **kwargs):
        """
        Render the complete GovUK table with radio buttons.
        This allows {{ field }} to work in your base template.
        """
        # Convert field choices to DataTable format
        data = []
        for choice_value, choice_data in field.choices:
            if isinstance(choice_data, dict):
                row_data = choice_data.copy()
                row_data[self.radio_value_key] = choice_value
            elif isinstance(choice_data, (list, tuple)):
                row_data = {self.radio_value_key: choice_value}
                for i, value in enumerate(choice_data):
                    if i < len(self.structure):
                        structure_id = self.structure[i].get("id", f"col_{i}")
                        row_data[structure_id] = str(value)
            else:
                row_data = {self.radio_value_key: choice_value, "label": str(choice_data)}
            data.append(row_data)

        # Create RadioDataTable
        table = RadioDataTable(
            structure=self.structure, data=data, radio_field_name=field.name, radio_value_key=self.radio_value_key
        )

        # Get table params
        table_params = table.to_govuk_params(selected_value=field.data, **kwargs)

        # Render using the same structure as govukTable macro
        return self._render_govuk_table(table_params, field)

    def _render_govuk_table(self, params: dict, field) -> Markup:
        """Render GovUK table HTML matching the official macro output."""
        html_parts = []

        # Add form group wrapper with error handling
        css_classes = ["govuk-form-group"]
        if field.errors:
            css_classes.append("govuk-form-group--error")

        html_parts.append(f'<div class="{" ".join(css_classes)}">')

        # Add field label as heading if it exists
        if hasattr(field, "label") and field.label.text:
            html_parts.append('<fieldset class="govuk-fieldset">')
            html_parts.append('<legend class="govuk-fieldset__legend govuk-fieldset__legend--l">')
            html_parts.append(f'<h1 class="govuk-fieldset__heading">{field.label.text}</h1>')
            html_parts.append("</legend>")

        # Add error message if present
        if field.errors:
            html_parts.append(f'<p id="{field.id}-error" class="govuk-error-message">')
            html_parts.append('<span class="govuk-visually-hidden">Error:</span>')
            html_parts.append(f"{field.errors[0]}")
            html_parts.append("</p>")

        # Build table
        table_classes = params.get("classes", "")
        table_attrs = {"class": table_classes}

        if "attributes" in params:
            table_attrs.update(params["attributes"])

        # Add error state
        if field.errors:
            table_attrs["aria-describedby"] = f"{field.id}-error"

        attrs_str = " ".join(f'{k}="{v}"' for k, v in table_attrs.items())
        html_parts.append(f"<table {attrs_str}>")

        # Table head
        if params.get("head"):
            html_parts.append('<thead class="govuk-table__head">')
            html_parts.append('<tr class="govuk-table__row">')
            for heading in params["head"]:
                classes = heading.get("classes", "")
                if "govuk-table__header" not in classes:
                    classes = f"govuk-table__header {classes}".strip()
                scope = 'scope="col"' if heading.get("text") else ""
                html_parts.append(f'<th class="{classes}" {scope}>{heading.get("text", "")}</th>')
            html_parts.append("</tr>")
            html_parts.append("</thead>")

        # Table body
        html_parts.append('<tbody class="govuk-table__body">')
        for row in params.get("rows", []):
            html_parts.append('<tr class="govuk-table__row">')
            for cell in row:
                classes = cell.get("classes", "")
                if "govuk-table__cell" not in classes:
                    classes = f"govuk-table__cell {classes}".strip()

                cell_attrs = f'class="{classes}"'
                if cell.get("attributes"):
                    for attr_name, attr_value in cell["attributes"].items():
                        cell_attrs += f' {attr_name}="{attr_value}"'

                content = cell.get("html", "") or cell.get("text", "")
                html_parts.append(f"<td {cell_attrs}>{content}</td>")
            html_parts.append("</tr>")

        html_parts.append("</tbody>")
        html_parts.append("</table>")

        # Close fieldset if we opened one
        if hasattr(field, "label") and field.label.text:
            html_parts.append("</fieldset>")

        html_parts.append("</div>")

        return Markup("".join(html_parts))


__all__ = [
    "LabelParams",
    "HintParams",
    "ErrorMessageParams",
    "PrefixParams",
    "SuffixParams",
    "BeforeAfterInputParams",
    "FormGroupParams",
    "InputWrapperParams",
    "FieldsetParams",
    "GovUKParams",
    "ParameterOverrideMixin",
    "GovTextInput",
    "GovPasswordInput",
    "GovCheckboxInput",
    "GovCheckboxesInput",
    "GovRadioInput",
    "GovDateInput",
    "GovFileInput",
    "GovSubmitInput",
    "GovTextArea",
    "GovCharacterCount",
    "GovSelect",
    "PageHeadingMixin",
    "PageHeadingInput",
    "PageHeadingTextArea",
    "PageHeadingSelect",
    "WidthConstrainedInput",
    "CharacterCountTextArea",
]
