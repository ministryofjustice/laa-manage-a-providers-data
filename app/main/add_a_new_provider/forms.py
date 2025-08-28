from flask import current_app, session
from wtforms import RadioField
from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired, Length, Optional

from app.constants import ADVOCATE_LEVEL_CHOICES, CONSTITUTIONAL_STATUS_CHOICES, FIRM_TYPE_CHOICES, YES_NO_CHOICES, \
    PARENT_FIRM_TYPE_CHOICES
from app.fields import GovUKTableRadioField
from app.validators import ValidateCompaniesHouseNumber, ValidateGovDateField, ValidatePastDate, ValidateSearchResults
from app.widgets import GovDateInput, GovRadioInput, GovTextInput

from ...fields import GovDateField
from ...forms import BaseForm


class AddProviderForm(BaseForm):
    title = "Add a parent provider"
    url = "add-provider"

    provider_name = StringField(
        "Provider name",
        widget=GovTextInput(
            heading_class="govuk-fieldset__legend--m",
            hint="Do not include the provider type or address in the name"
        ),
        validators=[
            InputRequired(message="Enter the provider name"),
        ],
    )

    provider_type = RadioField(
        "Provider type",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m"),
        validators=[InputRequired(message=("Select a provider type"))],
        choices=PARENT_FIRM_TYPE_CHOICES,
    )


class LspDetailsForm(BaseForm):
    title = "Legal services provider details"
    url = "additional-details-legal-services-provider"
    submit_button_text = "Submit"

    @property
    def caption(self):
        return session.get("new_provider", {}).get("firm_name", "Unknown")

    constitutional_status = RadioField(
        "Constitutional status",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m"),
        validators=[InputRequired(message="Select the constitutional status")],
        choices=CONSTITUTIONAL_STATUS_CHOICES,
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
        validators=[ValidateCompaniesHouseNumber()],
    )


class AdvocateDetailsForm(BaseForm):
    title = "Advocate details"
    url = "advocate-details"

    @property
    def caption(self):
        return session.get("new_provider", {}).get("firm_name", "Unknown")

    solicitor_advocate = RadioField(
        "Is the provider a solicitor advocate? (optional)",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m", classes="govuk-radios--inline"),
        choices=YES_NO_CHOICES,
        validators=[Optional()],
    )

    advocate_level = RadioField(
        "Advocate level",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m"),
        validators=[InputRequired(message="Select the advocate level")],
        choices=ADVOCATE_LEVEL_CHOICES,
    )

    bar_council_roll_number = StringField(
        "Bar Council roll number",
        widget=GovTextInput(
            heading_class="govuk-fieldset__legend--m",
            classes="govuk-!-width-one-half",
        ),
        validators=[
            InputRequired("Enter the Bar Council roll number"),
            Length(max=15, message="Bar Council roll number must be 15 characters or less"),
        ],
    )


class AssignChambersForm(BaseForm):
    title = "Assign to a chambers"
    url = "assign-chambers"
    template = "add_provider/assign-chambers.html"
    success_url = "main.providers"

    search = StringField(
        "Search for a chambers",
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
            {"text": "Provider", "id": "firm_name"},
            {"text": "Account number", "id": "firm_number"},
            {"text": "Type", "id": "firm_type"},
        ],
        choices=[],  # This will be set when the user sends a request.
        radio_value_key="firm_id",
        validators=[InputRequired(message="Select a chambers to assign the new provider to")],
    )

    def __init__(self, search_term=None, page=1, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get firms data
        pda = current_app.extensions["pda"]
        firms = pda.get_all_provider_firms()

        # Advocates or Barristers can only have Chambers as their parent
        firms = [firm for firm in firms if firm.firm_type == "Chambers"]

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
                if (search_lower in firm.firm_name.lower() or search_lower in str(firm.firm_id).lower())
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
                    firm.firm_id,
                    {
                        "firm_name": firm.firm_name,
                        "firm_number": firm.firm_number,
                        "firm_type": firm.firm_type,
                    },
                )
            )

        self.provider.choices = choices


class ChambersDetailsForm(BaseForm):
    title = "Chambers details"
    url = "chambers-details"

    @property
    def caption(self):
        return session.get("new_provider", {}).get("firm_name", "unknown")

    solicitor_advocate = RadioField(
        "Is the provider a solicitor advocate?",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m", classes="govuk-radios--inline"),
        validators=[InputRequired(message=("Select yes if the provider is a solicitor advocate"))],
        choices=YES_NO_CHOICES,
    )

    advocate_level = RadioField(
        "Advocate level",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m"),
        validators=[InputRequired(message=("Select the advocate level"))],
        choices=ADVOCATE_LEVEL_CHOICES,
    )

    bar_council_number = StringField(
        "Bar Council roll number",
        widget=GovTextInput(heading_class="govuk-fieldset__legend--m", classes="govuk-!-width-one-half"),
        validators=[
            InputRequired(message="Enter the Bar Council roll number"),
            Length(max=15, message="Bar Council roll number must be 15 characters or less"),
        ],
    )
