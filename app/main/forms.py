from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired
from ..forms import BaseForm
from ..widgets import PageHeadingInput
from app.widgets import GovRadioInput, GovTextInput
from wtforms import SubmitField, RadioField

class AddProviderForm(BaseForm):
    title = "Add a new provider"
    url = "add-provider"

    next_step_mapping = {
        "advocate": "main.index",
        "chambers": "main.index",
        "legalservicesprovider": "main.index",
    }

    provider_name = StringField(
        'Provider name',
        widget=GovTextInput(),
        validators=[
            InputRequired(message="Enter the provider name"),
        ],
    )

    provider_type = RadioField(
        'Provider type',
        widget=GovRadioInput(hint="Select one option"
        ),
        validators=[InputRequired(message=("Select a provider type"))],
        choices=[
            ("advocate", "Advocate"),
            ("chambers", "Chambers"),
            ("lsp", "Legal services provider"),
        ],
    )
