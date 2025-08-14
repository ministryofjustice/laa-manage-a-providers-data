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
            {"text": "Provider", "id": "firmName"},
            {"text": "Account number", "id": "firmNumber"},
            {"text": "Type", "id": "firmType"},
        ],
        choices=[],  # This will be set when the user sends a request.
        radio_value_key="firmId",
        validators=[InputRequired(message="Select a chambers to assign the new provider to")],
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

class ChambersDetailsForm(BaseForm):
    title = "Chambers details"
    url = "add-provider/chambers-details"

    @property
    def caption(self):
        return session.get("provider_name", default="unknown")

    solicitor_advocate = RadioField(
        "Is the provider a solicitor advocate?",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m", classes="govuk-radios--inline"),
        validators=[InputRequired(message=("Select yes if the provider is a solicitor advocate"))],
        choices=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
    )

    advocate_level = RadioField(
        "Advocate level",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m"),
        validators=[InputRequired(message=("Select the advocate level"))],
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
            Length(max=15, message="The Bar Council roll number must be 15 characters or less"),
        ],
    )


class ParentProviderForm(BaseForm):
    title = "Assign to parent provider"
    url = "add-provider/assign-parent-provider"
