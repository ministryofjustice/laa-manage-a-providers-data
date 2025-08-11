from flask import session
from wtforms import RadioField
from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired, Optional

from app.validators import ValidateCompaniesHouseNumber, ValidateGovDateField, ValidatePastDate
from app.widgets import GovDateInput, GovRadioInput, GovTextInput

from ...fields import GovDateField
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
    url = "additional-details-legal-services-provider"

    @property
    def caption(self):
        return session.get("provider_name")

    constitutional_status = RadioField(
        "Constitutional status",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m"),
        validators=[InputRequired(message="Select a constitutional status")],
        choices=[
            ("government funded organisation", "Government funded organisation"),
            ("sole practitioner", "Sole practitioner"),
            ("charity", "Charity"),
            ("partnership", "Partnership"),
            ("llp", "LLP"),
            ("limited company", "Limited company"),
        ],
    )

    indemnity_received_date = GovDateField(
        "Indemnity received date (optional)",
        widget=GovDateInput(heading_class="govuk-fieldset__legend--m", hint="For example 27 3 2025"),
        format="%d %m %Y",
        validators=[Optional(), ValidateGovDateField(), ValidatePastDate()],
    )

    companies_house_number = StringField(
        "Companies House number (optional)",
        widget=GovTextInput(
            heading_class="govuk-fieldset__legend--m",
            classes="govuk-!-width-one-half",
            hint="Also known as Company Registration Number",
        ),
        validators=[Optional(), ValidateCompaniesHouseNumber()],
    )


class ChambersDetailsForm(BaseForm):
    title = "Chambers details"
    url = "add-provider/chambers-details"


class ParentProviderForm(BaseForm):
    title = "Assign to parent provider"
    url = "add-provider/assign-parent-provider"
