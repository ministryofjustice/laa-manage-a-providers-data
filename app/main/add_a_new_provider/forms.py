from flask import current_app
from wtforms import RadioField
from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired, Length

from app.validators import ValidateSearchResults
from app.widgets import GovRadioInput, GovTextInput

from ...components.tables import RadioDataTable
from ...forms import BaseForm


class AddProviderForm(BaseForm):
    title = "Add a new provider"
    url = "add-provider"

    provider_name = StringField(
        "Provider name",
        widget=GovTextInput(heading_class="govuk-fieldset__legend--m"),
        validators=[
            InputRequired(message="Enter the provider name"),
        ],
    )

    provider_type = RadioField(
        "Provider type",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m"),
        validators=[InputRequired(message=("Select a provider type"))],
        choices=[
            ("barrister", "Barrister"),
            ("advocate", "Advocate"),
            ("chambers", "Chambers"),
            ("lsp", "Legal services provider"),
        ],
    )


class LspDetailsForm(BaseForm):
    title = "Legal services provider details"
    url = "add-provider/lsp-details"


class ChambersDetailsForm(BaseForm):
    title = "Chambers details"
    url = "add-provider/chambers-details"


class GovUKTableRadioField(RadioField):
    """A RadioField that generates GovUK table params for template rendering."""

    def __init__(self, label=None, validators=None, structure=None, radio_value_key="id", **kwargs):
        """
        Initialize the field.

        Args:
            label: Field label (will be rendered as page heading in template)
            validators: Field validators
            structure: Table structure definition following your TableStructure format
            radio_value_key: Key to use for radio button values
            **kwargs: Additional field arguments
        """
        super().__init__(label, validators, **kwargs)

        if structure is None:
            raise ValueError("structure parameter is required")

        self.structure = structure
        self.radio_value_key = radio_value_key
        # Use the field type for template detection
        self.type = "GovUKTableRadioField"

    def get_table_params(self, **kwargs):
        """
        Generate GovUK table params for use with your existing Jinja2 macro.

        Usage in template: {{ govukTable(field.get_table_params()) }}

        Args:
            **kwargs: Additional parameters to pass to the table

        Returns:
            dict: GovUK table parameters ready for your macro
        """
        # Convert field choices to DataTable format
        data = []
        for choice_value, choice_data in self.choices:
            if isinstance(choice_data, dict):
                # If choice_data is already a dict, use it directly
                row_data = choice_data.copy()
                row_data[self.radio_value_key] = choice_value
            elif isinstance(choice_data, (list, tuple)):
                # Convert list/tuple to dict using structure IDs
                row_data = {self.radio_value_key: choice_value}
                for i, value in enumerate(choice_data):
                    if i < len(self.structure):
                        structure_id = self.structure[i].get("id", f"col_{i}")
                        row_data[structure_id] = str(value)
            else:
                # Simple string value
                row_data = {self.radio_value_key: choice_value, "label": str(choice_data)}
            data.append(row_data)

        # Create RadioDataTable
        table = RadioDataTable(
            structure=self.structure, data=data, radio_field_name=self.name, radio_value_key=self.radio_value_key
        )

        return table.to_govuk_params(selected_value=self.data, **kwargs)


class ParentProviderForm(BaseForm):
    title = "Assign to parent provider"
    url = "assign-parent-provider"
    template = "add_provider/assign-parent-provider.html"
    success_url = "main.view_provider"

    search = StringField(
        "Search for a parent provider",
        widget=GovTextInput(
            form_group_classes="govuk-!-width-two-thirds",
            heading_class="govuk-fieldset__legend--s",
            classes="provider-search",
            hint="You can search by name or account number",
        ),
        validators=[Length(max=100, message="Search term must be 100 characters or less"), ValidateSearchResults()],
    )

    provider = GovUKTableRadioField(
        "",
        structure=[
            {"text": "Provider", "id": "firmName"},
            {"text": "Account number", "id": "firmNumber"},
            {"text": "Type", "id": "firmType"},
        ],
        choices=[],  # This will be set when the user sends a request.
        radio_value_key="firmId",
        validators=[InputRequired(message="Select a parent provider")],
    )

    def __init__(self, search_term=None, page=1, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get firms data
        pda = current_app.extensions["pda"]
        data = pda.get_all_provider_firms()
        firms = data["firms"]

        # Advocates or Barristers can only have Chambers as their parent
        firms = [firm for firm in firms if firm["firmType"] == "Chambers"]

        # Set search field data
        self.search_term = search_term
        if search_term:
            self.search.data = search_term

        # Filter providers based on search term
        if self.search_term:
            search_lower = self.search_term.lower()
            firms = [
                firm
                for firm in firms
                if (search_lower in firm["firmName"].lower() or search_lower in str(firm["firmId"]).lower())
            ]

        self.page = page
        self.providers_shown_per_page = 7
        self.num_results = len(firms)

        # Limit results and populate choices
        start_id = self.providers_shown_per_page * (self.page - 1)
        end_id = self.providers_shown_per_page * (self.page - 1) + self.providers_shown_per_page

        firms = firms[start_id:end_id]
        choices = []
        for firm in firms:
            choices.append(
                (
                    firm["firmId"],
                    {
                        "firmName": firm["firmName"],
                        "firmNumber": firm["firmNumber"],
                        "firmType": firm["firmType"],
                    },
                )
            )

        self.provider.choices = choices
