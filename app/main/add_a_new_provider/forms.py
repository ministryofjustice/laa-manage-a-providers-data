from flask import session
from wtforms import RadioField
from wtforms.fields import DateField, SelectField
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired, InputRequired, Optional

from app.validators import ValidateCompaniesHouseNumber, ValidatePastDate
from app.widgets import GovDateInput, GovRadioInput, GovSelect, GovTextInput

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
    title = "Additional details"
    url = "additional-details-legal-services-provider"

    @property
    def caption(self):
        return session.get("provider_name")

    constitutional_status = SelectField(
        "Constitutional status",
        widget=GovSelect(heading_class="govuk-fieldset__legend--m"),
        validators=[InputRequired(message="Select a constitutional status")],
        choices=[
            ("", "Select constitutional status"),
            ("sole practitioner", "Sole Practitioner"),
            ("partnership", "Partnership"),
            ("limited company", "Limited Company"),
            ("limited liability partnership", "Limited Liability Partnership"),
            ("charity (incorporated)", "Charity (Incorporated)"),
            ("charity (unincorporated)", "Charity (Unincorporated)"),
        ],
    )

    indemnity_received_date = DateField(
        "Indemnity received date (optional)",
        widget=GovDateInput(heading_class="govuk-fieldset__legend--m"),
        format="%d %m %Y",
        validators=[Optional(), DataRequired(message="Date must be a real date"), ValidatePastDate()],
    )

    non_profit_organisation = RadioField(
        "Is the provider a not for profit organisation?",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m", classes="govuk-radios--inline"),
        validators=[InputRequired(message="Select yes if the provider is a not for profit organisation")],
        choices=[
            ("Yes", "Yes"),
            ("No", "No"),
        ],
    )

    high_risk_supplier = RadioField(
        "Is the provider a high risk supplier? (optional)",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m", classes="govuk-radios--inline"),
        validators=[Optional()],
        choices=[
            ("Yes", "Yes"),
            ("No", "No"),
        ],
    )

    companies_house_number = StringField(
        "Companies House number",
        widget=GovTextInput(heading_class="govuk-fieldset__legend--m"),
        validators=[InputRequired(message="Enter the Companies House number"), ValidateCompaniesHouseNumber()],
    )


class ChambersDetailsForm(BaseForm):
    title = "Chambers details"
    url = "add-provider/chambers-details"


class ParentProviderForm(BaseForm):
    title = "Assign to parent provider"
    url = "add-provider/assign-parent-provider"
