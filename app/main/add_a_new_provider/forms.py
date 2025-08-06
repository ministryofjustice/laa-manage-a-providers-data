from flask import current_app
from wtforms import RadioField
from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired, Length
from flask import session

from app.fields import GovUKTableRadioField
from app.validators import ValidateSearchResults
from app.widgets import GovRadioInput, GovTextInput

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

    @property
    def caption(self):
        return session.get("provider_name", default="unknown")

    solicitor_advocate = RadioField(
        "Is the provider a solicitor advocate?",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m", classes="govuk-radios--inline"),
        validators=[InputRequired(message=("Select yes or no"))],
        choices=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
    )

    advocate_level = RadioField(
        "Advocate level",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m"),
        validators=[InputRequired(message=("Select an advocate level"))],
        choices=[
            ("pupil", "Pupil"),
            ("junior", "Junior"),
            ("king's counsel", "King's Counsel (KC, previously QC)"),
        ],
    )

    bar_council_number = StringField(
        "Bar Council roll number",
        widget=GovTextInput(heading_class="govuk-fieldset__legend--m", classes="govuk-!-width-one-half"),
        validators=[
            InputRequired(message="Enter the Bar Council roll number"),
            Length(max=15, message="The Bar Council roll number must be 15 characters or fewer"),
        ],
    )


class ParentProviderForm(BaseForm):
    title = "Assign to parent provider"
    url = "add-provider/assign-parent-provider"
