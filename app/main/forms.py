from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired
from ..forms import BaseForm
from app.widgets import GovRadioInput, GovTextInput
from wtforms import RadioField

class AddProviderForm(BaseForm):
    title = "Add a new provider"
    url = "add-provider"

    next_step_mapping = {
        "advocate": "main.index",
        "barrister": "main.index",
        "chambers": "main.index",
        "legalservicesprovider": "main.index",
    }

    provider_name = StringField(
        'Provider name',
        widget=GovTextInput(heading_class="govuk-fieldset__legend--m"),
        validators=[
            InputRequired(message="Enter the provider name"),
        ],
    )

    provider_type = RadioField(
        'Provider type',
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m"),
        validators=[InputRequired(message=("Select a provider type"))],
        choices=[
            ("advocate", "Advocate"),
            ("barrister", "Barrister"),
            ("chambers", "Chambers"),
            ("lsp", "Legal services provider"),
        ],
    )
