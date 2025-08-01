from wtforms import RadioField, SubmitField
from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired

from app.widgets import GovRadioInput, GovTextInput

from ...forms import BaseForm


class AddProviderForm(BaseForm):
    title = "Add a new provider"
    url = "add-provider"

    next_step_mapping = {
        "barrister": "main.add_parent_provider",
        "advocate": "main.add_parent_provider",
        "chambers": "main.add_parent_provider",
        "lsp": "main.add_provider/lsp_details",
    }

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


class ParentProviderForm(BaseForm):
    title = "Assign to parent provider"
    url = "add-provider/assign-parent-provider"


class AddParentProviderForm(BaseForm):
    title = "Assign to a parent provider"
    url = "add-parent-provider"

    search_term = StringField(
        "Search for parent provider",
        widget=GovTextInput(
            heading_class="govuk-fieldset__legend--m", hint="You can search by name or account numbe"
        ),
        validators=[
            InputRequired(message="YPlease enter a name or account number"),
        ],
    )

    search_button = SubmitField("Search")
